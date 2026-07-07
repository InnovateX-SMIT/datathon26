from backend.core.database import Base
from backend.models.mixins import BaseLookupMixin

class CaseCategory(BaseLookupMixin, Base):
    __tablename__ = "case_category"
    __pk_name__ = "CaseCategoryID"
    __name_col__ = "LookupValue"

class GravityOffence(BaseLookupMixin, Base):
    __tablename__ = "gravity_offence"
    __pk_name__ = "GravityOffenceID"
    __name_col__ = "LookupValue"

class CaseStatusMaster(BaseLookupMixin, Base):
    __tablename__ = "case_status_master"
    __pk_name__ = "CaseStatusID"
    __name_col__ = "CaseStatusName"

class CasteMaster(BaseLookupMixin, Base):
    __tablename__ = "caste_master"
    __pk_name__ = "caste_master_id"
    __name_col__ = "caste_master_name"

class ReligionMaster(BaseLookupMixin, Base):
    __tablename__ = "religion_master"
    __pk_name__ = "ReligionID"
    __name_col__ = "ReligionName"

class OccupationMaster(BaseLookupMixin, Base):
    __tablename__ = "occupation_master"
    __pk_name__ = "OccupationID"
    __name_col__ = "OccupationName"

class GenderMaster(BaseLookupMixin, Base):
    __tablename__ = "gender_master"
    __pk_name__ = "GenderID"
    __name_col__ = "GenderName"

class NationalityMaster(BaseLookupMixin, Base):
    __tablename__ = "nationality_master"
    __pk_name__ = "NationalityID"
    __name_col__ = "NationalityName"

class BloodGroupMaster(BaseLookupMixin, Base):
    __tablename__ = "blood_group_master"
    __pk_name__ = "BloodGroupID"
    __name_col__ = "BloodGroupName"
