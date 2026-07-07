import pytest
from datetime import date, datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.core.dataset_resolver import DatasetResolver
from backend.models import (
    Dataset, GenderMaster, NationalityMaster, BloodGroupMaster,
    CaseCategory, GravityOffence, CaseStatusMaster, CasteMaster, ReligionMaster, OccupationMaster,
    State, District, Court, UnitType, Unit, Rank, Designation, Employee,
    CaseMaster, Inv_OccuranceTime, ComplainantDetails, FIRVictim, Accused,
    ArrestSurrender, InvArrestSurrenderAccused, ChargesheetDetails,
    Act, Section, ActSectionAssociation, CrimeHead, CrimeSubHead, CrimeHeadActSection,
    AuditLog
)
from backend.repositories.fir_repository import FIRRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_dataset_resolver_with_fir_schema(db_session):
    resolver = DatasetResolver(db_session)
    
    # 1. Test standard default seeding behavior
    active_id = resolver.get_active_dataset_id()
    assert active_id is not None
    assert resolver.get_active_dataset_schema_type() == "legacy_crime_intel"

    # 2. Add an FIR dataset and set it to active
    ds_fir = Dataset(
        name="FIR_Seed",
        original_filename="fir_cases.csv",
        display_name="FIR Normalized 2026",
        source_type="CSV",
        status="Ready",
        is_active=True,
        schema_type="fir_normalized"
    )
    db_session.add(ds_fir)
    # Deactivate the old one to avoid conflict
    db_session.query(Dataset).filter(Dataset.id == active_id).update({Dataset.is_active: False})
    db_session.commit()

    assert resolver.get_active_dataset_id() == ds_fir.id
    assert resolver.get_active_dataset_schema_type() == "fir_normalized"
    assert resolver.get_dataset_schema_type(ds_fir.id) == "fir_normalized"


def test_fir_repository_crud_and_relationships(db_session):
    repo = FIRRepository(db_session)



    # 1. Setup basic lookup dictionaries
    gender = GenderMaster(name="Male")
    nationality = NationalityMaster(name="Indian")
    blood_group = BloodGroupMaster(name="O+")
    caste = CasteMaster(name="General")
    religion = ReligionMaster(name="Hindu")
    occupation = OccupationMaster(name="Officer")
    case_cat = CaseCategory(name="FIR")
    gravity = GravityOffence(name="Heinous")
    status_active = CaseStatusMaster(name="Under Investigation")

    db_session.add_all([gender, nationality, blood_group, caste, religion, occupation, case_cat, gravity, status_active])
    db_session.commit()

    # 2. Geography and Organization Setup
    state = State(name="Karnataka", NationalityID=nationality.id)
    db_session.add(state)
    db_session.commit()

    district = District(name="Bengaluru", StateID=state.id)
    db_session.add(district)
    db_session.commit()

    court = Court(name="High Court Bengaluru", DistrictID=district.id, StateID=state.id)
    unit_type = UnitType(name="Police Station", CityDistState="District")
    db_session.add_all([court, unit_type])
    db_session.commit()

    unit = Unit(name="Central PS", TypeID=unit_type.id, StateID=state.id, DistrictID=district.id, NationalityID=nationality.id)
    rank = Rank(name="Sub-Inspector")
    designation = Designation(name="SHO")
    db_session.add_all([unit, rank, designation])
    db_session.commit()

    employee = Employee(
        DistrictID=district.id,
        UnitID=unit.id,
        RankID=rank.id,
        DesignationID=designation.id,
        KGID="KA112233",
        FirstName="Raman",
        GenderID=gender.id
    )
    db_session.add(employee)
    db_session.commit()

    # 2.5 Add Dataset and Crime Heads
    dataset = Dataset(
        name="FIR_Seed_CRUD",
        original_filename="fir_cases.csv",
        display_name="FIR CRUD",
        source_type="CSV",
        status="Ready",
        is_active=True,
        schema_type="fir_normalized"
    )
    crime_head = CrimeHead(CrimeGroupName="Theft Group")
    db_session.add_all([dataset, crime_head])
    db_session.commit()

    crime_sub_head = CrimeSubHead(CrimeHeadID=crime_head.id, CrimeHeadName="Office Theft", SeqID=1)
    db_session.add(crime_sub_head)
    db_session.commit()

    # 3. Create Case
    case = repo.create_case(
        crime_no="123456789012345678",
        case_no="123456789",
        registered_date=date(2026, 7, 7),
        police_person_id=employee.id,
        police_station_id=unit.id,
        case_category_id=case_cat.id,
        gravity_offence_id=gravity.id,
        crime_major_head_id=crime_head.id,
        crime_minor_head_id=crime_sub_head.id,
        case_status_id=status_active.id,
        court_id=court.id,
        brief_facts="Theft of office assets.",
        dataset_id=dataset.id,
        incident_from_date=datetime(2026, 7, 6, 10, 0),
        incident_to_date=datetime(2026, 7, 6, 12, 0),
        info_received_ps_date=datetime(2026, 7, 7, 9, 0),
        latitude=12.9716,
        longitude=77.5946,
        performed_by_user_id=None
    )

    # Assert creation & 1:1 occurrence mapping
    assert case.id is not None
    assert case.CrimeNo == "123456789012345678"
    assert case.occurrence_time is not None
    assert float(case.occurrence_time.latitude) == pytest.approx(12.9716)

    # 4. Add transactional children and verify audit logging
    accused = repo.add_accused_to_case(
        case_id=case.id,
        name="Thief A",
        age=30,
        gender_id=gender.id,
        person_id="A1",
        performed_by_user_id=None
    )
    victim = repo.add_victim_to_case(
        case_id=case.id,
        name="Officer B",
        age=45,
        gender_id=gender.id,
        victim_police="1",
        performed_by_user_id=None
    )
    complainant = repo.add_complainant_to_case(
        case_id=case.id,
        name="Reporter C",
        age=35,
        occupation_id=occupation.id,
        religion_id=religion.id,
        caste_id=caste.id,
        gender_id=gender.id,
        performed_by_user_id=None
    )

    assert accused.id is not None
    assert victim.id is not None
    assert complainant.id is not None

    # Verify audit logs are bypassed when user_id is None
    audit_logs = db_session.query(AuditLog).order_by(AuditLog.created_at.asc()).all()
    assert len(audit_logs) == 0

    # 5. Fetch Case Eagerly
    fetched_case = repo.get_case_by_id(case.id)
    assert fetched_case is not None
    assert len(fetched_case.complainants) == 1
    assert fetched_case.complainants[0].ComplainantName == "Reporter C"
    assert len(fetched_case.victims) == 1
    assert fetched_case.victims[0].VictimName == "Officer B"
    assert len(fetched_case.accused) == 1
    assert fetched_case.accused[0].AccusedName == "Thief A"


def test_fir_repository_list_and_filters(db_session):
    repo = FIRRepository(db_session)

    # Set up basic structure
    nationality = NationalityMaster(name="Indian")
    gender = GenderMaster(name="Male")
    case_cat = CaseCategory(name="FIR")
    gravity = GravityOffence(name="Heinous")
    status_active = CaseStatusMaster(name="Under Investigation")
    db_session.add_all([nationality, gender, case_cat, gravity, status_active])
    db_session.commit()

    state = State(name="Karnataka", NationalityID=nationality.id)
    db_session.add(state)
    db_session.commit()

    district1 = District(name="Bengaluru", StateID=state.id)
    district2 = District(name="Mysuru", StateID=state.id)
    db_session.add_all([district1, district2])
    db_session.commit()

    unit_type = UnitType(name="Police Station")
    db_session.add(unit_type)
    db_session.commit()

    unit1 = Unit(name="Central PS", TypeID=unit_type.id, StateID=state.id, DistrictID=district1.id)
    unit2 = Unit(name="Devaraja PS", TypeID=unit_type.id, StateID=state.id, DistrictID=district2.id)
    db_session.add_all([unit1, unit2])
    db_session.commit()

    court = Court(name="High Court", DistrictID=district1.id, StateID=state.id)
    rank = Rank(name="Inspector")
    designation = Designation(name="SHO")
    db_session.add_all([court, rank, designation])
    db_session.commit()

    employee = Employee(DistrictID=district1.id, UnitID=unit1.id, RankID=rank.id, DesignationID=designation.id, KGID="KA001", FirstName="A", GenderID=gender.id)
    db_session.add(employee)
    db_session.commit()

    # Add Dataset and Crime Heads
    dataset = Dataset(
        name="FIR_Seed_List",
        original_filename="fir_cases.csv",
        display_name="FIR List",
        source_type="CSV",
        status="Ready",
        is_active=True,
        schema_type="fir_normalized"
    )
    crime_head = CrimeHead(CrimeGroupName="Theft Group")
    db_session.add_all([dataset, crime_head])
    db_session.commit()

    crime_sub_head = CrimeSubHead(CrimeHeadID=crime_head.id, CrimeHeadName="House Theft", SeqID=1)
    db_session.add(crime_sub_head)
    db_session.commit()

    # Create two cases, one in Bengaluru and one in Mysuru
    repo.create_case(
        crime_no="1", case_no="1", registered_date=date(2026, 7, 1),
        police_person_id=employee.id, police_station_id=unit1.id,
        case_category_id=case_cat.id, gravity_offence_id=gravity.id,
        crime_major_head_id=crime_head.id, crime_minor_head_id=crime_sub_head.id, case_status_id=status_active.id,
        court_id=court.id, dataset_id=dataset.id,
        incident_from_date=datetime(2026, 7, 1, 10, 0), info_received_ps_date=datetime(2026, 7, 1, 12, 0)
    )

    repo.create_case(
        crime_no="2", case_no="2", registered_date=date(2026, 7, 5),
        police_person_id=employee.id, police_station_id=unit2.id,
        case_category_id=case_cat.id, gravity_offence_id=gravity.id,
        crime_major_head_id=crime_head.id, crime_minor_head_id=crime_sub_head.id, case_status_id=status_active.id,
        court_id=court.id, dataset_id=dataset.id,
        incident_from_date=datetime(2026, 7, 5, 10, 0), info_received_ps_date=datetime(2026, 7, 5, 12, 0)
    )

    # 1. List cases all
    cases, count = repo.list_cases(active_dataset_id=dataset.id)
    assert count == 2
    assert len(cases) == 2

    # 2. Filter by district (Bengaluru)
    cases_bgl, count_bgl = repo.list_cases(district_id=district1.id, active_dataset_id=dataset.id)
    assert count_bgl == 1
    assert cases_bgl[0].CrimeNo == "1"

    # 3. Filter by date range (from 2026-07-02 to 2026-07-06)
    cases_date, count_date = repo.list_cases(
        start_date=date(2026, 7, 2),
        end_date=date(2026, 7, 6),
        active_dataset_id=dataset.id
    )
    assert count_date == 1
    assert cases_date[0].CrimeNo == "2"


def test_cascade_restrict_on_case_master_deletion(db_session):
    repo = FIRRepository(db_session)

    # Set up basic elements
    nationality = NationalityMaster(name="Indian")
    gender = GenderMaster(name="Male")
    case_cat = CaseCategory(name="FIR")
    gravity = GravityOffence(name="Heinous")
    status_active = CaseStatusMaster(name="Under Investigation")
    db_session.add_all([nationality, gender, case_cat, gravity, status_active])
    db_session.commit()

    state = State(name="Karnataka", NationalityID=nationality.id)
    db_session.add(state)
    db_session.commit()

    district = District(name="Bengaluru", StateID=state.id)
    db_session.add(district)
    db_session.commit()

    unit_type = UnitType(name="Police Station")
    db_session.add(unit_type)
    db_session.commit()

    unit = Unit(name="Central PS", TypeID=unit_type.id, StateID=state.id, DistrictID=district.id)
    db_session.add(unit)
    db_session.commit()

    court = Court(name="High Court", DistrictID=district.id, StateID=state.id)
    rank = Rank(name="Inspector")
    designation = Designation(name="SHO")
    db_session.add_all([court, rank, designation])
    db_session.commit()

    employee = Employee(DistrictID=district.id, UnitID=unit.id, RankID=rank.id, DesignationID=designation.id, KGID="KA001", FirstName="A", GenderID=gender.id)
    db_session.add(employee)
    db_session.commit()

    # Add Dataset and Crime Heads
    dataset = Dataset(
        name="FIR_Seed_Cascade",
        original_filename="fir_cases.csv",
        display_name="FIR Cascade",
        source_type="CSV",
        status="Ready",
        is_active=True,
        schema_type="fir_normalized"
    )
    crime_head = CrimeHead(CrimeGroupName="Theft Group")
    db_session.add_all([dataset, crime_head])
    db_session.commit()

    crime_sub_head = CrimeSubHead(CrimeHeadID=crime_head.id, CrimeHeadName="House Theft", SeqID=1)
    db_session.add(crime_sub_head)
    db_session.commit()

    # Create Case
    case = repo.create_case(
        crime_no="1", case_no="1", registered_date=date(2026, 7, 1),
        police_person_id=employee.id, police_station_id=unit.id,
        case_category_id=case_cat.id, gravity_offence_id=gravity.id,
        crime_major_head_id=crime_head.id, crime_minor_head_id=crime_sub_head.id, case_status_id=status_active.id,
        court_id=court.id, dataset_id=dataset.id,
        incident_from_date=datetime(2026, 7, 1, 10, 0), info_received_ps_date=datetime(2026, 7, 1, 12, 0)
    )

    # 1. When deleted without transactional children, CaseMaster and its Inv_OccuranceTime CASCADE delete successfully
    db_session.delete(case)
    db_session.commit()

    assert db_session.query(CaseMaster).filter_by(id=case.id).first() is None
    assert db_session.query(Inv_OccuranceTime).filter_by(CaseMasterID=case.id).first() is None

    # Re-create case and add a child entity (Accused)
    case_new = repo.create_case(
        crime_no="1", case_no="1", registered_date=date(2026, 7, 1),
        police_person_id=employee.id, police_station_id=unit.id,
        case_category_id=case_cat.id, gravity_offence_id=gravity.id,
        crime_major_head_id=crime_head.id, crime_minor_head_id=crime_sub_head.id, case_status_id=status_active.id,
        court_id=court.id, dataset_id=dataset.id,
        incident_from_date=datetime(2026, 7, 1, 10, 0), info_received_ps_date=datetime(2026, 7, 1, 12, 0)
    )
    
    repo.add_accused_to_case(case_id=case_new.id, name="Accused A", gender_id=gender.id)
    
    # 2. Deleting CaseMaster should raise an integrity error due to foreign key restrictions
    with pytest.raises(IntegrityError):
        db_session.delete(case_new)
        db_session.commit()
    
    db_session.rollback()
