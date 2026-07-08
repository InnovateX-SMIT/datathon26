import os
import sys
import sqlite3

def main():
    db_path = "crime_intel.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    print("Cleaning database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Delete predictions, recommendations, alerts, reports, models, audit logs, and histories
        cursor.execute("DELETE FROM ml_models")
        cursor.execute("DELETE FROM predictions")
        cursor.execute("DELETE FROM alerts")
        cursor.execute("DELETE FROM recommendations")
        cursor.execute("DELETE FROM reports")
        cursor.execute("DELETE FROM audit_logs")
        cursor.execute("DELETE FROM recommendation_history")

        # Completely truncate dataset-scoped tables so the next upload starts from a clean slate.
        cursor.execute("DELETE FROM complainant_details")
        cursor.execute("DELETE FROM act_section_association")
        cursor.execute("DELETE FROM victim")
        cursor.execute("DELETE FROM accused")
        cursor.execute("DELETE FROM arrest_surrender")
        cursor.execute("DELETE FROM chargesheet_details")
        cursor.execute("DELETE FROM inv_occurance_time")
        cursor.execute("DELETE FROM inv_arrestsurrenderaccused")
        cursor.execute("DELETE FROM case_master")
        cursor.execute("DELETE FROM crime_events")
        cursor.execute("DELETE FROM criminals")
        cursor.execute("DELETE FROM victims")
        cursor.execute("DELETE FROM crime_participation")
        cursor.execute("DELETE FROM datasets")

        conn.commit()
        print("Database tables cleaned successfully.")

        # Shrink database file size
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

    # Clear uploaded folder caches
    print("Clearing disk caches...")
    upload_paths = ["datasets/uploaded", "backend/datasets/uploaded"]
    for path in upload_paths:
        if os.path.exists(path):
            for f in os.listdir(path):
                if f != ".gitkeep":
                    try:
                        os.remove(os.path.join(path, f))
                    except Exception as err:
                        print(f"Error deleting file {f} from {path}: {err}")

    # Clear trained model caches
    model_paths = ["datasets/models", "backend/datasets/models"]
    for path in model_paths:
        if os.path.exists(path):
            for f in os.listdir(path):
                if f != ".gitkeep":
                    try:
                        os.remove(os.path.join(path, f))
                    except Exception as err:
                        print(f"Error deleting file {f} from {path}: {err}")

    print("Disk caches cleared successfully.")

if __name__ == "__main__":
    main()
