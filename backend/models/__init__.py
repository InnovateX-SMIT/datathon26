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
from backend.models.recommendation import Recommendation, ResourceAllocation, RecommendationHistory
from backend.models.report import Report
from backend.models.audit_log import AuditLog
from backend.models.dataset import Dataset
from backend.models.ml_model import MLModel

# New FIR-compliant models, mixins, and lookups
from backend.models.mixins import TimestampMixin, ActiveFlagMixin, BaseLookupMixin
from backend.models.fir_lookup import (
    CaseCategory, GravityOffence, CaseStatusMaster, CasteMaster,
    ReligionMaster, OccupationMaster, GenderMaster, NationalityMaster, BloodGroupMaster
)
from backend.models.fir_geography import State, District, Court
from backend.models.fir_organization import UnitType, Unit, Rank, Designation, Employee
from backend.models.fir_case import CaseMaster, Inv_OccuranceTime
from backend.models.fir_people import ComplainantDetails, FIRVictim, Accused
from backend.models.fir_proceedings import ArrestSurrender, InvArrestSurrenderAccused, ChargesheetDetails
from backend.models.fir_law import Act, Section, ActSectionAssociation, CrimeHead, CrimeSubHead, CrimeHeadActSection

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
    "RecommendationHistory",
    "Report",
    "AuditLog",
    "Dataset",
    "MLModel",
    # FIR structures
    "TimestampMixin",
    "ActiveFlagMixin",
    "BaseLookupMixin",
    "CaseCategory",
    "GravityOffence",
    "CaseStatusMaster",
    "CasteMaster",
    "ReligionMaster",
    "OccupationMaster",
    "GenderMaster",
    "NationalityMaster",
    "BloodGroupMaster",
    "State",
    "District",
    "Court",
    "UnitType",
    "Unit",
    "Rank",
    "Designation",
    "Employee",
    "CaseMaster",
    "Inv_OccuranceTime",
    "ComplainantDetails",
    "FIRVictim",
    "Accused",
    "ArrestSurrender",
    "InvArrestSurrenderAccused",
    "ChargesheetDetails",
    "Act",
    "Section",
    "ActSectionAssociation",
    "CrimeHead",
    "CrimeSubHead",
    "CrimeHeadActSection",
]

