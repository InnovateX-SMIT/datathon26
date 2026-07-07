import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
# Import all models to ensure metadata registration
from backend.models import (
    GenderMaster, NationalityMaster, BloodGroupMaster,
    CaseCategory, GravityOffence, CaseStatusMaster, CasteMaster, ReligionMaster, OccupationMaster,
    State, District, Court, UnitType, Unit, Rank, Designation, Employee,
    CaseMaster, Inv_OccuranceTime, ComplainantDetails, FIRVictim, Accused,
    ArrestSurrender, InvArrestSurrenderAccused, ChargesheetDetails,
    Act, Section, ActSectionAssociation, CrimeHead, CrimeSubHead, CrimeHeadActSection
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    # Setup test database
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_lookup_tables_creation_and_fields(db_session):
    # Test creation and insertion into new lookup masters
    gender = GenderMaster(name="Male")
    nationality = NationalityMaster(name="Indian")
    blood_group = BloodGroupMaster(name="O Positive")
    caste = CasteMaster(name="General")
    religion = ReligionMaster(name="Hindu")
    occupation = OccupationMaster(name="Farmer")
    
    case_cat = CaseCategory(name="FIR")
    gravity = GravityOffence(name="Heinous")
    case_status = CaseStatusMaster(name="Under Investigation")

    db_session.add_all([gender, nationality, blood_group, caste, religion, occupation, case_cat, gravity, case_status])
    db_session.commit()

    # Query them back
    assert db_session.query(GenderMaster).first().name == "Male"
    assert db_session.query(NationalityMaster).first().name == "Indian"
    assert db_session.query(BloodGroupMaster).first().name == "O Positive"
    assert db_session.query(CasteMaster).first().name == "General"
    assert db_session.query(ReligionMaster).first().name == "Hindu"
    assert db_session.query(OccupationMaster).first().name == "Farmer"
    assert db_session.query(CaseCategory).first().name == "FIR"
    assert db_session.query(GravityOffence).first().name == "Heinous"
    assert db_session.query(CaseStatusMaster).first().name == "Under Investigation"


def test_geography_and_organization_relationships(db_session):
    # 1. Lookups
    nationality = NationalityMaster(name="Indian")
    db_session.add(nationality)
    db_session.commit()

    # 2. State
    state = State(name="Karnataka", NationalityID=nationality.id)
    db_session.add(state)
    db_session.commit()

    # 3. District
    district = District(name="Bengaluru", StateID=state.id)
    db_session.add(district)
    db_session.commit()

    # 4. Court
    court = Court(name="District Court Bengaluru", DistrictID=district.id, StateID=state.id)
    db_session.add(court)
    
    # 5. UnitType
    unit_type = UnitType(name="Police Station", CityDistState="District", Hierarchy=1)
    db_session.add(unit_type)
    db_session.commit()

    # 6. Unit
    unit = Unit(
        name="Cubbon Park PS",
        TypeID=unit_type.id,
        NationalityID=nationality.id,
        StateID=state.id,
        DistrictID=district.id
    )
    db_session.add(unit)
    db_session.commit()

    # 7. Rank & Designation
    rank = Rank(name="Inspector", Hierarchy=1)
    designation = Designation(name="SHO", SortOrder=1)
    db_session.add_all([rank, designation])
    db_session.commit()

    # 8. Employee
    gender = GenderMaster(name="Female")
    blood_group = BloodGroupMaster(name="B Positive")
    db_session.add_all([gender, blood_group])
    db_session.commit()

    employee = Employee(
        DistrictID=district.id,
        UnitID=unit.id,
        RankID=rank.id,
        DesignationID=designation.id,
        KGID="KA20261122",
        FirstName="Anupama",
        EmployeeDOB=date(1990, 5, 10),
        GenderID=gender.id,
        BloodGroupID=blood_group.id,
        AppointmentDate=date(2015, 1, 15)
    )
    db_session.add(employee)
    db_session.commit()

    # Verification of joins and relations
    fetched_employee = db_session.query(Employee).filter_by(KGID="KA20261122").first()
    assert fetched_employee.FirstName == "Anupama"
    assert fetched_employee.rank.name == "Inspector"
    assert fetched_employee.designation.name == "SHO"
    assert fetched_employee.unit.name == "Cubbon Park PS"
    assert fetched_employee.gender.name == "Female"
    assert fetched_employee.blood_group.name == "B Positive"


def test_full_fir_flow(db_session):
    # Setup all master dependencies
    nationality = NationalityMaster(name="Indian")
    gender = GenderMaster(name="Male")
    blood_group = BloodGroupMaster(name="O Positive")
    caste = CasteMaster(name="General")
    religion = ReligionMaster(name="Hindu")
    occupation = OccupationMaster(name="Business")
    db_session.add_all([nationality, gender, blood_group, caste, religion, occupation])
    db_session.commit()

    state = State(name="Karnataka", NationalityID=nationality.id)
    db_session.add(state)
    db_session.commit()

    district = District(name="Mysuru", StateID=state.id)
    db_session.add(district)
    db_session.commit()

    court = Court(name="JMFC Mysuru", DistrictID=district.id, StateID=state.id)
    unit_type = UnitType(name="Police Station", CityDistState="City")
    db_session.add_all([court, unit_type])
    db_session.commit()

    unit = Unit(
        name="Devaraja PS",
        TypeID=unit_type.id,
        NationalityID=nationality.id,
        StateID=state.id,
        DistrictID=district.id
    )
    rank = Rank(name="Sub-Inspector")
    designation = Designation(name="Officer")
    db_session.add_all([unit, rank, designation])
    db_session.commit()

    employee = Employee(
        DistrictID=district.id,
        UnitID=unit.id,
        RankID=rank.id,
        DesignationID=designation.id,
        KGID="KA9876",
        FirstName="Rajesh",
        GenderID=gender.id,
        BloodGroupID=blood_group.id
    )
    case_cat = CaseCategory(name="UDR")
    gravity = GravityOffence(name="Non-Heinous")
    case_status = CaseStatusMaster(name="Chargesheeted")
    
    act = Act(ActCode="IPC", ActDescription="Indian Penal Code", ShortName="IPC")
    db_session.add_all([employee, case_cat, gravity, case_status, act])
    db_session.commit()

    section = Section(ActCode=act.ActCode, SectionCode="379", SectionDescription="Theft")
    crime_head = CrimeHead(CrimeGroupName="Theft Group")
    db_session.add_all([section, crime_head])
    db_session.commit()

    crime_sub_head = CrimeSubHead(CrimeHeadID=crime_head.id, CrimeHeadName="House Theft", SeqID=1)
    db_session.add(crime_sub_head)
    db_session.commit()

    # Create CaseMaster
    case = CaseMaster(
        CrimeNo="102140026202600045",
        CaseNo="202600045",
        CrimeRegisteredDate=date(2026, 4, 15),
        PolicePersonID=employee.id,
        PoliceStationID=unit.id,
        CaseCategoryID=case_cat.id,
        GravityOffenceID=gravity.id,
        CrimeMajorHeadID=crime_head.id,
        CrimeMinorHeadID=crime_sub_head.id,
        CaseStatusID=case_status.id,
        CourtID=court.id,
        BriefFacts="A laptop was stolen from a house."
    )
    db_session.add(case)
    db_session.commit()

    # Create Inv_OccuranceTime (1:1)
    occ = Inv_OccuranceTime(
        CaseMasterID=case.id,
        IncidentFromDate=datetime(2026, 4, 14, 22, 0, 0),
        IncidentToDate=datetime(2026, 4, 14, 23, 30, 0),
        InfoReceivedPSDate=datetime(2026, 4, 15, 8, 30, 0),
        latitude=12.2958,
        longitude=76.6394,
        BriefFacts="House break-in occurred."
    )
    db_session.add(occ)
    db_session.commit()

    # Create Complainant
    complainant = ComplainantDetails(
        CaseMasterID=case.id,
        ComplainantName="Suresh",
        AgeYear=40,
        OccupationID=occupation.id,
        ReligionID=religion.id,
        CasteID=caste.id,
        GenderID=gender.id
    )
    
    # Create Victim
    victim = FIRVictim(
        CaseMasterID=case.id,
        VictimName="Suresh",
        AgeYear=40,
        GenderID=gender.id,
        VictimPolice="0"
    )

    # Create Accused
    accused = Accused(
        CaseMasterID=case.id,
        AccusedName="Unknown thief",
        AgeYear=25,
        GenderID=gender.id,
        PersonID="A1"
    )
    db_session.add_all([complainant, victim, accused])
    db_session.commit()

    # Create Act Section Association
    act_assoc = ActSectionAssociation(
        CaseMasterID=case.id,
        ActCode=act.ActCode,
        SectionCode=section.SectionCode,
        ActOrderID=1,
        SectionOrderID=1
    )
    db_session.add(act_assoc)
    db_session.commit()

    # Create ArrestSurrender
    arrest = ArrestSurrender(
        CaseMasterID=case.id,
        ArrestSurrenderTypeID=1,
        ArrestSurrenderDate=date(2026, 4, 18),
        ArrestSurrenderStateId=state.id,
        ArrestSurrenderDistrictId=district.id,
        PoliceStationID=unit.id,
        IOID=employee.id,
        CourtID=court.id,
        AccusedMasterID=accused.id
    )
    db_session.add(arrest)
    db_session.commit()

    # Create junction Many-to-Many
    junction = InvArrestSurrenderAccused(ArrestSurrenderID=arrest.id, AccusedMasterID=accused.id)
    db_session.add(junction)
    db_session.commit()

    # Create ChargesheetDetails
    cs = ChargesheetDetails(
        CaseMasterID=case.id,
        csdate=datetime(2026, 5, 20, 10, 0, 0),
        cstype="A",
        PolicePersonID=employee.id
    )
    db_session.add(cs)
    db_session.commit()

    # Verify everything reads back cleanly
    fetched_case = db_session.query(CaseMaster).filter_by(CrimeNo="102140026202600045").first()
    assert fetched_case is not None
    assert float(fetched_case.occurrence_time.latitude) == pytest.approx(12.2958)
    assert float(fetched_case.occurrence_time.longitude) == pytest.approx(76.6394)
    assert fetched_case.complainants[0].ComplainantName == "Suresh"
    assert len(fetched_case.victims) == 1
    assert fetched_case.victims[0].VictimName == "Suresh"
    assert len(fetched_case.accused) == 1
    assert fetched_case.accused[0].AccusedName == "Unknown thief"
    assert len(fetched_case.act_sections) == 1
    assert fetched_case.act_sections[0].SectionCode == "379"
    assert len(fetched_case.arrest_surrenders) == 1
    assert fetched_case.arrest_surrenders[0].primary_accused.AccusedName == "Unknown thief"
    assert len(fetched_case.arrest_surrenders[0].all_accused) == 1
    assert len(fetched_case.chargesheets) == 1
    assert fetched_case.chargesheets[0].cstype == "A"
