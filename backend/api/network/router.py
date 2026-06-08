from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/graph")
def get_network_graph() -> Dict[str, Any]:
    return {
        "nodes": [
            {"id": "c_1", "label": "Criminal A", "type": "criminal", "risk": 0.8},
            {"id": "c_2", "label": "Criminal B", "type": "criminal", "risk": 0.5},
            {"id": "e_1", "label": "FIR 0042/2026", "type": "event", "severity": 2.0}
        ],
        "edges": [
            {"source": "c_1", "target": "e_1", "role": "accused"},
            {"source": "c_2", "target": "e_1", "role": "accomplice"}
        ]
    }

@router.get("/centrality")
def get_network_centrality() -> Dict[str, Any]:
    return {
        "c_1": 0.85,
        "c_2": 0.45
    }
