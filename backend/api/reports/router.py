from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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
