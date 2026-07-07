from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.mixins import TimestampMixin

class ComplainantDetails(TimestampMixin, Base):
    __tablename__ = "complainant_details"

    id = Column("ComplainantID", Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("case_master.CaseMasterID"), nullable=False)
    ComplainantName = Column(String(150), nullable=False)
    AgeYear = Column(Integer, nullable=True)
    OccupationID = Column(Integer, ForeignKey("occupation_master.OccupationID"), nullable=True)
    ReligionID = Column(Integer, ForeignKey("religion_master.ReligionID"), nullable=True)
    CasteID = Column(Integer, ForeignKey("caste_master.caste_master_id"), nullable=True)
    GenderID = Column(Integer, ForeignKey("gender_master.GenderID"), nullable=False)

    # Relationships
    case_master = relationship("CaseMaster", back_populates="complainants")
    occupation = relationship("OccupationMaster")
    religion = relationship("ReligionMaster")
    caste = relationship("CasteMaster")
    gender = relationship("GenderMaster")

class FIRVictim(TimestampMixin, Base):
    """Normalized FIR-shaped Victim table (mapped as 'victim' singular to avoid clash with legacy 'victims')."""
    __tablename__ = "victim"

    id = Column("VictimMasterID", Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("case_master.CaseMasterID"), nullable=False)
    VictimName = Column(String(150), nullable=False)
    AgeYear = Column(Integer, nullable=True)
    GenderID = Column(Integer, ForeignKey("gender_master.GenderID"), nullable=True)
    VictimPolice = Column(String(10), nullable=True)

    # Relationships
    case_master = relationship("CaseMaster", back_populates="victims")
    gender = relationship("GenderMaster")

class Accused(TimestampMixin, Base):
    __tablename__ = "accused"

    id = Column("AccusedMasterID", Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("case_master.CaseMasterID"), nullable=False)
    AccusedName = Column(String(150), nullable=False)
    AgeYear = Column(Integer, nullable=True)
    GenderID = Column(Integer, ForeignKey("gender_master.GenderID"), nullable=True)
    PersonID = Column(String(50), nullable=True)

    # Relationships
    case_master = relationship("CaseMaster", back_populates="accused")
    gender = relationship("GenderMaster")
    arrest_surrenders = relationship("ArrestSurrender", back_populates="primary_accused")
