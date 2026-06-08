from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
def get_crimes() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "crime_type": "Theft",
            "crime_category": "Property Crime",
            "description": "Store burglary at Whitefield",
            "severity": 1.2,
            "status": "investigating",
            "crime_date": "2026-06-01",
            "victim_count": 1,
            "accused_count": 2
        }
    ]

@router.get("/{id}")
def get_crime_by_id(id: int) -> Dict[str, Any]:
    return {
        "id": id,
        "crime_type": "Theft",
        "crime_category": "Property Crime",
        "description": "Store burglary at Whitefield",
        "severity": 1.2,
        "status": "investigating",
        "crime_date": "2026-06-01",
        "victim_count": 1,
        "accused_count": 2
    }
