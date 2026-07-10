from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Any

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.models.user import User, UserRole

from backend.schemas.report import (
    ReportResponse,
    ReportSummaryResponse,
    GenerateReportRequest,
    ReportTypeResponse,
    ReportTypeInfo
)
from backend.services.report_service import ReportService

router = APIRouter()

def check_executive_clearance(user: User):
    if user.role not in [UserRole.ADMIN, UserRole.SUPERINTENDENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Superintendents and Admins only."
        )

@router.get("/types", response_model=ReportTypeResponse)
def get_report_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportTypeResponse:
    """
    Returns a list of all supported executive report types.
    """
    check_executive_clearance(current_user)
    try:
        service = ReportService(db)
        types_list = service.get_supported_types()
        return ReportTypeResponse(types=[ReportTypeInfo(**t) for t in types_list])
    except Exception as e:
        logger.error(f"Error in get_report_types: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report types."
        )

@router.get("/", response_model=List[ReportSummaryResponse])
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportSummaryResponse]:
    """
    Returns the list of all historical generated reports.
    """
    check_executive_clearance(current_user)
    try:
        service = ReportService(db)
        reports = service.retrieve_generated_reports()
        
        # Map database objects to summaries
        response = []
        for r in reports:
            response.append(ReportSummaryResponse(
                id=r.id,
                report_id=r.id,
                title=r.title,
                report_type=r.report_type,
                generated_at=r.generated_at,
                executive_summary=r.summary
            ))
        return response
    except Exception as e:
        logger.error(f"Error in get_reports: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report list."
        )

@router.get("/{report_id}", response_model=ReportResponse)
def get_report_by_id(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """
    Retrieves detailed structured data for a single executive report.
    """
    check_executive_clearance(current_user)
    try:
        service = ReportService(db)
        report_data = service.get_report_by_id(report_id)
        if not report_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found."
            )
        return ReportResponse(**report_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in get_report_by_id: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report details."
        )

@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    payload: GenerateReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """
    Generates a new executive report from aggregated analytics data and saves its metadata.
    """
    check_executive_clearance(current_user)
    try:
        service = ReportService(db)
        report_data = service.trigger_report_generation(
            title=payload.title,
            report_type=payload.report_type
        )
        
        from backend.repositories.admin_repository import AdminRepository
        admin_repo = AdminRepository(db)
        admin_repo.create_audit_log(
            user_id=current_user.id if current_user and not isinstance(current_user, dict) else (current_user.get("id") if isinstance(current_user, dict) else None),
            action="REPORT_GENERATED",
            entity_type="report",
            entity_id=report_data.get("report_id"),
            details=f"Generated {payload.report_type} report '{payload.title}'"
        )
        
        return ReportResponse(**report_data)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error in generate_report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate executive report."
        )

@router.get("/{report_id}/download")
def download_report_csv(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generates and downloads a CSV export file of the executive report.
    """
    import io
    import csv
    check_executive_clearance(current_user)
    try:
        service = ReportService(db)
        report_data = service.get_report_by_id(report_id)
        if not report_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found."
            )
        # Audit log the download
        from backend.repositories.admin_repository import AdminRepository
        admin_repo = AdminRepository(db)
        admin_repo.create_audit_log(
            user_id=current_user.id if current_user and not isinstance(current_user, dict) else (current_user.get("id") if isinstance(current_user, dict) else None),
            action="REPORT_DOWNLOADED",
            entity_type="report",
            entity_id=report_id,
            details=f"Downloaded CSV export for report ID {report_id}"
        )
            
        # Compile CSV in-memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header info
        writer.writerow(["EXECUTIVE BRIEFING DOSSIER"])
        writer.writerow([f"Dossier ID: INTEL-{report_data['report_id']}"])
        writer.writerow([f"Title: {report_data['title']}"])
        writer.writerow([f"Report Type: {report_data['report_type']}"])
        writer.writerow([f"Generated At: {report_data['generated_at']}"])
        writer.writerow([])
        
        # Summary
        writer.writerow(["EXECUTIVE SUMMARY NARRATIVE"])
        writer.writerow([report_data["executive_summary"]])
        writer.writerow([])
        
        # Section 1: Crime Overview
        overview = report_data["crime_overview"]
        writer.writerow(["SECTION I: CRIME ANALYTICS OVERVIEW"])
        writer.writerow([f"Total Crimes: {overview['total_crimes']}"])
        writer.writerow([f"Trend Direction: {overview['trend_direction']}"])
        writer.writerow([])
        writer.writerow(["Top Crime Categories"])
        writer.writerow(["Category", "Count"])
        for cat in overview.get("top_categories", []):
            writer.writerow([cat.get("category"), cat.get("count")])
        writer.writerow([])
        
        # Section 2: Predictive Insights
        preds = report_data["predictive_insights"]
        writer.writerow(["SECTION II: PREDICTIVE RISK AND SPOT FORECASTS"])
        writer.writerow([f"Hotspot Count: {preds['hotspot_count']}"])
        rss = preds.get("risk_score_summary", {})
        writer.writerow([f"Average Criminal Risk: {rss.get('average_criminal_risk')}"])
        writer.writerow([f"High-Risk Criminals Count: {rss.get('high_risk_criminals_count')}"])
        writer.writerow([f"Total Criminals Tracked: {rss.get('total_criminals_tracked')}"])
        writer.writerow([])
        writer.writerow(["High-Risk Locations"])
        writer.writerow(["District", "Crime Count", "Risk Level"])
        for loc in preds.get("high_risk_locations", []):
            writer.writerow([loc.get("district"), loc.get("crime_count"), loc.get("risk_level")])
        writer.writerow([])
        
        # Section 3: Network Insights
        networks = report_data["network_insights"]
        writer.writerow(["SECTION III: CRIMINAL CO-OFFENDING NETWORK INTELLIGENCE"])
        writer.writerow([f"Total Networks: {networks['total_networks']}"])
        writer.writerow([f"Largest Network Size: {networks['largest_network_size']}"])
        writer.writerow([])
        writer.writerow(["Key Network Influencers"])
        writer.writerow(["Node ID", "Type", "Label", "Centrality Score"])
        for entity in networks.get("key_entities", []):
            writer.writerow([entity.get("id"), entity.get("type"), entity.get("label"), entity.get("score")])
        writer.writerow([])
        
        # Section 4: Recommendations
        writer.writerow(["SECTION IV: STRATEGIC OPERATIONAL RECOMMENDATIONS"])
        writer.writerow(["ID", "Priority", "Recommendation Text", "Reason", "Status"])
        for rec in report_data.get("recommendations", []):
            writer.writerow([rec.get("id"), rec.get("priority"), rec.get("recommendation_text"), rec.get("reason"), rec.get("status")])
        writer.writerow([])
        
        # Section 5: Alerts
        writer.writerow(["SECTION V: SYSTEM & PATROL ESCALATIONS"])
        writer.writerow(["ID", "Severity", "Source", "Title", "Description", "Status"])
        for alt in report_data.get("alerts", []):
            writer.writerow([alt.get("id"), alt.get("severity"), alt.get("source"), alt.get("title"), alt.get("description"), alt.get("status")])
            
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=dossier_intel_{report_id}.csv"}
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in download_report_csv: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export CSV dossier."
        )

@router.post("/{report_id}/share")
def share_report(
    report_id: int,
    shared_with_email: str = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Simulates sharing an executive report with another user/agency.
    """
    check_executive_clearance(current_user)
    try:
        service = ReportService(db)
        report_data = service.get_report_by_id(report_id)
        if not report_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found."
            )
        
        # Audit Log Sharing
        try:
            user_id = getattr(current_user, "id", None)
            from backend.repositories.admin_repository import AdminRepository
            admin_repo = AdminRepository(db)
            admin_repo.create_audit_log(
                user_id=user_id,
                action="REPORT_SHARED",
                entity_type="report",
                entity_id=report_id,
                details=f"Shared report ID {report_id} with email {shared_with_email}"
            )
        except Exception as ae:
            logger.error(f"Failed to log report sharing audit: {ae}")
            
        return {"success": True, "message": f"Report shared with {shared_with_email} successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in share_report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to share executive report."
        )
