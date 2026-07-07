from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.mixins import BaseLookupMixin

class State(BaseLookupMixin, Base):
    __tablename__ = "state"
    __pk_name__ = "StateID"
    __name_col__ = "StateName"

    NationalityID = Column(Integer, ForeignKey("nationality_master.NationalityID"), nullable=True)

    # Relationships
    nationality = relationship("NationalityMaster")
    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")

class District(BaseLookupMixin, Base):
    __tablename__ = "district"
    __pk_name__ = "DistrictID"
    __name_col__ = "DistrictName"

    StateID = Column(Integer, ForeignKey("state.StateID"), nullable=False)

    # Relationships
    state = relationship("State", back_populates="districts")
    courts = relationship("Court", back_populates="district", cascade="all, delete-orphan")
    units = relationship("Unit", back_populates="district", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="district", cascade="all, delete-orphan")

class Court(BaseLookupMixin, Base):
    __tablename__ = "court"
    __pk_name__ = "CourtID"
    __name_col__ = "CourtName"

    DistrictID = Column(Integer, ForeignKey("district.DistrictID"), nullable=False)
    StateID = Column(Integer, ForeignKey("state.StateID"), nullable=False)

    # Relationships
    district = relationship("District", back_populates="courts")
    state = relationship("State")
