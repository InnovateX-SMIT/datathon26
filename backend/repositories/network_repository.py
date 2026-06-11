from sqlalchemy.orm import Session, joinedload, selectinload
from typing import Optional
from backend.models.criminal import Criminal
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.models.crime_participation import CrimeParticipation

class NetworkRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_criminal_by_id(self, criminal_id: int) -> Optional[Criminal]:
        return self.db.query(Criminal).filter(Criminal.id == criminal_id).first()

    def get_crime_by_id(self, crime_id: int) -> Optional[CrimeEvent]:
        return self.db.query(CrimeEvent).filter(CrimeEvent.id == crime_id).first()

    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        return self.db.query(Location).filter(Location.id == location_id).first()

    def get_criminal_network(self, criminal_id: int) -> Optional[Criminal]:
        return (
            self.db.query(Criminal)
            .filter(Criminal.id == criminal_id)
            .options(
                selectinload(Criminal.participations)
                .selectinload(CrimeParticipation.crime_event)
                .selectinload(CrimeEvent.location)
            )
            .first()
        )

    def get_crime_network(self, crime_id: int) -> Optional[CrimeEvent]:
        return (
            self.db.query(CrimeEvent)
            .filter(CrimeEvent.id == crime_id)
            .options(
                selectinload(CrimeEvent.participations)
                .selectinload(CrimeParticipation.criminal),
                joinedload(CrimeEvent.location)
            )
            .first()
        )

    def get_location_network(self, location_id: int) -> Optional[Location]:
        return (
            self.db.query(Location)
            .filter(Location.id == location_id)
            .options(
                selectinload(Location.crime_events)
                .selectinload(CrimeEvent.participations)
                .selectinload(CrimeParticipation.criminal)
            )
            .first()
        )
