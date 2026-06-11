from sqlalchemy.orm import Session
from backend.models.prediction import Prediction
from datetime import datetime
from typing import Optional

class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_prediction(
        self, 
        prediction_type: str, 
        prediction_value: str, 
        confidence_score: float,
        crime_event_id: Optional[int] = None
    ) -> Prediction:
        """
        Persists a new prediction record to the predictions table.
        """
        db_prediction = Prediction(
            prediction_type=prediction_type,
            prediction_value=prediction_value,
            confidence_score=confidence_score,
            crime_event_id=crime_event_id,
            generated_at=datetime.utcnow()
        )
        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)
        return db_prediction

    def get_predictions(self, limit: int = 100):
        """
        Retrieve prediction log.
        """
        return self.db.query(Prediction).order_by(Prediction.generated_at.desc()).limit(limit).all()
