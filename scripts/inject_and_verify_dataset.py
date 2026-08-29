"""
inject_and_verify_dataset.py
============================
1. Generates the 'New Karnataka Crime Synthetic Dataset (15K)'.
2. Imports the 31 normalized tables into SQLite (backend/crime_intel.db).
3. Registers/activates the dataset in the 'dataset' registry table.
4. Executes validation checks ensuring 100% clean foreign key integrity.

Usage:
    python scripts/inject_and_verify_dataset.py
"""

import os
import sys
import pandas as pd
from sqlalchemy import text

# Ensure backend package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_master_synthetic_dataset import generate_synthetic_dataset
from backend.core.database import engine, SessionLocal, Base
from backend.app.main import migrate_database_schema
from backend.models import Dataset

NORMALIZED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ClaudeForTheProject",
    "normalized_tables",
    "out"
)

# FK dependency order: Level 0 -> Level 5
TABLE_IMPORT_SPECS = [
    # Level 0: Master tables
    ("GenderMaster.csv", "gender_master", {}),
    ("BloodGroupMaster.csv", "blood_group_master", {}),
    ("ArrestSurrenderTypeMaster.csv", "arrest_surrender_type_master", {}),
    ("CasteMaster.csv", "caste_master", {}),
    ("ReligionMaster.csv", "religion_master", {}),
    ("OccupationMaster.csv", "occupation_master", {}),
    ("CaseCategory.csv", "case_category", {}),
    ("GravityOffence.csv", "gravity_offence", {}),
    ("CaseStatusMaster.csv", "case_status_master", {}),
    ("State.csv", "state", {}),
    ("UnitType.csv", "unit_type", {}),
    ("Rank.csv", "rank", {}),
    ("Designation.csv", "designation", {}),
    ("Act.csv", "act", {}),
    
    # Level 1: First-tier dependent masters
    ("District.csv", "district", {}),
    ("Court.csv", "court", {}),
    ("Section.csv", "section", {}),
    ("CrimeHead.csv", "crime_head", {}),
    
    # Level 2: Second-tier dependent masters
    ("Unit.csv", "unit", {}),
    ("CrimeSubHead.csv", "crime_sub_head", {}),
    ("CrimeHeadActSection.csv", "crime_head_act_section", {}),
    
    # Level 3: Employees & Case Master
    ("Employee.csv", "employee", {}),
    ("CaseMaster.csv", "case_master", {"dataset_id": 1}),
    
    # Level 4: Case Detail & Dependent Entities
    ("Inv_OccuranceTime.csv", "inv_occurance_time", {}),
    ("ComplainantDetails.csv", "complainant_details", {}),
    ("Victim.csv", "victim", {}),
    ("Accused.csv", "accused", {}),
    ("ActSectionAssociation.csv", "act_section_association", {"column_remap": {"ActID": "ActCode", "SectionID": "SectionCode"}}),
    ("ChargesheetDetails.csv", "chargesheet_details", {}),
    
    # Level 5: Arrest & Junction Proceedings
    ("ArrestSurrender.csv", "arrest_surrender", {}),
    ("inv_arrestsurrenderaccused.csv", "inv_arrestsurrenderaccused", {}),
]


def run_full_pipeline(num_rows: int = 15000):
    print("=" * 70)
    print(f"STEP 1: GENERATING NEW SYNTHETIC DATASET ({num_rows} CASES)")
    print("=" * 70)
    csv_file_path = generate_synthetic_dataset(num_cases=num_rows)

    print("\n" + "=" * 70)
    print("STEP 2: INITIALIZING DATABASE & INGESTING 31 NORMALIZED TABLES")
    print("=" * 70)
    
    Base.metadata.create_all(bind=engine)
    migrate_database_schema(engine)

    db = SessionLocal()
    try:
        # Register or update dataset active record
        ds = db.query(Dataset).filter(Dataset.id == 1).first()
        file_size_b = os.path.getsize(csv_file_path) if os.path.exists(csv_file_path) else 0
        
        if not ds:
            print("Creating default active Dataset (ID=1) for new synthetic dataset...")
            ds = Dataset(
                id=1,
                name="new_karnataka_crime_synthetic_15k",
                original_filename="new_karnataka_crime_synthetic_dataset_15k.csv",
                display_name="New Karnataka Crime Synthetic Dataset (15K)",
                description="New synthetic dataset containing 15,000 cases normalized across 31 relational tables.",
                row_count=num_rows,
                column_count=62,
                file_size=file_size_b,
                status="Ready",
                upload_status="Completed",
                is_active=True,
                schema_type="fir_normalized"
            )
            db.add(ds)
            db.commit()
        else:
            ds.name = "new_karnataka_crime_synthetic_15k"
            ds.original_filename = "new_karnataka_crime_synthetic_dataset_15k.csv"
            ds.display_name = "New Karnataka Crime Synthetic Dataset (15K)"
            ds.row_count = num_rows
            ds.file_size = file_size_b
            ds.is_active = True
            ds.status = "Ready"
            ds.upload_status = "Completed"
            ds.schema_type = "fir_normalized"
            db.commit()

        print(f"Importing normalized tables into SQLite DB at: '{engine.url.database}'")
        
        with engine.begin() as conn:
            # First clear operational tables to allow clean batch re-ingestion
            clear_tables = [
                "inv_arrestsurrenderaccused", "arrest_surrender", "chargesheet_details",
                "act_section_association", "accused", "victim", "complainant_details",
                "inv_occurance_time", "case_master", "employee", "crime_head_act_section",
                "crime_sub_head", "unit", "crime_head", "section", "court", "district",
                "act", "designation", "rank", "unit_type", "state", "case_status_master",
                "gravity_offence", "case_category", "occupation_master", "religion_master",
                "caste_master", "arrest_surrender_type_master", "blood_group_master", "gender_master"
            ]
            for t_name in clear_tables:
                try:
                    conn.execute(text(f"DELETE FROM {t_name}"))
                except Exception:
                    pass

            for csv_file, table_name, extra in TABLE_IMPORT_SPECS:
                file_path = os.path.join(NORMALIZED_DIR, csv_file)
                if not os.path.exists(file_path):
                    print(f"  [SKIP] File not found: {csv_file}")
                    continue
                
                df = pd.read_csv(file_path)
                
                if "column_remap" in extra:
                    df = df.rename(columns=extra["column_remap"])
                    
                for col_name, col_val in extra.items():
                    if col_name != "column_remap" and col_name not in df.columns:
                        df[col_name] = col_val

                db_cols_info = conn.execute(text(f"PRAGMA table_info('{table_name}')")).fetchall()
                db_cols = {col[1] for col in db_cols_info}
                
                if "sort_order" in db_cols and "sort_order" not in df.columns:
                    df["sort_order"] = 0
                if "active" in db_cols and "active" not in df.columns:
                    df["active"] = 1
                if "created_at" in db_cols and "created_at" not in df.columns:
                    df["created_at"] = pd.Timestamp.now()
                if "updated_at" in db_cols and "updated_at" not in df.columns:
                    df["updated_at"] = pd.Timestamp.now()

                valid_cols = [c for c in df.columns if c in db_cols]
                df = df[valid_cols]

                if "IsComplainantAccused" in df.columns:
                    df["IsComplainantAccused"] = df["IsComplainantAccused"].fillna(0).astype(int)
                if "IsAccused" in df.columns:
                    df["IsAccused"] = df["IsAccused"].fillna(1).astype(int)
                if "PhysicallyChallenged" in df.columns:
                    df["PhysicallyChallenged"] = df["PhysicallyChallenged"].fillna(0).astype(int)

                df = df.where(pd.notnull(df), None)

                df.to_sql(name=table_name, con=conn, if_exists="append", index=False)
                new_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                print(f"  [IMPORTED] {table_name:30s}: {new_count:6d} rows")

        print("\n" + "=" * 70)
        print("STEP 3: RUNNING POST-IMPORT VALIDATION & INTEGRITY CHECKS")
        print("=" * 70)
        
        orphan_queries = [
            ("Orphan Victim rows", "SELECT COUNT(*) FROM victim v LEFT JOIN case_master c ON v.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL"),
            ("Orphan Accused rows", "SELECT COUNT(*) FROM accused a LEFT JOIN case_master c ON a.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL"),
            ("Orphan Complainant rows", "SELECT COUNT(*) FROM complainant_details cd LEFT JOIN case_master c ON cd.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL"),
            ("Orphan ArrestSurrender rows", "SELECT COUNT(*) FROM arrest_surrender ar LEFT JOIN case_master c ON ar.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL"),
            ("Orphan Arrest Accused FK", "SELECT COUNT(*) FROM arrest_surrender ar LEFT JOIN accused a ON ar.AccusedMasterID = a.AccusedMasterID WHERE ar.AccusedMasterID IS NOT NULL AND a.AccusedMasterID IS NULL"),
            ("Orphan Arrest Junction rows", "SELECT COUNT(*) FROM inv_arrestsurrenderaccused j LEFT JOIN arrest_surrender ar ON j.ArrestSurrenderID = ar.ArrestSurrenderID LEFT JOIN accused a ON j.AccusedMasterID = a.AccusedMasterID WHERE ar.ArrestSurrenderID IS NULL OR a.AccusedMasterID IS NULL"),
            ("Orphan Chargesheet rows", "SELECT COUNT(*) FROM chargesheet_details cs LEFT JOIN case_master c ON cs.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL"),
            ("Orphan ActSection rows", "SELECT COUNT(*) FROM act_section_association asa LEFT JOIN case_master c ON asa.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL"),
            ("Orphan OccuranceTime rows", "SELECT COUNT(*) FROM inv_occurance_time o LEFT JOIN case_master c ON o.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL"),
        ]
        
        all_passed = True
        with engine.connect() as conn:
            print("\n1. Orphan Checks (Expect 0 bad rows):")
            for check_label, sql_query in orphan_queries:
                bad_count = conn.execute(text(sql_query)).scalar()
                status = "PASS (0)" if bad_count == 0 else f"FAIL ({bad_count})"
                if bad_count > 0:
                    all_passed = False
                print(f"  - {check_label:35s}: {status}")

            print("\n2. Database Summary Row Counts:")
            check_tables = [
                "case_master", "inv_occurance_time", "complainant_details",
                "victim", "accused", "act_section_association",
                "arrest_surrender", "inv_arrestsurrenderaccused", "chargesheet_details"
            ]
            for t_name in check_tables:
                actual = conn.execute(text(f"SELECT COUNT(*) FROM {t_name}")).scalar()
                print(f"  - {t_name:35s}: {actual:6d} rows")

        print("\n" + "=" * 70)
        if all_passed:
            print("PIPELINE COMPLETE: 100% CLEAN / ALL CHECKS PASSED!")
            print(f"Flat CSV File Path: {csv_file_path}")
            print(f"Database File Path: {engine.url.database}")
        else:
            print("PIPELINE SUMMARY: DISCREPANCIES DETECTED!")
        print("=" * 70 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_full_pipeline(num_rows=15000)
