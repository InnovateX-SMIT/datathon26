from backend.core.database import Base
from backend.models.user import User, UserRole
from backend.models.location import Location
from backend.models.police_station import PoliceStation
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.victim import Victim
from backend.models.crime_participation import CrimeParticipation
from backend.models.prediction import Prediction
from backend.models.alert import Alert
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.models.report import Report
from backend.models.audit_log import AuditLog

# Expose them all in __all__
__all__ = [
    "Base",
    "User",
    "UserRole",
    "Location",
    "PoliceStation",
    "CrimeEvent",
    "Criminal",
    "Victim",
    "CrimeParticipation",
    "Prediction",
    "Alert",
    "Recommendation",
    "ResourceAllocation",
    "Report",
    "AuditLog",
]
