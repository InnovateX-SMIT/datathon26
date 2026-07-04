from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.schemas.network import (
    NetworkGraphResponse,
    CentralityResponse,
    ClusterResponse,
    AssociationResponse,
    LocationNetworkResponse,
    LinkAnalysisResponse
)
from backend.services.network_service import NetworkService
from backend.services.network_analytics_service import NetworkAnalyticsService

router = APIRouter()

@router.get("/graph")
def get_network_graph_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns summary statistics of the criminal intelligence network graph."""
    try:
        service = NetworkAnalyticsService(db)
        G = service.get_graph()
        node_types = {}
        for _, attr in G.nodes(data=True):
            t = attr.get("type", "unknown")
            node_types[t] = node_types.get(t, 0) + 1
        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "node_type_breakdown": node_types
        }
    except Exception as e:
        logger.error(f"Error in get_network_graph_summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while retrieving network graph summary"
        )

@router.get("/centrality", response_model=CentralityResponse)
def get_network_centrality(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkAnalyticsService(db)
        return service.get_centrality()
    except Exception as e:
        logger.error(f"Error in get_network_centrality: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while computing network centrality"
        )

@router.get("/clusters", response_model=List[ClusterResponse])
def get_network_clusters(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkAnalyticsService(db)
        return service.get_clusters()
    except Exception as e:
        logger.error(f"Error in get_network_clusters: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while detecting network clusters"
        )

@router.get("/associations", response_model=List[AssociationResponse])
def get_network_associations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkAnalyticsService(db)
        return service.get_repeat_associations()
    except Exception as e:
        logger.error(f"Error in get_network_associations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while computing network associations"
        )

@router.get("/location-intelligence", response_model=LocationNetworkResponse)
def get_location_intelligence(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkAnalyticsService(db)
        return service.get_location_intelligence()
    except Exception as e:
        logger.error(f"Error in get_location_intelligence: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while computing location network intelligence"
        )

@router.get("/link-analysis", response_model=LinkAnalysisResponse)
def get_link_analysis(
    source_id: str = Query(..., description="Source node ID (e.g. criminal_1)"),
    target_id: str = Query(..., description="Target node ID (e.g. location_5)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    try:
        service = NetworkAnalyticsService(db)
        return service.find_shortest_path(source_id, target_id)
    except Exception as e:
        logger.error(f"Error in get_link_analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while performing shortest path link analysis"
        )

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

