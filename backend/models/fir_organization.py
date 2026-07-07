from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.mixins import BaseLookupMixin, ActiveFlagMixin, TimestampMixin

class UnitType(BaseLookupMixin, Base):
    __tablename__ = "unit_type"
    __pk_name__ = "UnitTypeID"
    __name_col__ = "UnitTypeName"

    CityDistState = Column(String(100), nullable=True)
    Hierarchy = Column(Integer, nullable=True)

class Unit(BaseLookupMixin, Base):
    __tablename__ = "unit"
    __pk_name__ = "UnitID"
    __name_col__ = "UnitName"

    TypeID = Column(Integer, ForeignKey("unit_type.UnitTypeID"), nullable=False)
    ParentUnit = Column(Integer, ForeignKey("unit.UnitID"), nullable=True)
    NationalityID = Column(Integer, ForeignKey("nationality_master.NationalityID"), nullable=True)
    StateID = Column(Integer, ForeignKey("state.StateID"), nullable=False)
    DistrictID = Column(Integer, ForeignKey("district.DistrictID"), nullable=False)

    # Relationships
    unit_type = relationship("UnitType")
    parent = relationship("Unit", remote_side="Unit.id", back_populates="child_units")
    child_units = relationship("Unit", back_populates="parent")
    nationality = relationship("NationalityMaster")
    state = relationship("State")
    district = relationship("District", back_populates="units")

class Rank(BaseLookupMixin, Base):
    __tablename__ = "rank"
    __pk_name__ = "RankID"
    __name_col__ = "RankName"

    Hierarchy = Column(Integer, nullable=True)

class Designation(BaseLookupMixin, Base):
    __tablename__ = "designation"
    __pk_name__ = "DesignationID"
    __name_col__ = "DesignationName"

    SortOrder = Column(Integer, nullable=True)

class Employee(ActiveFlagMixin, TimestampMixin, Base):
    __tablename__ = "employee"

    id = Column("EmployeeID", Integer, primary_key=True)
    DistrictID = Column(Integer, ForeignKey("district.DistrictID"), nullable=False)
    UnitID = Column(Integer, ForeignKey("unit.UnitID"), nullable=False)
    RankID = Column(Integer, ForeignKey("rank.RankID"), nullable=False)
    DesignationID = Column(Integer, ForeignKey("designation.DesignationID"), nullable=False)
    KGID = Column(String(50), nullable=False, unique=True, index=True)
    FirstName = Column(String(150), nullable=False)
    EmployeeDOB = Column(Date, nullable=True)
    GenderID = Column(Integer, ForeignKey("gender_master.GenderID"), nullable=False)
    BloodGroupID = Column(Integer, ForeignKey("blood_group_master.BloodGroupID"), nullable=True)
    PhysicallyChallenged = Column(Boolean, default=False, nullable=False)
    AppointmentDate = Column(Date, nullable=True)

    # Relationships
    district = relationship("District", back_populates="employees")
    unit = relationship("Unit")
    rank = relationship("Rank")
    designation = relationship("Designation")
    gender = relationship("GenderMaster")
    blood_group = relationship("BloodGroupMaster")
