from backend.schemas.user import UserBase, UserCreate, UserResponse
from backend.schemas.location import LocationBase, LocationCreate, LocationResponse
from backend.schemas.police_station import PoliceStationBase, PoliceStationCreate, PoliceStationResponse
from backend.schemas.crime import CrimeEventBase, CrimeEventCreate, CrimeEventResponse
from backend.schemas.criminal import CriminalBase, CriminalCreate, CriminalResponse
from backend.schemas.victim import VictimBase, VictimCreate, VictimResponse
from backend.schemas.crime_participation import CrimeParticipationBase, CrimeParticipationCreate, CrimeParticipationResponse
from backend.schemas.prediction import PredictionBase, PredictionCreate, PredictionResponse
from backend.schemas.alert import AlertBase, AlertCreate, AlertResponse
from backend.schemas.recommendation import RecommendationBase, RecommendationCreate, RecommendationResponse
from backend.schemas.report import ReportBase, ReportCreate, ReportResponse
from backend.schemas.fir import (
    StateDTO, DistrictDTO, CourtDTO, UnitTypeDTO, UnitDTO, RankDTO, DesignationDTO, EmployeeDTO,
    CaseCategoryDTO, GravityOffenceDTO, CaseStatusDTO, CasteDTO, ReligionDTO, OccupationDTO,
    GenderDTO, NationalityDTO, BloodGroupDTO, ActDTO, SectionDTO, CrimeHeadDTO, CrimeSubHeadDTO,
    InvOccuranceTimeCreate, InvOccuranceTimeResponse, ComplainantDetailsCreate, ComplainantDetailsResponse,
    FIRVictimCreate, FIRVictimResponse, AccusedCreate, AccusedResponse, ActSectionAssociationCreate,
    ActSectionAssociationResponse, ArrestSurrenderCreate, ArrestSurrenderResponse, ChargesheetDetailsCreate,
    ChargesheetDetailsResponse, CaseMasterCreate, CaseMasterResponse
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "LocationBase",
    "LocationCreate",
    "LocationResponse",
    "PoliceStationBase",
    "PoliceStationCreate",
    "PoliceStationResponse",
    "CrimeEventBase",
    "CrimeEventCreate",
    "CrimeEventResponse",
    "CriminalBase",
    "CriminalCreate",
    "CriminalResponse",
    "VictimBase",
    "VictimCreate",
    "VictimResponse",
    "CrimeParticipationBase",
    "CrimeParticipationCreate",
    "CrimeParticipationResponse",
    "PredictionBase",
    "PredictionCreate",
    "PredictionResponse",
    "AlertBase",
    "AlertCreate",
    "AlertResponse",
    "RecommendationBase",
    "RecommendationCreate",
    "RecommendationResponse",
    "ReportBase",
    "ReportCreate",
    "ReportResponse",
    "StateDTO", "DistrictDTO", "CourtDTO", "UnitTypeDTO", "UnitDTO", "RankDTO", "DesignationDTO", "EmployeeDTO",
    "CaseCategoryDTO", "GravityOffenceDTO", "CaseStatusDTO", "CasteDTO", "ReligionDTO", "OccupationDTO",
    "GenderDTO", "NationalityDTO", "BloodGroupDTO", "ActDTO", "SectionDTO", "CrimeHeadDTO", "CrimeSubHeadDTO",
    "InvOccuranceTimeCreate", "InvOccuranceTimeResponse", "ComplainantDetailsCreate", "ComplainantDetailsResponse",
    "FIRVictimCreate", "FIRVictimResponse", "AccusedCreate", "AccusedResponse", "ActSectionAssociationCreate",
    "ActSectionAssociationResponse", "ArrestSurrenderCreate", "ArrestSurrenderResponse", "ChargesheetDetailsCreate",
    "ChargesheetDetailsResponse", "CaseMasterCreate", "CaseMasterResponse"
]
