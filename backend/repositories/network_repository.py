from sqlalchemy.orm import Session, joinedload, selectinload, with_loader_criteria
from typing import Optional
from backend.models.criminal import Criminal
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.models.crime_participation import CrimeParticipation

class NetworkRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_criminal_by_id(self, criminal_id: int, dataset_id: Optional[int] = None) -> Optional[Criminal]:
        q = self.db.query(Criminal).filter(Criminal.id == criminal_id)
        if dataset_id is not None:
            q = q.filter(Criminal.dataset_id == dataset_id)
        return q.first()

    def get_crime_by_id(self, crime_id: int, dataset_id: Optional[int] = None) -> Optional[CrimeEvent]:
        q = self.db.query(CrimeEvent).filter(CrimeEvent.id == crime_id)
        if dataset_id is not None:
            q = q.filter(CrimeEvent.dataset_id == dataset_id)
        return q.first()

    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        return self.db.query(Location).filter(Location.id == location_id).first()

    def get_criminal_network(self, criminal_id: int, dataset_id: Optional[int] = None) -> Optional[Criminal]:
        q = self.db.query(Criminal).filter(Criminal.id == criminal_id)
        if dataset_id is not None:
            q = q.filter(Criminal.dataset_id == dataset_id)
        return (
            q.options(
                selectinload(Criminal.participations)
                .selectinload(CrimeParticipation.crime_event)
                .selectinload(CrimeEvent.location)
            )
            .first()
        )

    def get_crime_network(self, crime_id: int, dataset_id: Optional[int] = None) -> Optional[CrimeEvent]:
        q = self.db.query(CrimeEvent).filter(CrimeEvent.id == crime_id)
        if dataset_id is not None:
            q = q.filter(CrimeEvent.dataset_id == dataset_id)
        return (
            q.options(
                selectinload(CrimeEvent.participations)
                .selectinload(CrimeParticipation.criminal),
                joinedload(CrimeEvent.location)
            )
            .first()
        )

    def get_location_network(self, location_id: int, dataset_id: Optional[int] = None) -> Optional[Location]:
        q = self.db.query(Location).filter(Location.id == location_id)
        options = [
            selectinload(Location.crime_events)
            .selectinload(CrimeEvent.participations)
            .selectinload(CrimeParticipation.criminal)
        ]
        if dataset_id is not None:
            options.extend([
                with_loader_criteria(CrimeEvent, CrimeEvent.dataset_id == dataset_id, include_aliases=True),
                with_loader_criteria(CrimeParticipation, CrimeParticipation.dataset_id == dataset_id, include_aliases=True),
                with_loader_criteria(Criminal, Criminal.dataset_id == dataset_id, include_aliases=True),
            ])
        return q.options(*options).first()


    def get_sample_criminals(self, dataset_id: Optional[int] = None, limit: int = 10) -> list[Criminal]:
        q = self.db.query(Criminal)
        if dataset_id is not None:
            q = q.filter(Criminal.dataset_id == dataset_id)
        return q.order_by(Criminal.id.asc()).limit(limit).all()

    def get_all_criminals(self, dataset_id: Optional[int] = None) -> list[Criminal]:
        q = self.db.query(Criminal)
        if dataset_id is not None:
            q = q.filter(Criminal.dataset_id == dataset_id)
        return q.all()

    def get_all_crimes(self, dataset_id: Optional[int] = None) -> list[CrimeEvent]:
        q = self.db.query(CrimeEvent).options(joinedload(CrimeEvent.location))
        if dataset_id is not None:
            q = q.filter(CrimeEvent.dataset_id == dataset_id)
        return q.all()

    def get_all_locations(self) -> list[Location]:
        return self.db.query(Location).all()

    def get_all_participations(self, dataset_id: Optional[int] = None) -> list[CrimeParticipation]:
        q = self.db.query(CrimeParticipation)
        if dataset_id is not None:
            q = q.filter(CrimeParticipation.dataset_id == dataset_id)
        return q.all()
