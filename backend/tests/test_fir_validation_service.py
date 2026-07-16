import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.core.validation import (
    validate_crime_no, validate_case_no, generate_crime_no, generate_case_no,
    validate_latitude, validate_longitude, validate_age
)
from backend.services.fir_service import FIRService
from backend.schemas.fir import (
    CaseMasterCreate, InvOccuranceTimeCreate, ComplainantDetailsCreate,
    FIRVictimCreate, AccusedCreate, ActSectionAssociationCreate,
    ArrestSurrenderCreate, ChargesheetDetailsCreate
)
from backend.models import (
    GenderMaster, NationalityMaster, BloodGroupMaster,
    CaseCategory, GravityOffence, CaseStatusMaster, CasteMaster, ReligionMaster, OccupationMaster,
    State, District, Court, UnitType, Unit, Rank, Designation, Employee, Act, Section, CrimeHead, CrimeSubHead,
    Accused, ArrestSurrender, InvArrestSurrenderAccused
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    # Setup testing database
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_centralized_validation_helpers():
    # 1. CrimeNo Validation
    assert validate_crime_no("102140026202600045") is True
    assert validate_crime_no("102140026189900045") is False  # Invalid year 1899
    assert validate_crime_no("10214002620260004") is False   # Less than 18 digits
    assert validate_crime_no("1021400262026000456") is False # Greater than 18 digits
    assert validate_crime_no("102140026202a00045") is False  # Non-numeric
    
    # 2. CaseNo Validation
    assert validate_case_no("202600045") is True
    assert validate_case_no("189900045") is False  # Invalid year
    assert validate_case_no("20260004") is False   # Less than 9 digits
    assert validate_case_no("2026000456") is False # Greater than 9 digits
    assert validate_case_no("202a00045") is False  # Non-numeric

    # 3. Generation
    generated = generate_crime_no(category=1, district=214, station=26, year=2026, serial=45)
    assert generated == "102140026202600045"
    assert generate_case_no(generated) == "202600045"

    with pytest.raises(ValueError):
        generate_crime_no(category=12, district=214, station=26, year=2026, serial=45)  # Invalid category
    with pytest.raises(ValueError):
        generate_crime_no(category=1, district=214, station=26, year=1899, serial=45)  # Invalid year
    with pytest.raises(ValueError):
        generate_case_no("invalid")

    # 4. Lat/Lon Validation
    assert validate_latitude(12.2958) is True
    assert validate_latitude(95.0) is False
    assert validate_latitude(-95.0) is False
    assert validate_longitude(76.6394) is True
    assert validate_longitude(185.0) is False
    assert validate_longitude(-185.0) is False

    # 5. Age Validation
    assert validate_age(35) is True
    assert validate_age(-1) is False
    assert validate_age(130) is False



def test_fir_service_crud_and_validations(db_session):
    # 1. Setup lookups
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

    # 2. Instantiate Service
    fir_service = FIRService(db_session)

    # 3. Create Valid CaseMaster DTO
    case_create = CaseMasterCreate(
        CrimeNo=None,  # test autogeneration
        CaseNo=None,
        CrimeRegisteredDate=date(2026, 4, 15),
        PolicePersonID=employee.id,
        PoliceStationID=unit.id,
        CaseCategoryID=case_cat.id,
        GravityOffenceID=gravity.id,
        CrimeMajorHeadID=crime_head.id,
        CrimeMinorHeadID=crime_sub_head.id,
        CaseStatusID=case_status.id,
        CourtID=court.id,
        BriefFacts="House theft registered",
        occurrence_time=InvOccuranceTimeCreate(
            IncidentFromDate=datetime(2026, 4, 14, 22, 0, 0),
            IncidentToDate=datetime(2026, 4, 14, 23, 30, 0),
            InfoReceivedPSDate=datetime(2026, 4, 15, 8, 30, 0),
            latitude=12.2958,
            longitude=76.6394,
            BriefFacts="Break-in detail"
        ),
        complainants=[
            ComplainantDetailsCreate(
                ComplainantName="Suresh",
                AgeYear=40,
                OccupationID=occupation.id,
                ReligionID=religion.id,
                CasteID=caste.id,
                GenderID=gender.id
            )
        ],
        victims=[
            FIRVictimCreate(
                VictimName="Ramesh",
                AgeYear=38,
                GenderID=gender.id,
                VictimPolice="0"
            )
        ],
        accused=[
            AccusedCreate(
                AccusedName="Stolen Raju",
                AgeYear=28,
                GenderID=gender.id,
                PersonID="A1"
            )
        ],
        act_sections=[
            ActSectionAssociationCreate(
                ActCode="IPC",
                SectionCode="379"
            )
        ],
        arrest_surrenders=[
            ArrestSurrenderCreate(
                ArrestSurrenderTypeID=1,
                ArrestSurrenderDate=date(2026, 4, 16),
                ArrestSurrenderStateId=state.id,
                ArrestSurrenderDistrictId=district.id,
                PoliceStationID=unit.id,
                IOID=employee.id,
                CourtID=court.id,
                AccusedMasterID=0  # references accused[0] (Stolen Raju)
            )
        ],
        chargesheets=[
            ChargesheetDetailsCreate(
                csdate=datetime(2026, 4, 20, 10, 0, 0),
                cstype="A",
                PolicePersonID=employee.id
            )
        ]
    )

    # Execution
    response = fir_service.create_case(case_create)
    
    # Assertions
    assert response.id is not None
    assert response.CrimeNo == "100010001202600001"  # autogenerated category=1, district=1, station=1, year=2026, serial=1
    assert response.CaseNo == "202600001"
    
    assert response.occurrence_time is not None
    assert response.occurrence_time.latitude == 12.2958
    assert len(response.complainants) == 1
    assert response.complainants[0].ComplainantName == "Suresh"
    assert len(response.victims) == 1
    assert response.victims[0].VictimName == "Ramesh"
    assert len(response.accused) == 1
    assert response.accused[0].AccusedName == "Stolen Raju"
    assert len(response.arrest_surrenders) == 1
    assert response.arrest_surrenders[0].associated_accused_ids == [response.accused[0].id]
    assert len(response.chargesheets) == 1
    assert response.chargesheets[0].cstype == "A"

    # Test coordinate validation failure
    case_create.occurrence_time.latitude = 100.0
    with pytest.raises(ValueError, match="Invalid latitude"):
        fir_service.create_case(case_create)
    case_create.occurrence_time.latitude = 12.2958

    # Test age validation failure
    case_create.accused[0].AgeYear = 130
    with pytest.raises(ValueError, match="Invalid accused age"):
        fir_service.create_case(case_create)
    case_create.accused[0].AgeYear = 28

    # Test duplicate check failure
    case_create.CrimeNo = "100010001202600001"
    with pytest.raises(ValueError, match="Duplicate Case"):
        fir_service.create_case(case_create)
