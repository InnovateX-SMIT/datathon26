from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.services.prediction_service import PredictionService

# Import schemas
from backend.schemas.prediction import (
    PredictionHealthResponse,
    RepeatOffenderRequest,
    RepeatOffenderResponse,
    CrimeRiskRequest,
    CrimeRiskResponse,
    CrimeTypeRequest,
    CrimeTypeResponse,
    HotspotRequest,
    HotspotResponse,
    ExplainRequest,
    ExplainResponse
)

router = APIRouter()

@router.get("/health", response_model=PredictionHealthResponse)
def get_health(db: Session = Depends(get_db)):
    """
    Check if the ML models are successfully trained and loadable in memory.
    """
    try:
        service = PredictionService(db)
        health_data = service.check_health()
        return PredictionHealthResponse(data=health_data)
    except Exception as e:
        logger.error(f"Error in prediction health check: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying prediction engine health"
        )

@router.post("/repeat-offender", response_model=RepeatOffenderResponse)
def predict_repeat_offender(
    payload: RepeatOffenderRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Predict probability of an offender becoming a repeat offender.
    """
    try:
        service = PredictionService(db)
        result = service.predict_repeat_offender(
            age=payload.age,
            occupation=payload.occupation,
            caste=payload.caste,
            district=payload.district
        )
        return RepeatOffenderResponse(data=result)
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fnfe)
        )
    except Exception as e:
        logger.error(f"Error predicting repeat offender: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing repeat offender prediction"
        )

@router.post("/crime-risk", response_model=CrimeRiskResponse)
def predict_crime_risk(
    payload: CrimeRiskRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Predict risk level of crime occurrence in a district.
    """
    try:
        service = PredictionService(db)
        result = service.predict_crime_risk(
            district=payload.district,
            crime_category=payload.crime_category,
            historical_crime_count=payload.historical_crime_count
        )
        return CrimeRiskResponse(data=result)
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fnfe)
        )
    except Exception as e:
        logger.error(f"Error predicting crime risk: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing crime risk scoring"
        )

@router.post("/crime-type", response_model=CrimeTypeResponse)
def predict_crime_type(
    payload: CrimeTypeRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Predict likely future crime category.
    """
    try:
        service = PredictionService(db)
        result = service.predict_crime_type(
            district=payload.district,
            month=payload.month,
            hour=payload.hour,
            day_of_week=payload.day_of_week,
            historical_crime_count=payload.historical_crime_count
        )
        return CrimeTypeResponse(data=result)
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fnfe)
        )
    except Exception as e:
        logger.error(f"Error predicting crime type: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing crime type prediction"
        )

@router.post("/hotspot", response_model=HotspotResponse)
def predict_hotspot(
    payload: HotspotRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Predict district emerging hotspot probability.
    """
    try:
        service = PredictionService(db)
        result = service.predict_hotspot(
            district=payload.district,
            trend_metrics=payload.trend_metrics,
            historical_crime_growth=payload.historical_crime_growth
        )
        return HotspotResponse(data=result)
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fnfe)
        )
    except Exception as e:
        logger.error(f"Error predicting hotspot: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing emerging hotspot prediction"
        )

@router.post("/explain", response_model=ExplainResponse)
def predict_explain(
    payload: ExplainRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Explain predictions with SHAP values.
    """
    try:
        service = PredictionService(db)
        result = service.generate_shap_explanation(
            prediction_type=payload.prediction_type,
            features=payload.features
        )
        return ExplainResponse(data=result)
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fnfe)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error explaining prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating SHAP explainability analysis"
        )
