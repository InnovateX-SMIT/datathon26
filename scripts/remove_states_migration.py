import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crime_intel.db")
print(f"Connecting to database at {db_path}...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Deactivate Tamil Nadu (1) and Maharashtra (2)
    cursor.execute("UPDATE state SET active = 0 WHERE StateName IN ('Tamil Nadu', 'Maharashtra')")
    print(f"Deactivated states. Rows affected: {cursor.rowcount}")

    # 2. Re-assign districts with StateID 1 or 2 to Karnataka (StateID 3)
    cursor.execute("UPDATE district SET StateID = 3 WHERE StateID IN (1, 2)")
    print(f"Migrated districts to Karnataka. Rows affected: {cursor.rowcount}")

    # 3. Re-assign courts with StateID 1 or 2 to Karnataka (StateID 3)
    cursor.execute("UPDATE court SET StateID = 3 WHERE StateID IN (1, 2)")
    print(f"Migrated courts to Karnataka. Rows affected: {cursor.rowcount}")

    # 4. Re-assign units with StateID 1 or 2 to Karnataka (StateID 3)
    cursor.execute("UPDATE unit SET StateID = 3 WHERE StateID IN (1, 2)")
    print(f"Migrated units to Karnataka. Rows affected: {cursor.rowcount}")

    # 5. Re-assign arrest records with StateID 1 or 2 to Karnataka (StateID 3)
    cursor.execute("UPDATE arrest_surrender SET ArrestSurrenderStateId = 3 WHERE ArrestSurrenderStateId IN (1, 2)")
    print(f"Migrated arrest surrender records to Karnataka. Rows affected: {cursor.rowcount}")

    conn.commit()
    print("Migration completed successfully!")
except Exception as e:
    conn.rollback()
    print(f"Migration failed: {e}")
finally:
    conn.close()
