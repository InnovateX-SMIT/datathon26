from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import List, Optional

# ==========================================
# Lookup / Master Table DTOs
# ==========================================

class LookupDTO(BaseModel):
    id: int
    name: str
    active: bool = True
    sort_order: int = 0

    model_config = {
        "from_attributes": True
    }

class StateDTO(LookupDTO):
    NationalityID: Optional[int] = None

class DistrictDTO(LookupDTO):
    StateID: int

class CourtDTO(LookupDTO):
    DistrictID: int
    StateID: int

class UnitTypeDTO(LookupDTO):
    CityDistState: Optional[str] = None
    Hierarchy: Optional[int] = None

class UnitDTO(LookupDTO):
    TypeID: int
    ParentUnit: Optional[int] = None
    NationalityID: Optional[int] = None
    StateID: int
    DistrictID: int

class RankDTO(LookupDTO):
    Hierarchy: Optional[int] = None

class DesignationDTO(LookupDTO):
    SortOrder: Optional[int] = None

class EmployeeDTO(BaseModel):
    id: int
    DistrictID: int
    UnitID: int
    RankID: int
    DesignationID: int
    KGID: str
    FirstName: str
    EmployeeDOB: Optional[date] = None
    GenderID: int
    BloodGroupID: Optional[int] = None
    PhysicallyChallenged: bool = False
    AppointmentDate: Optional[date] = None
    active: bool = True

    model_config = {
        "from_attributes": True
    }

class CaseCategoryDTO(LookupDTO):
    pass

class GravityOffenceDTO(LookupDTO):
    pass

class CaseStatusDTO(LookupDTO):
    pass

class CasteDTO(LookupDTO):
    pass

class ReligionDTO(LookupDTO):
    pass

class OccupationDTO(LookupDTO):
    pass

class GenderDTO(LookupDTO):
    pass

class NationalityDTO(LookupDTO):
    pass

class BloodGroupDTO(LookupDTO):
    pass

class ActDTO(BaseModel):
    ActCode: str
    ActDescription: Optional[str] = None
    ShortName: Optional[str] = None
    active: bool = True

    model_config = {
        "from_attributes": True
    }

class SectionDTO(BaseModel):
    ActCode: str
    SectionCode: str
    SectionDescription: Optional[str] = None
    active: bool = True

    model_config = {
        "from_attributes": True
    }

class CrimeHeadDTO(BaseModel):
    id: int
    CrimeGroupName: str
    active: bool = True

    model_config = {
        "from_attributes": True
    }

class CrimeSubHeadDTO(BaseModel):
    id: int
    CrimeHeadID: int
    CrimeHeadName: str
    SeqID: Optional[int] = None

    model_config = {
        "from_attributes": True
    }

# ==========================================
# Transactional Incident DTOs
# ==========================================

class InvOccuranceTimeBase(BaseModel):
    IncidentFromDate: Optional[datetime] = None
    IncidentToDate: Optional[datetime] = None
    InfoReceivedPSDate: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    BriefFacts: Optional[str] = None

class InvOccuranceTimeCreate(InvOccuranceTimeBase):
    pass

class InvOccuranceTimeResponse(InvOccuranceTimeBase):
    CaseMasterID: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ComplainantDetailsBase(BaseModel):
    ComplainantName: str
    AgeYear: Optional[int] = None
    OccupationID: Optional[int] = None
    ReligionID: Optional[int] = None
    CasteID: Optional[int] = None
    GenderID: Optional[int] = None

class ComplainantDetailsCreate(ComplainantDetailsBase):
    pass

class ComplainantDetailsResponse(ComplainantDetailsBase):
    id: int
    CaseMasterID: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class FIRVictimBase(BaseModel):
    VictimName: str
    AgeYear: Optional[int] = None
    GenderID: Optional[int] = None
    VictimPolice: str = "0"

class FIRVictimCreate(FIRVictimBase):
    pass

class FIRVictimResponse(FIRVictimBase):
    id: int
    CaseMasterID: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class AccusedBase(BaseModel):
    AccusedName: str
    AgeYear: Optional[int] = None
    GenderID: Optional[int] = None
    PersonID: Optional[str] = None

class AccusedCreate(AccusedBase):
    pass

class AccusedResponse(AccusedBase):
    id: int
    CaseMasterID: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ActSectionAssociationBase(BaseModel):
    ActCode: str
    SectionCode: str
    ActOrderID: Optional[int] = None
    SectionOrderID: Optional[int] = None

class ActSectionAssociationCreate(ActSectionAssociationBase):
    pass

class ActSectionAssociationResponse(ActSectionAssociationBase):
    CaseMasterID: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ArrestSurrenderBase(BaseModel):
    ArrestSurrenderTypeID: int
    ArrestSurrenderDate: date
    ArrestSurrenderStateId: int
    ArrestSurrenderDistrictId: int
    PoliceStationID: int
    IOID: int
    CourtID: int
    AccusedMasterID: int
    IsAccused: bool = True
    IsComplainantAccused: bool = False

class ArrestSurrenderCreate(ArrestSurrenderBase):
    associated_accused_ids: List[int] = []

class ArrestSurrenderResponse(ArrestSurrenderBase):
    id: int
    CaseMasterID: int
    created_at: datetime
    updated_at: datetime
    associated_accused_ids: List[int] = []

    model_config = {
        "from_attributes": True
    }

class ChargesheetDetailsBase(BaseModel):
    csdate: datetime
    cstype: str
    PolicePersonID: int

class ChargesheetDetailsCreate(ChargesheetDetailsBase):
    pass

class ChargesheetDetailsResponse(ChargesheetDetailsBase):
    id: int
    CaseMasterID: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class CaseMasterBase(BaseModel):
    CrimeNo: Optional[str] = None
    CaseNo: Optional[str] = None
    CrimeRegisteredDate: Optional[date] = None
    PolicePersonID: int
    PoliceStationID: int
    CaseCategoryID: int
    GravityOffenceID: int
    CrimeMajorHeadID: int
    CrimeMinorHeadID: int
    CaseStatusID: int
    CourtID: int
    BriefFacts: Optional[str] = None
    dataset_id: Optional[int] = None

class CaseMasterCreate(CaseMasterBase):
    occurrence_time: Optional[InvOccuranceTimeCreate] = None
    complainants: List[ComplainantDetailsCreate] = []
    victims: List[FIRVictimCreate] = []
    accused: List[AccusedCreate] = []
    act_sections: List[ActSectionAssociationCreate] = []
    arrest_surrenders: List[ArrestSurrenderCreate] = []
    chargesheets: List[ChargesheetDetailsCreate] = []

class CaseMasterResponse(CaseMasterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    occurrence_time: Optional[InvOccuranceTimeResponse] = None
    complainants: List[ComplainantDetailsResponse] = []
    victims: List[FIRVictimResponse] = []
    accused: List[AccusedResponse] = []
    act_sections: List[ActSectionAssociationResponse] = []
    arrest_surrenders: List[ArrestSurrenderResponse] = []
    chargesheets: List[ChargesheetDetailsResponse] = []

    model_config = {
        "from_attributes": True
    }
