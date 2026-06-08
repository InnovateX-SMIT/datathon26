from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class ReportRequest(BaseModel):
    title: str
    report_type: str
    summary_params: Dict[str, Any]

@router.get("/")
def get_reports() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "title": "Monthly Crime Analytics Report - May 2026",
            "report_type": "PDF",
            "generated_at": "2026-06-01T00:00:00"
        }
    ]

@router.post("/generate")
def generate_report(payload: ReportRequest) -> Dict[str, Any]:
    return {
        "id": 99,
        "title": payload.title,
        "report_type": payload.report_type,
        "status": "generated",
        "download_url": "/api/v1/reports/download/99"
    }
