from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.schemas.network import NetworkGraphResponse
from backend.services.network_service import NetworkService

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

@router.get("/criminal/{criminal_id}", response_model=NetworkGraphResponse)
def get_criminal_network(
    criminal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkService(db)
        network = service.build_criminal_network(criminal_id)
        if not network:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Criminal network for ID {criminal_id} not found"
            )
        return network
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_criminal_network: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred while building criminal network"
        )

@router.get("/crime/{crime_id}", response_model=NetworkGraphResponse)
def get_crime_network(
    crime_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkService(db)
        network = service.build_crime_network(crime_id)
        if not network:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crime network for ID {crime_id} not found"
            )
        return network
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_crime_network: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred while building crime network"
        )

@router.get("/location/{location_id}", response_model=NetworkGraphResponse)
def get_location_network(
    location_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkService(db)
        network = service.build_location_network(location_id)
        if not network:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location network for ID {location_id} not found"
            )
        return network
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_location_network: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred while building location network"
        )

