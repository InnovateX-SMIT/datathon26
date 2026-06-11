import os
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from backend.repositories.prediction_repository import PredictionRepository

# ML predictor functions imports
from ml.offender_prediction.predict import predict_offender_recidivism
from ml.crime_prediction.predict import predict_crime_category, predict_crime_risk_score
from ml.hotspot_prediction.predict import predict_hotspot_probability
from ml.explainability.shap_analysis import compute_shap_explanations

# Resolve model files directory absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

MODEL_PATHS = {
    "repeat_offender": os.path.join(project_root, "ml", "offender_prediction", "model.pkl"),
    "crime_type": os.path.join(project_root, "ml", "crime_prediction", "model.pkl"),
    "crime_risk": os.path.join(project_root, "ml", "crime_prediction", "risk_model.pkl"),
    "hotspot": os.path.join(project_root, "ml", "hotspot_prediction", "model.pkl"),
}

class PredictionService:
    _cached_models = {}

    def __init__(self, db: Session):
        self.db = db
        self.repo = PredictionRepository(db)

    def _load_model(self, name: str):
        """
        Loads a serialized model dict into memory if not cached.
        """
        if name not in self._cached_models:
            path = MODEL_PATHS[name]
            if not os.path.exists(path):
                raise FileNotFoundError(f"Model file not found at: {path}")
            self._cached_models[name] = joblib.load(path)
        return self._cached_models[name]

    def check_health(self) -> dict:
        """
        Checks model loading health.
        """
        loaded = {}
        for name, path in MODEL_PATHS.items():
            loaded[name] = os.path.exists(path)
        
        status = "healthy" if all(loaded.values()) else "degraded"
        return {
            "status": status,
            "models_loaded": loaded
        }

    def predict_repeat_offender(self, age: float, occupation: str, caste: str, district: str) -> dict:
        """
        Feature 1: Predict repeat offender probability.
        """
        model = self._load_model("repeat_offender")
        features = {
            "age": age,
            "occupation": occupation,
            "caste": caste,
            "district": district
        }
        res = predict_offender_recidivism(model, features)
        
        # Save to database
        val_str = f"Risk: {res['risk_level']} (Prob: {res['probability']:.2f})"
        self.repo.save_prediction(
            prediction_type="repeat-offender",
            prediction_value=val_str,
            confidence_score=res["probability"]
        )
        return res

    def predict_crime_risk(self, district: str, crime_category: str, historical_crime_count: int) -> dict:
        """
        Feature 2: Predict crime risk score.
        """
        model = self._load_model("crime_risk")
        features = {
            "district": district,
            "crime_category": crime_category,
            "historical_crime_count": historical_crime_count
        }
        res = predict_crime_risk_score(model, features)
        
        # Save to database
        val_str = f"Risk: {res['risk_level']} (Score: {res['risk_score']:.1f})"
        self.repo.save_prediction(
            prediction_type="crime-risk",
            prediction_value=val_str,
            confidence_score=res["risk_score"] / 100.0
        )
        return res

    def predict_crime_type(
        self, 
        district: str, 
        month: int, 
        hour: int, 
        day_of_week: int, 
        historical_crime_count: int
    ) -> dict:
        """
        Feature 3: Predict crime type category.
        """
        model = self._load_model("crime_type")
        features = {
            "district": district,
            "month": month,
            "hour": hour,
            "day_of_week": day_of_week,
            "historical_crime_count": historical_crime_count
        }
        res = predict_crime_category(model, features)
        
        # Save to database
        val_str = f"Crime: {res['crime_type']} (Conf: {res['confidence']:.2f})"
        self.repo.save_prediction(
            prediction_type="crime-type",
            prediction_value=val_str,
            confidence_score=res["confidence"]
        )
        return res

    def predict_hotspot(self, district: str, trend_metrics: float, historical_crime_growth: float) -> dict:
        """
        Feature 4: Predict emerging hotspot probability.
        """
        model = self._load_model("hotspot")
        features = {
            "district": district,
            "trend_metrics": trend_metrics,
            "historical_crime_growth": historical_crime_growth
        }
        res = predict_hotspot_probability(model, features)
        
        # Save to database
        val_str = f"Hotspot Prob: {res['hotspot_probability']:.2f} (Trend: {res['trend']})"
        self.repo.save_prediction(
            prediction_type="hotspot",
            prediction_value=val_str,
            confidence_score=res["hotspot_probability"]
        )
        return res

    def generate_shap_explanation(self, prediction_type: str, features: dict) -> list:
        """
        Feature 5: Generate SHAP explanations for any prediction.
        """
        model_map = {
            "repeat-offender": "repeat_offender",
            "crime-risk": "crime_risk",
            "crime-type": "crime_type",
            "hotspot": "hotspot"
        }
        
        m_name = model_map.get(prediction_type)
        if not m_name:
            raise ValueError(f"Unknown prediction type: {prediction_type}")
            
        model = self._load_model(m_name)
        preprocessor = model["preprocessor"]
        clf = model["model"]
        feature_names = model["feature_names"]
        
        # Format input
        df = pd.DataFrame([features])
        X_proc = preprocessor.transform(df)
        
        # Compute SHAP
        shap_exps = compute_shap_explanations(clf, X_proc, feature_names)
        
        return shap_exps

    # Stubs kept for backward compatibility
    def run_recidivism_scoring(self, age: float, caste: str, profession: str, city: str):
        res = self.predict_repeat_offender(age=age, occupation=profession, caste=caste, district=city)
        return {"probability": res["probability"], "repeat": res["risk_level"] == "HIGH"}

    def fetch_historical_predictions(self):
        return self.repo.get_predictions()
