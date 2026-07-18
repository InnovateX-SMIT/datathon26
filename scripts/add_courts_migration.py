import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crime_intel.db")
print(f"Connecting to database at {db_path}...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Fetch all active districts
    cursor.execute("SELECT DistrictID, DistrictName, StateID FROM district WHERE active = 1")
    districts = cursor.fetchall()
    print(f"Found {len(districts)} active districts.")

    courts_to_add = ["District Court", "Tribunal Court", "High Court"]
    total_added = 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Add the three courts for each district
    for dist_id, dist_name, state_id in districts:
        for court_name in courts_to_add:
            # Check if this court already exists for this district
            cursor.execute(
                "SELECT CourtID FROM court WHERE CourtName = ? AND DistrictID = ? AND StateID = ?",
                (court_name, dist_id, state_id)
            )
            res = cursor.fetchone()
            if not res:
                cursor.execute(
                    "INSERT INTO court (DistrictID, StateID, sort_order, CourtName, active, created_at, updated_at) VALUES (?, ?, 0, ?, 1, ?, ?)",
                    (dist_id, state_id, court_name, now_str, now_str)
                )
                total_added += 1

    conn.commit()
    print(f"Migration completed successfully! Added {total_added} court records.")
except Exception as e:
    conn.rollback()
    print(f"Migration failed: {e}")
finally:
    conn.close()
