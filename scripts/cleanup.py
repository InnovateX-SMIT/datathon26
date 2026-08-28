import os
import sys
import sqlite3

def get_db_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    candidates = [
        os.path.join(root_dir, "backend", "crime_intel.db"),
        os.path.join(root_dir, "crime_intel.db"),
        "backend/crime_intel.db",
        "crime_intel.db"
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

def main():
    db_path = get_db_path()
    if not db_path:
        print("Database crime_intel.db not found in root or backend directories.")
        return

    print(f"Cleaning database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = set(r[0] for r in cursor.fetchall())

        target_tables = [
            "alerts",
            "recommendations",
            "reports",
            "audit_logs",
            "recommendation_history",
            "resource_allocations",
            "dataset_configs",
            "complainant_details",
            "act_section_association",
            "victim",
            "accused",
            "arrest_surrender",
            "chargesheet_details",
            "inv_occurance_time",
            "inv_arrestsurrenderaccused",
            "case_master",
            "crime_events",
            "criminals",
            "victims",
            "crime_participation",
            "datasets"
        ]

        for table in target_tables:
            if table in existing_tables:
                cursor.execute(f"DELETE FROM {table}")

        conn.commit()
        print("Database tables cleaned successfully.")

        print("Optimizing database size via VACUUM...")
        cursor.execute("VACUUM")
        conn.commit()
        print("Database optimized.")

    except Exception as e:
        print(f"Error cleaning database: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

    print("Clearing disk caches...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)

    upload_paths = [
        os.path.join(root_dir, "datasets", "uploaded"),
        os.path.join(root_dir, "backend", "datasets", "uploaded"),
        os.path.join(root_dir, "datasets", "models"),
        os.path.join(root_dir, "backend", "datasets", "models")
    ]
    for path in upload_paths:
        if os.path.exists(path):
            for f in os.listdir(path):
                if f != ".gitkeep":
                    file_p = os.path.join(path, f)
                    try:
                        if os.path.isfile(file_p):
                            os.remove(file_p)
                    except Exception as err:
                        print(f"Error deleting file {f} from {path}: {err}")

    print("Disk caches cleared successfully.")

if __name__ == "__main__":
    main()

