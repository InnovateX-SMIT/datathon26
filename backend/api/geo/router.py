from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/hotspots")
def get_hotspots() -> List[Dict[str, Any]]:
    return [
        {"id": 1, "latitude": 12.9716, "longitude": 77.5946, "severity": "high", "district": "Bengaluru Urban"},
        {"id": 2, "latitude": 12.9141, "longitude": 77.6413, "severity": "medium", "district": "Bengaluru Urban"}
    ]

@router.get("/district-map")
def get_district_map() -> Dict[str, Any]:
    return {
        "district": "Bengaluru Urban",
        "boundary_type": "geojson_stub",
        "features": []
    }
