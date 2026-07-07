from sqlalchemy.orm import Session
from typing import Optional

class MLCompatibilityService:
    """
    ML Compatibility translation layer that abstracts lookup translation.
    It converts normalized database lookup IDs into string feature labels 
    required by the ML prediction models.
    """
    def __init__(self, db: Session):
        self.db = db

    def resolve_district_name(self, district_id: Optional[int]) -> str:
        if not district_id:
            return "Unknown"
        from backend.models.fir_geography import District
        res = self.db.query(District).filter(District.id == district_id).first()
        return res.name if res else "Unknown"

    def resolve_occupation_name(self, occupation_id: Optional[int]) -> str:
        if not occupation_id:
            return "Unknown"
        from backend.models.fir_lookup import OccupationMaster
        res = self.db.query(OccupationMaster).filter(OccupationMaster.id == occupation_id).first()
        return res.name if res else "Unknown"

    def resolve_caste_name(self, caste_id: Optional[int]) -> str:
        if not caste_id:
            return "Unknown"
        from backend.models.fir_lookup import CasteMaster
        res = self.db.query(CasteMaster).filter(CasteMaster.id == caste_id).first()
        return res.name if res else "Unknown"

    def resolve_case_category_name(self, category_id: Optional[int]) -> str:
        if not category_id:
            return "Unknown"
        from backend.models.fir_lookup import CaseCategory
        res = self.db.query(CaseCategory).filter(CaseCategory.id == category_id).first()
        return res.name if res else "Unknown"

    # Feature sets mappings matching legacy ML parameters
    
    def get_repeat_offender_features(self, age: Optional[int], occupation_id: Optional[int], caste_id: Optional[int], district_id: Optional[int]) -> dict:
        return {
            "age": float(age) if age is not None else 30.0,
            "occupation": self.resolve_occupation_name(occupation_id),
            "caste": self.resolve_caste_name(caste_id),
            "district": self.resolve_district_name(district_id)
        }

    def get_crime_risk_features(self, district_id: Optional[int], category_id: Optional[int], historical_crime_count: int) -> dict:
        return {
            "district": self.resolve_district_name(district_id),
            "crime_category": self.resolve_case_category_name(category_id),
            "historical_crime_count": historical_crime_count
        }

    def get_crime_type_features(self, district_id: Optional[int], month: int, hour: int, day_of_week: int, historical_crime_count: int) -> dict:
        return {
            "district": self.resolve_district_name(district_id),
            "month": month,
            "hour": hour,
            "day_of_week": day_of_week,
            "historical_crime_count": historical_crime_count
        }

    def get_hotspot_features(self, district_id: Optional[int], trend_metrics: float, historical_crime_growth: float) -> dict:
        return {
            "district": self.resolve_district_name(district_id),
            "trend_metrics": trend_metrics,
            "historical_crime_growth": historical_crime_growth
        }
