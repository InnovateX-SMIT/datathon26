import csv
from sqlalchemy.orm import Session
from backend.models.location import Location
from backend.models.police_station import PoliceStation

def seed_police_stations(db: Session, csv_path: str = "datasets/processed/police_stations.csv"):
    if db.query(PoliceStation).first() is not None:
        print("Police Stations already seeded.")
        return

    # Map districts to location IDs
    locations = db.query(Location).all()
    district_to_loc_id = {loc.district: loc.id for loc in locations}

    stations_to_insert = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dist = row["district"]
            loc_id = district_to_loc_id.get(dist)

            station = PoliceStation(
                station_name=row["station_name"],
                district=dist,
                beat=row["beat"],
                location_id=loc_id,
                officer_count=int(row["officer_count"]),
                vehicle_count=int(row["vehicle_count"]),
                equipment_count=int(row["equipment_count"]),
                capacity=int(row["capacity"]),
                availability=row["availability"]
            )
            stations_to_insert.append(station)

    batch_size = 1000
    for i in range(0, len(stations_to_insert), batch_size):
        chunk = stations_to_insert[i:i+batch_size]
        db.bulk_save_objects(chunk)
        db.commit()
        print(f"Logged: Seeded police stations batch {i // batch_size + 1}")

    print("Police Stations Seeded")
