import csv
from sqlalchemy.orm import Session
from backend.models.location import Location

def seed_locations(db: Session, csv_path: str = "datasets/processed/locations.csv"):
    if db.query(Location).first() is not None:
        print("Locations already seeded.")
        return

    locations_to_insert = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc = Location(
                state=row["state"],
                district=row["district"],
                latitude=float(row["latitude"]) if row["latitude"] else None,
                longitude=float(row["longitude"]) if row["longitude"] else None
            )
            locations_to_insert.append(loc)

    batch_size = 1000
    for i in range(0, len(locations_to_insert), batch_size):
        chunk = locations_to_insert[i:i+batch_size]
        db.bulk_save_objects(chunk)
        db.commit()
        print(f"Logged: Seeded locations batch {i // batch_size + 1}")

    print("Locations Seeded")
