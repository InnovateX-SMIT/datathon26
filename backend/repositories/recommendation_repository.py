import json
from sqlalchemy.orm import Session
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.schemas.recommendation import RecommendationCreate
from typing import Optional, List

class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_recommendation(self, rec: RecommendationCreate) -> Recommendation:
        db_rec = Recommendation(
            crime_event_id=rec.crime_event_id,
            priority=rec.priority,
            recommendation_text=rec.recommendation_text,
            reason=rec.reason,
            status=rec.status
        )
        self.db.add(db_rec)
        self.db.commit()
        self.db.refresh(db_rec)
        return db_rec

    def create_recommendations_bulk(self, recs: List[RecommendationCreate]) -> List[Recommendation]:
        db_recs = []
        for rec in recs:
            db_rec = Recommendation(
                crime_event_id=rec.crime_event_id,
                priority=rec.priority,
                recommendation_text=rec.recommendation_text,
                reason=rec.reason,
                status=rec.status
            )
            self.db.add(db_rec)
            db_recs.append(db_rec)
        self.db.commit()
        for db_rec in db_recs:
            self.db.refresh(db_rec)
        return db_recs

    def get_recommendations(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Recommendation]:
        query = self.db.query(Recommendation)
        if status:
            query = query.filter(Recommendation.status == status)
        if priority:
            query = query.filter(Recommendation.priority == priority)
        return query.order_by(Recommendation.created_at.desc()).all()

    def update_recommendation_status(self, recommendation_id: int, status: str) -> Optional[Recommendation]:
        db_rec = self.db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if db_rec:
            db_rec.status = status
            self.db.commit()
            self.db.refresh(db_rec)
        return db_rec

    def save_resource_allocation(
        self,
        district: str,
        allocated_asi: int,
        allocated_chc: int,
        allocated_cpc: int,
        solved_allocation: list
    ) -> ResourceAllocation:
        db_alloc = ResourceAllocation(
            district=district,
            allocated_asi=allocated_asi,
            allocated_chc=allocated_chc,
            allocated_cpc=allocated_cpc,
            solved_allocation=json.dumps(solved_allocation)
        )
        self.db.add(db_alloc)
        self.db.commit()
        self.db.refresh(db_alloc)
        return db_alloc

    def get_resource_allocations_history(self, limit: int = 10) -> List[ResourceAllocation]:
        return self.db.query(ResourceAllocation).order_by(ResourceAllocation.created_at.desc()).limit(limit).all()

    def clear_pending_recommendations(self) -> None:
        self.db.query(Recommendation).filter(Recommendation.status == "pending").delete()
        self.db.commit()
