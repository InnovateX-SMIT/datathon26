from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class SuspectProfile(BaseModel):
    age: float
    caste: str
    profession: str
    present_city: str
    district_name: str

class RecidivismResult(BaseModel):
    recidivism_probability: float
    is_repeat_offender: bool
    risk_level: str
    explainability_shap: Dict[str, float]

@router.post("/recidivism", response_model=RecidivismResult)
def predict_recidivism(profile: SuspectProfile):
    return RecidivismResult(
        recidivism_probability=0.78,
        is_repeat_offender=True,
        risk_level="HIGH",
        explainability_shap={
            "age": -0.12,
            "district_name": 0.35,
            "profession": 0.22,
            "caste": 0.15
        }
    )

@router.get("/history")
def get_prediction_history() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "suspect_name": "Accused A",
            "prediction_type": "Recidivism",
            "prediction_value": "High Risk (78%)",
            "generated_at": "2026-06-08T10:00:00"
        }
    ]
