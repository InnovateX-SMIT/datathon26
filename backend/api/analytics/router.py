from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/trends")
def get_trends() -> List[Dict[str, Any]]:
    return [
        {"date": "2026-06-01", "crime_count": 12},
        {"date": "2026-06-02", "crime_count": 15},
        {"date": "2026-06-03", "crime_count": 9}
    ]

@router.get("/categories")
def get_categories() -> List[Dict[str, Any]]:
    return [
        {"category": "Property Crime", "count": 230},
        {"category": "Violent Crime", "count": 120},
        {"category": "Cyber Crime", "count": 45}
    ]
