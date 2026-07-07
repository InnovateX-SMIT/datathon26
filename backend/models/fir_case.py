from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.mixins import TimestampMixin

class CaseMaster(TimestampMixin, Base):
    __tablename__ = "case_master"

    id = Column("CaseMasterID", Integer, primary_key=True)
    CrimeNo = Column(String(50), nullable=False, index=True)
    CaseNo = Column(String(50), nullable=False, index=True)
    CrimeRegisteredDate = Column(Date, nullable=False)
    PolicePersonID = Column(Integer, ForeignKey("employee.EmployeeID"), nullable=False)
    PoliceStationID = Column(Integer, ForeignKey("unit.UnitID"), nullable=False)
    CaseCategoryID = Column(Integer, ForeignKey("case_category.CaseCategoryID"), nullable=False)
    GravityOffenceID = Column(Integer, ForeignKey("gravity_offence.GravityOffenceID"), nullable=False)
    CrimeMajorHeadID = Column(Integer, ForeignKey("crime_head.CrimeHeadID"), nullable=False)
    CrimeMinorHeadID = Column(Integer, ForeignKey("crime_sub_head.CrimeSubHeadID"), nullable=False)
    CaseStatusID = Column(Integer, ForeignKey("case_status_master.CaseStatusID"), nullable=False)
    CourtID = Column(Integer, ForeignKey("court.CourtID"), nullable=False)
    BriefFacts = Column(Text, nullable=True)

    # Relationships
    police_person = relationship("Employee")
    police_station = relationship("Unit")
    case_category = relationship("CaseCategory")
    gravity_offence = relationship("GravityOffence")
    crime_major_head = relationship("CrimeHead")
    crime_minor_head = relationship("CrimeSubHead")
    case_status = relationship("CaseStatusMaster")
    court = relationship("Court")

    occurrence_time = relationship("Inv_OccuranceTime", back_populates="case_master", uselist=False, cascade="all, delete-orphan")
    complainants = relationship("ComplainantDetails", back_populates="case_master", cascade="all, delete-orphan")
    victims = relationship("FIRVictim", back_populates="case_master", cascade="all, delete-orphan")
    accused = relationship("Accused", back_populates="case_master", cascade="all, delete-orphan")
    arrest_surrenders = relationship("ArrestSurrender", back_populates="case_master", cascade="all, delete-orphan")
    chargesheets = relationship("ChargesheetDetails", back_populates="case_master", cascade="all, delete-orphan")
    act_sections = relationship("ActSectionAssociation", back_populates="case_master", cascade="all, delete-orphan")

class Inv_OccuranceTime(TimestampMixin, Base):
    __tablename__ = "inv_occurance_time"

    CaseMasterID = Column(Integer, ForeignKey("case_master.CaseMasterID"), primary_key=True)
    IncidentFromDate = Column(DateTime, nullable=False)
    IncidentToDate = Column(DateTime, nullable=True)
    InfoReceivedPSDate = Column(DateTime, nullable=False)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    BriefFacts = Column(Text, nullable=True)

    # Relationships
    case_master = relationship("CaseMaster", back_populates="occurrence_time")
