from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class AllocationPayload(BaseModel):
    district: str
    sanctioned_asi: int
    sanctioned_chc: int
    sanctioned_cpc: int

@router.post("/solve")
def run_allocation_solver(payload: AllocationPayload) -> Dict[str, Any]:
    return {
        "status": "success",
        "district": payload.district,
        "solved_allocation": [
            {"beat_name": "Beat Alpha", "asi_allocated": 1, "chc_allocated": 2, "cpc_allocated": 5, "normalized_severity": 0.95},
            {"beat_name": "Beat Beta", "asi_allocated": 0, "chc_allocated": 1, "cpc_allocated": 3, "normalized_severity": 0.60}
        ]
    }

@router.get("/resource-allocation")
def get_resource_allocations_history() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "district": "Bengaluru Urban",
            "allocated_asi": 12,
            "allocated_chc": 30,
            "allocated_cpc": 75,
            "created_at": "2026-06-08T11:00:00"
        }
    ]
