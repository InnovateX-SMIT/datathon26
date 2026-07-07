from sqlalchemy import Column, Integer, String, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.mixins import TimestampMixin, ActiveFlagMixin

class Act(ActiveFlagMixin, TimestampMixin, Base):
    __tablename__ = "act"

    ActCode = Column(String(50), primary_key=True)
    ActDescription = Column(String(500), nullable=True)
    ShortName = Column(String(100), nullable=True)

    # Relationships
    sections = relationship("Section", back_populates="act", cascade="all, delete-orphan")

class Section(ActiveFlagMixin, TimestampMixin, Base):
    __tablename__ = "section"

    ActCode = Column(String(50), ForeignKey("act.ActCode"), primary_key=True)
    SectionCode = Column(String(100), primary_key=True)
    SectionDescription = Column(String(500), nullable=True)

    # Relationships
    act = relationship("Act", back_populates="sections")

class ActSectionAssociation(TimestampMixin, Base):
    __tablename__ = "act_section_association"

    CaseMasterID = Column(Integer, ForeignKey("case_master.CaseMasterID"), primary_key=True)
    ActCode = Column(String(50), primary_key=True)
    SectionCode = Column(String(100), primary_key=True)
    ActOrderID = Column(Integer, nullable=True)
    SectionOrderID = Column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['ActCode', 'SectionCode'],
            ['section.ActCode', 'section.SectionCode']
        ),
    )

    # Relationships
    case_master = relationship("CaseMaster", back_populates="act_sections")
    section = relationship("Section")

class CrimeHead(ActiveFlagMixin, TimestampMixin, Base):
    __tablename__ = "crime_head"

    id = Column("CrimeHeadID", Integer, primary_key=True)
    CrimeGroupName = Column(String(255), nullable=False)

    # Relationships
    sub_heads = relationship("CrimeSubHead", back_populates="crime_head", cascade="all, delete-orphan")

class CrimeSubHead(TimestampMixin, Base):
    __tablename__ = "crime_sub_head"

    id = Column("CrimeSubHeadID", Integer, primary_key=True)
    CrimeHeadID = Column(Integer, ForeignKey("crime_head.CrimeHeadID"), nullable=False)
    CrimeHeadName = Column(String(255), nullable=False)
    SeqID = Column(Integer, nullable=True)

    # Relationships
    crime_head = relationship("CrimeHead", back_populates="sub_heads")

class CrimeHeadActSection(TimestampMixin, Base):
    __tablename__ = "crime_head_act_section"

    CrimeHeadID = Column(Integer, ForeignKey("crime_head.CrimeHeadID"), primary_key=True)
    ActCode = Column(String(50), primary_key=True)
    SectionCode = Column(String(100), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['ActCode', 'SectionCode'],
            ['section.ActCode', 'section.SectionCode']
        ),
    )

    # Relationships
    crime_head = relationship("CrimeHead")
    section = relationship("Section")
