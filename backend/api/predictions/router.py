"""
backend/api/predictions/router.py
-----------------------------------
FastAPI Router for Phase 5 AI/ML Predictive Intelligence Endpoints.
Serves:
1. Crime Risk Prediction
2. Future Hotspot Prediction
3. Repeat Offender Recidivism Risk Prediction
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.api.deps import get_session_id
from backend.services.prediction_service import PredictionService

router = APIRouter()


# --- Request Schemas ---

class CrimeRiskRequest(BaseModel):
    case_master_id: int = Field(default=1, description="Case Master ID")
    district_id: int = Field(default=1, description="District ID")
    police_station_id: int = Field(default=1, description="Police Station Unit ID")
    crime_major_head_id: int = Field(default=2, description="Crime Major Head ID")
    crime_minor_head_id: int = Field(default=6, description="Crime Minor Head ID")
    gravity_offence_id: int = Field(default=2, description="Gravity Offence Class (1=Non-Grave, 2=Grave)")
    latitude: float = Field(default=12.9716, description="Incident Latitude")
    longitude: float = Field(default=77.5946, description="Incident Longitude")
    hour_of_day: int = Field(default=22, ge=0, le=23, description="Incident hour of day (0-23)")
    day_of_week: int = Field(default=5, ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")
    month: int = Field(default=8, ge=1, le=12, description="Incident Month (1-12)")
    is_weekend: int = Field(default=1, ge=0, le=1, description="Weekend flag")
    is_night_time: int = Field(default=1, ge=0, le=1, description="Night window flag (1=22:00-06:00, 0=Other)")
    hist_station_crime_count_30d: int = Field(default=500, description="Station 30-day incident volume")
    hist_district_crime_count_30d: int = Field(default=800, description="District 30-day incident volume")


class HotspotPredictionRequest(BaseModel):
    grid_lat: float = Field(default=13.0, description="Sector Grid Latitude")
    grid_lon: float = Field(default=76.1, description="Sector Grid Longitude")
    district_id: int = Field(default=9, description="District ID")
    police_station_id: int = Field(default=10, description="Police Station Unit ID")
    prior_7d_crime_count: int = Field(default=0, description="Prior 7-day crime count")
    prior_30d_crime_count: int = Field(default=0, description="Prior 30-day crime count")
    prior_90d_crime_count: int = Field(default=1, description="Prior 90-day crime count")
    prior_180d_crime_count: int = Field(default=5, description="Prior 180-day crime count")
    spatial_density_ratio: float = Field(default=0.0, description="Spatial density ratio")
    peak_hour_window_id: int = Field(default=0, description="Peak hour window ID (0=NIGHT, 1=MORNING, 2=AFTERNOON, 3=EVENING)")


class OffenderRecidivismRequest(BaseModel):
    age_years: int = Field(default=25, ge=1, le=120)
    gender_id: int = Field(default=1, ge=1, le=3)
    district_id: int = Field(default=11, ge=1)
    police_station_id: int = Field(default=17, ge=1)
    initial_gravity_offence_id: int = Field(default=2, ge=1, le=2)
    initial_crime_major_head_id: int = Field(default=2, ge=1)
    initial_crime_minor_head_id: int = Field(default=12, ge=1)
    initial_hour_of_day: int = Field(default=19, ge=0, le=23)
    initial_day_of_week: int = Field(default=6, ge=0, le=6)
    initial_month: int = Field(default=12, ge=1, le=12)
    initial_is_weekend: int = Field(default=1, ge=0, le=1)
    initial_is_night_time: int = Field(default=0, ge=0, le=1)
    initial_co_offender_count: int = Field(default=3, ge=1)


# --- Endpoint Routes ---

@router.api_route("/crime-risk", methods=["GET", "POST"])
def predict_crime_risk(
    req: Optional[CrimeRiskRequest] = None,
    case_master_id: int = Query(1),
    district_id: int = Query(1),
    police_station_id: int = Query(1),
    crime_major_head_id: int = Query(2),
    crime_minor_head_id: int = Query(6),
    gravity_offence_id: int = Query(2),
    latitude: float = Query(12.9716),
    longitude: float = Query(77.5946),
    hour_of_day: int = Query(22),
    day_of_week: int = Query(5),
    month: int = Query(8),
    is_weekend: int = Query(1),
    is_night_time: int = Query(1),
    hist_station_crime_count_30d: int = Query(500),
    hist_district_crime_count_30d: int = Query(800),
    session_id: str = Depends(get_session_id)
):
    """
    Predict Crime Risk Score & Risk Tier (0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL) via Zoho Catalyst QuickML POST Endpoint.
    """
    try:
        service = PredictionService()
        if req:
            cm_id = req.case_master_id
            d_id = req.district_id
            ps_id = req.police_station_id
            cmaj = req.crime_major_head_id
            cmin = req.crime_minor_head_id
            grav = req.gravity_offence_id
            lat = req.latitude
            lon = req.longitude
            hr = req.hour_of_day
            dow = req.day_of_week
            mth = req.month
            wknd = req.is_weekend
            night = req.is_night_time
            st_30d = req.hist_station_crime_count_30d
            dt_30d = req.hist_district_crime_count_30d
        else:
            cm_id = case_master_id
            d_id = district_id
            ps_id = police_station_id
            cmaj = crime_major_head_id
            cmin = crime_minor_head_id
            grav = gravity_offence_id
            lat = latitude
            lon = longitude
            hr = hour_of_day
            dow = day_of_week
            mth = month
            wknd = is_weekend
            night = is_night_time
            st_30d = hist_station_crime_count_30d
            dt_30d = hist_district_crime_count_30d

        return service.predict_crime_risk(
            case_master_id=cm_id,
            district_id=d_id,
            police_station_id=ps_id,
            crime_major_head_id=cmaj,
            crime_minor_head_id=cmin,
            gravity_offence_id=grav,
            latitude=lat,
            longitude=lon,
            hour_of_day=hr,
            day_of_week=dow,
            month=mth,
            is_weekend=wknd,
            is_night_time=night,
            hist_station_crime_count_30d=st_30d,
            hist_district_crime_count_30d=dt_30d
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crime risk prediction failed: {str(e)}")


@router.api_route("/hotspots", methods=["GET", "POST"])
def predict_future_hotspots(
    req: Optional[HotspotPredictionRequest] = None,
    grid_lat: float = Query(13.0),
    grid_lon: float = Query(76.1),
    district_id: int = Query(9),
    police_station_id: int = Query(10),
    prior_7d_crime_count: int = Query(0),
    prior_30d_crime_count: int = Query(0),
    prior_90d_crime_count: int = Query(1),
    prior_180d_crime_count: int = Query(5),
    spatial_density_ratio: float = Query(0.0),
    peak_hour_window_id: int = Query(0),
    session_id: str = Depends(get_session_id)
):
    """
    Predict Future High-Risk Hotspot Sector Clusters (0=NON_HOTSPOT, 1=FUTURE_HOTSPOT) via QuickML Pipeline 2.
    """
    try:
        service = PredictionService()
        if req:
            lat = req.grid_lat
            lon = req.grid_lon
            d_id = req.district_id
            ps_id = req.police_station_id
            p7 = req.prior_7d_crime_count
            p30 = req.prior_30d_crime_count
            p90 = req.prior_90d_crime_count
            p180 = req.prior_180d_crime_count
            density = req.spatial_density_ratio
            peak = req.peak_hour_window_id
        else:
            lat = grid_lat
            lon = grid_lon
            d_id = district_id
            ps_id = police_station_id
            p7 = prior_7d_crime_count
            p30 = prior_30d_crime_count
            p90 = prior_90d_crime_count
            p180 = prior_180d_crime_count
            density = spatial_density_ratio
            peak = peak_hour_window_id

        return service.predict_future_hotspots(
            grid_lat=lat,
            grid_lon=lon,
            district_id=d_id,
            police_station_id=ps_id,
            prior_7d_crime_count=p7,
            prior_30d_crime_count=p30,
            prior_90d_crime_count=p90,
            prior_180d_crime_count=p180,
            spatial_density_ratio=density,
            peak_hour_window_id=peak
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotspot prediction failed: {str(e)}")


@router.api_route("/recidivism", methods=["GET", "POST"])
def predict_recidivism(
    req: Optional[OffenderRecidivismRequest] = None,
    age_years: int = Query(25),
    gender_id: int = Query(1),
    district_id: int = Query(11),
    police_station_id: int = Query(17),
    initial_gravity_offence_id: int = Query(2),
    initial_crime_major_head_id: int = Query(2),
    initial_crime_minor_head_id: int = Query(12),
    initial_hour_of_day: int = Query(19),
    initial_day_of_week: int = Query(6),
    initial_month: int = Query(12),
    initial_is_weekend: int = Query(1),
    initial_is_night_time: int = Query(0),
    initial_co_offender_count: int = Query(3),
    session_id: str = Depends(get_session_id)
):
    """
    Predict Repeat Offender Recidivism Risk (0=NON_RECIDIVIST, 1=REPEAT_OFFENDER) via QuickML Pipeline 3 Endpoint.
    """
    try:
        service = PredictionService()
        if req:
            age = req.age_years
            gid = req.gender_id
            did = req.district_id
            psid = req.police_station_id
            grav = req.initial_gravity_offence_id
            cmaj = req.initial_crime_major_head_id
            cmin = req.initial_crime_minor_head_id
            hr = req.initial_hour_of_day
            dow = req.initial_day_of_week
            mth = req.initial_month
            wknd = req.initial_is_weekend
            night = req.initial_is_night_time
            co_off = req.initial_co_offender_count
        else:
            age = age_years
            gid = gender_id
            did = district_id
            psid = police_station_id
            grav = initial_gravity_offence_id
            cmaj = initial_crime_major_head_id
            cmin = initial_crime_minor_head_id
            hr = initial_hour_of_day
            dow = initial_day_of_week
            mth = initial_month
            wknd = initial_is_weekend
            night = initial_is_night_time
            co_off = initial_co_offender_count

        return service.predict_recidivism(
            age_years=age,
            gender_id=gid,
            district_id=did,
            police_station_id=psid,
            initial_gravity_offence_id=grav,
            initial_crime_major_head_id=cmaj,
            initial_crime_minor_head_id=cmin,
            initial_hour_of_day=hr,
            initial_day_of_week=dow,
            initial_month=mth,
            initial_is_weekend=wknd,
            initial_is_night_time=night,
            initial_co_offender_count=co_off
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recidivism prediction failed: {str(e)}")

