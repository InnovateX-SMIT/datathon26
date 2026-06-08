from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
def get_alerts() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "crime_event_id": 42,
            "alert_type": "Anomaly Detection",
            "severity": "high",
            "message": "Spike in theft crimes observed in Beat Alpha",
            "status": "unread",
            "created_at": "2026-06-08T14:30:00"
        }
    ]

@router.put("/{id}/read")
def mark_alert_read(id: int) -> Dict[str, Any]:
    return {"id": id, "status": "read", "message": "Alert marked as read"}
