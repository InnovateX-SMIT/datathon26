"""
import_normalized_tables.py
============================
Imports the 31 normalized CSV tables from ClaudeForTheProject/normalized_tables/out/
into the operational CrimeNexus database (SQLite/PostgreSQL) in strict FK dependency order.

Usage:
    python scripts/import_normalized_tables.py
"""

import os
import sys
import pandas as pd
from sqlalchemy import text

# Ensure backend package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    # Level 0: Master tables (no FK dependencies)
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


def import_normalized_data():
    print("Initializing CrimeNexus Database Schema...")
    Base.metadata.create_all(bind=engine)
    migrate_database_schema(engine)
    
    db = SessionLocal()
    try:
        # Ensure default Dataset record exists for dataset_id=1
        ds = db.query(Dataset).filter(Dataset.id == 1).first()
        if not ds:
            print("Creating default active Dataset (ID=1) for normalized FIR data...")
            ds = Dataset(
                id=1,
                name="karnataka_crime_intel",
                original_filename="karnataka_crime_dataset_10k_compliant.csv",
                display_name="Karnataka Crime Dataset (10K Normalized)",
                description="Official Karnataka FIR compliant 10K dataset normalized across 31 relational tables.",
                row_count=5078,
                column_count=62,
                status="Ready",
                upload_status="Completed",
                is_active=True,
                schema_type="fir_normalized"
            )
            db.add(ds)
            db.commit()
        else:
            ds.is_active = True
            ds.schema_type = "fir_normalized"
            db.commit()

        print(f"Reading normalized tables from: {NORMALIZED_DIR}")
        with engine.begin() as conn:
            for csv_file, table_name, extra in TABLE_IMPORT_SPECS:
                file_path = os.path.join(NORMALIZED_DIR, csv_file)
                if not os.path.exists(file_path):
                    print(f"  [SKIP] File not found: {csv_file}")
                    continue
                
                df = pd.read_csv(file_path)
                
                # Apply column remapping if required
                if "column_remap" in extra:
                    df = df.rename(columns=extra["column_remap"])
                    
                # Add default column values if specified
                for col_name, col_val in extra.items():
                    if col_name != "column_remap" and col_name not in df.columns:
                        df[col_name] = col_val

                # Get table columns from DB schema
                db_cols_info = conn.execute(text(f"PRAGMA table_info('{table_name}')")).fetchall()
                db_cols = {col[1] for col in db_cols_info}
                
                # Ensure mixin defaults if required by DB schema
                if "sort_order" in db_cols and "sort_order" not in df.columns:
                    df["sort_order"] = 0
                if "active" in db_cols and "active" not in df.columns:
                    df["active"] = 1
                if "created_at" in db_cols and "created_at" not in df.columns:
                    df["created_at"] = pd.Timestamp.now()
                if "updated_at" in db_cols and "updated_at" not in df.columns:
                    df["updated_at"] = pd.Timestamp.now()

                # Keep only columns that exist in the DB schema
                valid_cols = [c for c in df.columns if c in db_cols]
                df = df[valid_cols]

                # Fill default values for NOT NULL boolean columns if null
                if "IsComplainantAccused" in df.columns:
                    df["IsComplainantAccused"] = df["IsComplainantAccused"].fillna(0).astype(int)
                if "IsAccused" in df.columns:
                    df["IsAccused"] = df["IsAccused"].fillna(1).astype(int)
                if "PhysicallyChallenged" in df.columns:
                    df["PhysicallyChallenged"] = df["PhysicallyChallenged"].fillna(0).astype(int)

                # Clean NaN values for integer/nullable FK columns
                df = df.where(pd.notnull(df), None)

                # Check current count in table
                existing_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                if existing_count >= len(df):
                    print(f"  [EXISTS] {table_name}: {existing_count} rows already present. Skipping.")
                    continue

                # Truncate table if partially filled to prevent duplicate key conflicts
                if existing_count > 0:
                    print(f"  [CLEAR] Clearing {existing_count} rows from {table_name} before clean import...")
                    conn.execute(text(f"DELETE FROM {table_name}"))

                # Write dataframe to SQL
                df.to_sql(name=table_name, con=conn, if_exists="append", index=False)
                new_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                print(f"  [IMPORTED] {table_name}: {new_count} rows imported successfully.")

        print("\nAll normalized tables imported successfully!")
        
    finally:
        db.close()


def run_validation_queries():
    print("\n" + "="*60)
    print("RUNNING POST-IMPORT VALIDATION CHECKS")
    print("="*60)
    
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
    
    with engine.connect() as conn:
        all_passed = True
        print("\n1. Orphan Checks (Expect 0 bad rows):")
        for check_label, sql_query in orphan_queries:
            bad_count = conn.execute(text(sql_query)).scalar()
            status = "PASS (0)" if bad_count == 0 else f"FAIL ({bad_count})"
            if bad_count > 0:
                all_passed = False
            print(f"  - {check_label:35s}: {status}")

        print("\n2. Core Row-Count Reconciliation:")
        expected_counts = [
            ("case_master", 5078),
            ("inv_occurance_time", 5078),
            ("complainant_details", 5078),
            ("victim", 6993),
            ("accused", 8870),
            ("act_section_association", 5078),
            ("arrest_surrender", 2271),
            ("inv_arrestsurrenderaccused", 3122),
            ("chargesheet_details", 1522),
        ]
        
        for table_name, expected in expected_counts:
            actual = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            status = "MATCH" if actual == expected else f"MISMATCH (got {actual})"
            if actual != expected:
                all_passed = False
            print(f"  - {table_name:35s}: {actual:5d} / {expected:5d} ({status})")

        print("\n" + "="*60)
        if all_passed:
            print("VALIDATION SUMMARY: 100% CLEAN / ALL CHECKS PASSED!")
        else:
            print("VALIDATION SUMMARY: DISCREPANCIES DETECTED!")
        print("="*60 + "\n")


if __name__ == "__main__":
    import_normalized_data()
    run_validation_queries()
