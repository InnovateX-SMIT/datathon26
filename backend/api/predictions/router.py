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


class OffenderRecidivismRequest(BaseModel):
    accused_id: int = Field(..., description="Accused Master ID")
    age_years: int = Field(default=35, ge=1, le=120)
    prior_case_count: int = Field(default=2, ge=0)
    arrest_count: int = Field(default=1, ge=0)
    grave_offence_ratio: float = Field(default=0.50, ge=0.0, le=1.0)


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
    district_id: Optional[int] = Query(None),
    police_station_id: Optional[int] = Query(None),
    top_k: int = Query(10, ge=1, le=100),
    session_id: str = Depends(get_session_id)
):
    """
    Predict Future High-Risk Hotspot Grid Cells (Next 24h / 7d).
    """
    try:
        service = PredictionService()
        return service.predict_future_hotspots(
            district_id=district_id,
            police_station_id=police_station_id,
            top_k=top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotspot prediction failed: {str(e)}")


@router.api_route("/recidivism", methods=["GET", "POST"])
def predict_recidivism(
    req: Optional[OffenderRecidivismRequest] = None,
    accused_id: int = Query(1),
    age_years: int = Query(35),
    prior_case_count: int = Query(2),
    arrest_count: int = Query(1),
    grave_offence_ratio: float = Query(0.50),
    session_id: str = Depends(get_session_id)
):
    """
    Predict Repeat Offender Recidivism Risk & Profile.
    """
    try:
        service = PredictionService()
        if req:
            acc_id = req.accused_id
            age = req.age_years
            p_cnt = req.prior_case_count
            arr = req.arrest_count
            g_ratio = req.grave_offence_ratio
        else:
            acc_id = accused_id
            age = age_years
            p_cnt = prior_case_count
            arr = arrest_count
            g_ratio = grave_offence_ratio

        return service.predict_recidivism(
            accused_id=acc_id,
            age_years=age,
            prior_case_count=p_cnt,
            arrest_count=arr,
            grave_offence_ratio=g_ratio
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recidivism prediction failed: {str(e)}")
