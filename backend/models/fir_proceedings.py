from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.mixins import TimestampMixin

class ArrestSurrender(TimestampMixin, Base):
    __tablename__ = "arrest_surrender"

    id = Column("ArrestSurrenderID", Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("case_master.CaseMasterID"), nullable=False)
    ArrestSurrenderTypeID = Column(Integer, nullable=False)
    ArrestSurrenderDate = Column(Date, nullable=False)
    ArrestSurrenderStateId = Column(Integer, ForeignKey("state.StateID"), nullable=False)
    ArrestSurrenderDistrictId = Column(Integer, ForeignKey("district.DistrictID"), nullable=False)
    PoliceStationID = Column(Integer, ForeignKey("unit.UnitID"), nullable=False)
    IOID = Column(Integer, ForeignKey("employee.EmployeeID"), nullable=False)
    CourtID = Column(Integer, ForeignKey("court.CourtID"), nullable=False)
    # AccusedMasterID represents the primary accused individual for this specific arrest event.
    AccusedMasterID = Column(Integer, ForeignKey("accused.AccusedMasterID"), nullable=False)
    IsAccused = Column(Boolean, default=True, nullable=False)
    IsComplainantAccused = Column(Boolean, default=False, nullable=False)

    # Relationships
    case_master = relationship("CaseMaster", back_populates="arrest_surrenders")
    state = relationship("State")
    district = relationship("District")
    police_station = relationship("Unit")
    io = relationship("Employee")
    court = relationship("Court")
    
    # Primary accused relation (direct 1:M relationship mapping)
    primary_accused = relationship("Accused", back_populates="arrest_surrenders")
    
    # Joint/multiple accused involved in the same arrest event (mapped via many-to-many junction)
    all_accused = relationship("Accused", secondary="inv_arrestsurrenderaccused")

    @property
    def associated_accused_ids(self) -> list[int]:
        return [acc.id for acc in self.all_accused] if self.all_accused else []

class InvArrestSurrenderAccused(Base):
    __tablename__ = "inv_arrestsurrenderaccused"

    ArrestSurrenderID = Column(Integer, ForeignKey("arrest_surrender.ArrestSurrenderID"), primary_key=True)
    AccusedMasterID = Column(Integer, ForeignKey("accused.AccusedMasterID"), primary_key=True)

class ChargesheetDetails(TimestampMixin, Base):
    __tablename__ = "chargesheet_details"

    id = Column("CSID", Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("case_master.CaseMasterID"), nullable=False)
    csdate = Column(DateTime, nullable=False)
    cstype = Column(String(10), nullable=False)  # e.g., 'A', 'B', 'C'
    PolicePersonID = Column(Integer, ForeignKey("employee.EmployeeID"), nullable=False)

    # Relationships
    case_master = relationship("CaseMaster", back_populates="chargesheets")
    police_person = relationship("Employee")
