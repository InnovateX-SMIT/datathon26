from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
<<<<<<< Updated upstream
from backend.schemas.geo import DistrictCrime, StationCrime, HeatmapPoint, HotspotCluster, GeoIntelligenceResponse
=======
from backend.api.deps import get_session_id
from backend.schemas.geo import (
    DistrictCrime,
    StationCrime,
    HeatmapPoint,
    HotspotCluster,
    GeoIntelligenceResponse,
    TimeOfDayResponse,
)
>>>>>>> Stashed changes
from backend.services.geo_service import GeoService

router = APIRouter()

def parse_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: '{date_str}'. Use YYYY-MM-DD format."
        )


@router.get("/intelligence", response_model=GeoIntelligenceResponse)
def get_geo_intelligence(
    district: Optional[str] = Query(None, description="Filter by district name"),
    police_station: Optional[str] = Query(None, description="Filter by police station name"),
    crime_type: Optional[str] = Query(None, description="Filter by crime category/type"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)
        service = GeoService(db)
        return service.get_geo_intelligence(
            district=district,
            police_station=police_station,
            crime_type=crime_type,
            start_date=parsed_start,
            end_date=parsed_end
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching geo intelligence summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unable to load geospatial intelligence data")

@router.get("/districts", response_model=List[DistrictCrime])
def get_districts(
    district: Optional[str] = Query(None, description="Filter by district name"),
    police_station: Optional[str] = Query(None, description="Filter by police station name"),
    crime_type: Optional[str] = Query(None, description="Filter by crime category/type"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)
        service = GeoService(db)
        return service.get_district_crime_distribution(
            district=district,
            police_station=police_station,
            crime_type=crime_type,
            start_date=parsed_start,
            end_date=parsed_end
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching district crime distribution: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stations", response_model=List[StationCrime])
def get_stations(
    district: Optional[str] = Query(None, description="Filter by district name"),
    police_station: Optional[str] = Query(None, description="Filter by police station name"),
    crime_type: Optional[str] = Query(None, description="Filter by crime category/type"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)
        service = GeoService(db)
        return service.get_station_crime_distribution(
            district=district,
            police_station=police_station,
            crime_type=crime_type,
            start_date=parsed_start,
            end_date=parsed_end
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching station crime distribution: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/heatmap", response_model=List[HeatmapPoint])
def get_heatmap(
    district: Optional[str] = Query(None, description="Filter by district name"),
    police_station: Optional[str] = Query(None, description="Filter by police station name"),
    crime_type: Optional[str] = Query(None, description="Filter by crime category/type"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)
        service = GeoService(db)
        return service.get_heatmap_points(
            district=district,
            police_station=police_station,
            crime_type=crime_type,
            start_date=parsed_start,
            end_date=parsed_end
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching heatmap points: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/hotspots", response_model=List[HotspotCluster])
def get_hotspots(
    district: Optional[str] = Query(None, description="Filter by district name"),
    police_station: Optional[str] = Query(None, description="Filter by police station name"),
    crime_type: Optional[str] = Query(None, description="Filter by crime category/type"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
<<<<<<< Updated upstream
=======
    min_crime_count: Optional[int] = Query(None, ge=1, description="Minimum crime count per hotspot cluster (controls DBSCAN min_samples sensitivity)"),
>>>>>>> Stashed changes
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)
        service = GeoService(db)
        return service.get_hotspot_clusters(
            district=district,
            police_station=police_station,
            crime_type=crime_type,
            start_date=parsed_start,
            end_date=parsed_end
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching hotspot clusters: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/time-of-day", response_model=TimeOfDayResponse)
def get_time_of_day_analysis(
    district: Optional[str] = Query(None, description="Filter by district name"),
    police_station: Optional[str] = Query(None, description="Filter by police station name"),
    crime_type: Optional[str] = Query(None, description="Filter by crime category/type"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)
        service = GeoService(db, session_id=session_id)
        return service.get_time_of_day_distribution(
            district=district,
            police_station=police_station,
            crime_type=crime_type,
            start_date=parsed_start,
            end_date=parsed_end
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching time-of-day analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unable to load time-of-day analysis")

@router.get("/boundary-geojson")
def get_karnataka_boundary_geojson(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    current_user = Depends(get_current_user)
):
    try:
        service = GeoService(db, session_id=session_id)
        return service.get_district_boundary()
    except Exception as e:
        logger.error(f"Error fetching Karnataka boundary GeoJSON: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unable to load Karnataka boundary")

@router.get("/lookup-options")
def get_lookup_options(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = GeoService(db)
        return service.get_lookup_options()
    except Exception as e:
        logger.error(f"Error fetching geo lookup options: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unable to load lookup filters")
