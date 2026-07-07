import os
import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.models import (
    Dataset, CaseMaster, Accused, FIRVictim, ComplainantDetails, ArrestSurrender,
    Inv_OccuranceTime, ChargesheetDetails, ActSectionAssociation
)
from backend.core.dataset_resolver import DatasetResolver
from backend.services.dataset_service import DatasetService
from backend.services.fir_synthetic_generator import FIRSyntheticDataGenerator
from backend.services.fir_import_service import FIRImportService
from backend.repositories.fir_repository import FIRRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
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

def test_schema_detection_and_validation():
    db = None # Not needed for pure parsing/validation tests
    importer = FIRImportService(db=None)
    
    # 1. Schema detection
    fir_cols = ["crime_no", "registered_date", "act_code", "section_code", "unit", "district", "state"]
    legacy_cols = ["district", "police_station", "crime_date", "crime_type"]
    
    assert importer.detect_schema_type(fir_cols) == "fir_normalized"
    assert importer.detect_schema_type(legacy_cols) == "legacy_crime_intel"
    assert importer.detect_schema_type(["random", "column"]) == "legacy_crime_intel"

    # 2. Validation warnings on missing columns
    rows = [{"some_col": "val"}]
    errors = importer.validate_rows(rows)
    assert any("Missing required schema columns" in err for err in errors)

    # 3. Validation on invalid coordinates
    rows_bad_coords = [{
        "crime_no": "100010001202600001",
        "registered_date": "2026-04-15",
        "unit": "Devaraja PS",
        "act_code": "IPC",
        "section_code": "379",
        "district": "Mysuru",
        "state": "Karnataka",
        "latitude": 120.0,  # Invalid
        "longitude": 77.0
    }]
    errors = importer.validate_rows(rows_bad_coords)
    assert any("Latitude 120.0 is out of bounds" in err for err in errors)

    # 4. Validation on invalid age bounds
    rows_bad_age = [{
        "crime_no": "100010001202600001",
        "registered_date": "2026-04-15",
        "unit": "Devaraja PS",
        "act_code": "IPC",
        "section_code": "379",
        "district": "Mysuru",
        "state": "Karnataka",
        "complainant_age": -5  # Invalid
    }]
    errors = importer.validate_rows(rows_bad_age)
    assert any("complainant_age' -5 is out of bounds" in err for err in errors)

    # 5. Validation on invalid CrimeNo structure (needs to be 18 digits)
    rows_bad_crimeno = [{
        "crime_no": "12345",  # Invalid
        "registered_date": "2026-04-15",
        "unit": "Devaraja PS",
        "act_code": "IPC",
        "section_code": "379",
        "district": "Mysuru",
        "state": "Karnataka"
    }]
    errors = importer.validate_rows(rows_bad_crimeno)
    assert any("does not conform to the 18-digit official spec" in err for err in errors)


def test_generator_configurability_and_export():
    generator = FIRSyntheticDataGenerator()
    
    # Configurable limits
    limit_small = 5
    limit_large = 15
    
    rows_small = generator.generate(num_records=limit_small)
    rows_large = generator.generate(num_records=limit_large)
    
    # Since cases can contain multiple accused/victims (flattened),
    # count distinct generated crime_nos
    distinct_crime_nos_small = {r["crime_no"] for r in rows_small}
    distinct_crime_nos_large = {r["crime_no"] for r in rows_large}
    
    assert len(distinct_crime_nos_small) == limit_small
    assert len(distinct_crime_nos_large) == limit_large

    # Configurable output paths
    csv_path = "backend/tests/scratch/synthetic_test.csv"
    excel_path = "backend/tests/scratch/synthetic_test.xlsx"
    
    # Clear prior
    for path in [csv_path, excel_path]:
        if os.path.exists(path):
            os.remove(path)
            
    generator.generate_and_export(csv_path, excel_path, num_records=3)
    
    assert os.path.exists(csv_path)
    assert os.path.exists(excel_path)
    
    # Clean up files
    for path in [csv_path, excel_path]:
        if os.path.exists(path):
            os.remove(path)
            
    # Clean up scratch dir if empty
    scratch_dir = "backend/tests/scratch"
    if os.path.exists(scratch_dir) and not os.listdir(scratch_dir):
        os.rmdir(scratch_dir)


def test_end_to_end_ingestion_pipeline(db_session):
    # Setup services
    ds_service = DatasetService(db_session)
    generator = FIRSyntheticDataGenerator()
    
    # 1. Generate and export temporary test files
    csv_file = "backend/tests/scratch_e2e_fir.csv"
    excel_file = "backend/tests/scratch_e2e_fir.xlsx"
    
    generator.generate_and_export(csv_file, excel_file, num_records=10)
    
    try:
        # 2. Ingest CSV file bytes
        with open(csv_file, "rb") as f:
            csv_bytes = f.read()
            
        dataset_csv = ds_service.import_dataset(
            display_name="Synthetic E2E CSV",
            description="Relational CSV Ingestion Test",
            file_name="scratch_e2e_fir.csv",
            file_bytes=csv_bytes,
            user_id=None
        )
        
        # Verify dataset registration
        assert dataset_csv.id is not None
        assert dataset_csv.schema_type == "fir_normalized"
        assert dataset_csv.status == "Ready"
        assert dataset_csv.row_count == 10
        
        # Verify active status activation
        assert dataset_csv.is_active is True
        
        # 3. Verify in-memory resolver compatibility
        resolver = DatasetResolver(db_session)
        assert resolver.get_active_dataset_id() == dataset_csv.id
        assert resolver.get_active_dataset_schema_type() == "fir_normalized"

        # 4. Query repository layer to verify relational entities
        repo = FIRRepository(db_session)
        cases, count = repo.list_cases(active_dataset_id=dataset_csv.id)
        assert count == 10
        assert len(cases) == 10
        
        # Validate details of first case
        first_case = repo.get_case_by_id(cases[0].id)
        assert first_case is not None
        assert first_case.occurrence_time is not None
        assert len(first_case.complainants) >= 1
        assert len(first_case.victims) >= 1
        assert len(first_case.accused) >= 1
        assert len(first_case.arrest_surrenders) >= 1

        # 5. Ingest Excel file bytes and check duplicate rejection
        with open(excel_file, "rb") as f:
            excel_bytes = f.read()
            
        with pytest.raises(ValueError, match="already been uploaded"):
            ds_service.import_dataset(
                display_name="Synthetic E2E Excel",
                description="Relational Excel Ingestion Test",
                file_name="scratch_e2e_fir.csv", # Duplicate filename check
                file_bytes=excel_bytes,
                user_id=None
            )

        # Clear existing cases and child records to allow Excel import to insert 10 cases again
        db_session.query(Inv_OccuranceTime).delete()
        db_session.query(ComplainantDetails).delete()
        db_session.query(FIRVictim).delete()
        db_session.query(Accused).delete()
        db_session.query(ArrestSurrender).delete()
        db_session.query(ChargesheetDetails).delete()
        db_session.query(ActSectionAssociation).delete()
        db_session.query(CaseMaster).delete()
        db_session.commit()

        # Successful import under new name
        dataset_excel = ds_service.import_dataset(
            display_name="Synthetic E2E Excel",
            description="Relational Excel Ingestion Test",
            file_name="scratch_e2e_fir_new.xlsx",
            file_bytes=excel_bytes,
            user_id=None
        )
        
        assert dataset_excel.id is not None
        assert dataset_excel.schema_type == "fir_normalized"
        assert dataset_excel.status == "Ready"
        assert dataset_excel.row_count == 10
        
        # Verify activation switch (excel becomes active, csv deactivated)
        db_session.refresh(dataset_csv)
        assert dataset_excel.is_active is True
        assert dataset_csv.is_active is False
        
        # Verify repo lists cases for the active excel dataset
        cases_xls, count_xls = repo.list_cases(active_dataset_id=dataset_excel.id)
        assert count_xls == 10

    finally:
        # Clean up temporary test files
        for path in [csv_file, excel_file]:
            if os.path.exists(path):
                os.remove(path)
        scratch_dir = "backend/tests"
        # Remove generated files inside datasets/uploaded too to keep it clean
        import shutil
        if os.path.exists("datasets/uploaded"):
            shutil.rmtree("datasets/uploaded")
