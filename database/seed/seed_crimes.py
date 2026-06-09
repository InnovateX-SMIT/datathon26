import csv
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.location import Location
from backend.models.police_station import PoliceStation
from backend.models.crime import CrimeEvent
from backend.models.victim import Victim
from backend.models.criminal import Criminal
from backend.models.crime_participation import CrimeParticipation

def seed_crimes(db: Session, csv_path: str = "datasets/processed/crime_events.csv"):
    if db.query(CrimeEvent).first() is not None:
        print("Crimes already seeded.")
        return

    print("Resolving location and station mappings...")
    locations = db.query(Location).all()
    district_to_loc_id = {loc.district: loc.id for loc in locations}

    stations = db.query(PoliceStation).all()
    station_to_station_id = {s.station_name: s.id for s in stations}

    first_names = ["Amit", "Rahul", "Vijay", "Sanjay", "Anil", "Sunil", "Rajesh", "Prakash", "Kiran", "Ramesh", "Deepak", "Suresh", "Priya", "Sunita", "Anita", "Geeta"]
    last_names = ["Kumar", "Sharma", "Singh", "Patil", "Gowda", "Reddy", "Nair", "Joshi", "Das", "Mehta", "Sen", "Rao", "Patel", "Chatterjee", "Mukherjee", "Pillai"]
    castes = ["General", "OBC", "SC", "ST"]

    print("Reading crime events CSV...")
    rows = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total_records = len(rows)
    batch_size = 1000
    print(f"Seeding {total_records} crimes in batches of {batch_size}...")

    for i in range(0, total_records, batch_size):
        batch_rows = rows[i:i+batch_size]
        
        # Batch insert collections
        crime_events = []
        victim_infos = []
        criminal_infos = []

        for idx, row in enumerate(batch_rows):
            global_idx = i + idx
            dist = row["district"]
            ps = row["police_station"]

            loc_id = district_to_loc_id.get(dist)
            ps_id = station_to_station_id.get(ps)

            # Parse date and time
            date_obj = datetime.strptime(row["crime_date"], "%Y-%m-%d").date()
            time_obj = None
            if row["crime_time"]:
                try:
                    time_obj = datetime.strptime(row["crime_time"], "%H:%M").time()
                except ValueError:
                    time_obj = None

            # Create CrimeEvent model
            crime = CrimeEvent(
                crime_type=row["crime_type"],
                crime_category=row["crime_type"],
                crime_subcategory=f"{row['crime_type']} - Subcategory",
                description=f"{row['crime_type']} incident registered under {row['fir_id']}",
                severity=float(row["severity"]) if row["severity"] else 1.0,
                status=row["status"],
                crime_date=date_obj,
                crime_time=time_obj,
                location_id=loc_id,
                police_station_id=ps_id,
                victim_count=1,
                accused_count=1
            )
            crime_events.append(crime)

            # Prepare Victim and Criminal details (to be created after CrimeEvent IDs are obtained)
            v_age = float(row["victim_age"]) if row["victim_age"] else None
            c_age = float(row["accused_age"]) if row["accused_age"] else None
            gender = row["gender"]
            occ = row["occupation"]

            # Deterministic names and castes
            c_name = f"{first_names[global_idx % len(first_names)]} {last_names[(global_idx * 3) % len(last_names)]}"
            c_caste = castes[global_idx % len(castes)]
            risk_score = 0.85 if row["repeat_offender"] == "1" else 0.15

            victim_infos.append({
                "gender": gender,
                "age": v_age,
                "occupation": occ,
                "location_id": loc_id
            })

            criminal_infos.append({
                "name": c_name,
                "gender": gender,  # assume matching or similar demographic row
                "age": c_age,
                "occupation": occ,
                "caste": c_caste,
                "risk_score": risk_score,
                "status": "accused" if row["status"] != "Closed" else "convicted"
            })

        # Add crime events and flush to populate IDs
        db.add_all(crime_events)
        db.flush()

        # Add victims and criminals
        criminals = []
        victims = []
        for idx, crime in enumerate(crime_events):
            c_info = criminal_infos[idx]
            criminal = Criminal(
                name=c_info["name"],
                gender=c_info["gender"],
                age=c_info["age"],
                occupation=c_info["occupation"],
                caste=c_info["caste"],
                risk_score=c_info["risk_score"],
                status=c_info["status"]
            )
            criminals.append(criminal)

            v_info = victim_infos[idx]
            victim = Victim(
                crime_event_id=crime.id,
                gender=v_info["gender"],
                age=v_info["age"],
                occupation=v_info["occupation"],
                location_id=v_info["location_id"]
            )
            victims.append(victim)

        db.add_all(criminals)
        db.flush()

        # Add CrimeParticipation bridge
        participations = []
        for idx, crime in enumerate(crime_events):
            criminal = criminals[idx]
            participation = CrimeParticipation(
                crime_event_id=crime.id,
                criminal_id=criminal.id,
                role="principal accused"
            )
            participations.append(participation)

        db.add_all(victims + participations)
        db.commit()

        if (i + batch_size) % 5000 == 0 or (i + batch_size) >= total_records:
            print(f"Logged: Seeded crimes progress: {min(i + batch_size, total_records)}/{total_records}")

    print("Crimes Seeded")
