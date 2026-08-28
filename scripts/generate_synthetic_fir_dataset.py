import os
import random
import csv
from datetime import datetime, timedelta

def generate_dataset(output_path: str, num_records: int = 5000):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    categories = ["FIR", "UDR", "PAR", "Zero FIR"]
    gravities = ["Heinous", "Non-Heinous"]
    case_statuses = ["Under Investigation", "Chargesheet Filed", "Report Beece (B-Report)", "Undetected"]
    states = ["Karnataka"]
    
    districts_courts = [
        ("Bengaluru Urban", "Principal City Civil & Sessions Court, Bengaluru", "Bengaluru City PS", 13.0, 77.6),
        ("Bengaluru Rural", "Bengaluru Rural District & Sessions Court", "Bengaluru Rural PS", 13.3, 77.5),
        ("Mysuru", "Mysuru District & Sessions Court", "Saraswathipuram PS", 12.3, 76.6),
        ("Mangaluru", "Dakshina Kannada District & Sessions Court", "Mangaluru Town PS", 12.9, 74.8),
        ("Belagavi", "Belagavi District & Sessions Court", "Belagavi City PS", 15.8, 74.5),
        ("Hubballi-Dharwad", "Dharwad District & Sessions Court", "Dharwad Town PS", 15.4, 75.0),
        ("Kalaburagi", "Kalaburagi District & Sessions Court", "Kalaburagi City PS", 17.3, 76.8),
        ("Ballari", "Ballari District & Sessions Court", "Ballari City PS", 15.1, 76.9),
        ("Udupi", "Udupi District & Sessions Court", "Udupi Town PS", 13.3, 74.7),
        ("Tumakuru", "Tumakuru District & Sessions Court", "Tumakuru Town PS", 13.3, 77.1),
        ("Shivamogga", "Shivamogga District & Sessions Court", "Shivamogga Town PS", 13.9, 75.5),
        ("Hassan", "Hassan District & Sessions Court", "Hassan Town PS", 13.0, 76.1),
        ("Mandya", "Mandya District & Sessions Court", "Mandya Town PS", 12.5, 76.9),
        ("Vijayapura", "Vijayapura District & Sessions Court", "Vijayapura Town PS", 16.8, 75.7),
        ("Bidar", "Bidar District & Sessions Court", "Bidar Town PS", 17.9, 77.5)
    ]

    ranks = ["Constable", "Head Constable", "Sub-Inspector", "Inspector", "Deputy Superintendent"]
    designations = ["Investigating Officer", "SHO", "Circle Inspector", "Station Writer"]
    genders = ["Male", "Female", "Transgender"]
    blood_groups = ["A Positive", "B Positive", "O Positive", "AB Positive", "A Negative", "B Negative", "O Negative", "AB Negative"]

    crime_heads = [
        ("Cyber Crime", "Cyber Crime", "ITA", "Information Technology Act, 2000", "IT Act", "66C", "Identity theft using computer resource"),
        ("Cyber Crime", "Dark Web Crime", "ITA", "Information Technology Act, 2000", "IT Act", "67", "Publishing/transmitting obscene material electronically"),
        ("Cyber Crime", "Cryptocurrency Crime", "ITA", "Information Technology Act, 2000", "IT Act", "66D", "Cheating by personation using a computer resource"),
        ("Property Crimes", "Theft", "IPC", "Indian Penal Code", "IPC", "379", "Punishment for theft"),
        ("Property Crimes", "Robbery", "IPC", "Indian Penal Code", "IPC", "392", "Punishment for robbery"),
        ("Crimes Against Body", "Murder", "IPC", "Indian Penal Code", "IPC", "302", "Punishment for murder"),
        ("Crimes Against Body", "Assault", "IPC", "Indian Penal Code", "IPC", "351", "Assault"),
        ("Financial Crime", "Money Laundering", "PMLA", "Prevention of Money Laundering Act, 2002", "PMLA", "3", "Offence of money laundering"),
        ("Narcotics", "Drug Offence", "NDPS", "Narcotic Drugs and Psychotropic Substances Act, 1985", "NDPS", "20", "Punishment for cannabis-related offences")
    ]

    first_names = ["Aarav", "Aditi", "Ananya", "Bhavya", "Chirag", "Dev", "Divya", "Esha", "Farhan", "Gautam", "Hari", "Isha", "Kavya", "Manish", "Nikhil", "Pooja", "Rahul", "Siddharth", "Tanvi", "Vikram"]
    last_names = ["Sharma", "Verma", "Rao", "Patil", "Gowda", "Kulkarni", "Nair", "Deshmukh", "Joshi", "Shetty", "Bhat", "Hegde", "Reddy", "Kumar", "Singh", "Das"]

    headers = [
        "case_category", "gravity_offence", "case_status", "state", "district", "court",
        "unit_type", "unit", "officer_kgid", "officer_name", "officer_rank", "officer_designation",
        "officer_dob", "officer_gender", "officer_blood_group", "officer_physically_challenged",
        "officer_appointment_date", "crime_no", "case_no", "registered_date", "brief_facts",
        "incident_from_date", "incident_to_date", "info_received_date", "latitude", "longitude",
        "occurrence_brief_facts", "crime_group_name", "crime_head_name", "act_code", "act_description",
        "short_name", "section_code", "section_description", "act_order", "section_order",
        "complainant_name", "complainant_age", "complainant_occupation", "complainant_religion",
        "complainant_caste", "complainant_gender", "victim_name", "victim_age", "victim_gender",
        "victim_police", "accused_name", "accused_age", "accused_gender", "accused_person_id",
        "arrest_type", "arrest_date", "arrest_state", "arrest_district", "arrest_station",
        "arrest_io_kgid", "arrest_court", "arrest_primary_accused_name", "arrest_joint_accused_names",
        "chargesheet_date", "chargesheet_type", "chargesheet_officer_kgid"
    ]

    base_date = datetime(2022, 1, 1)
    
    rows = []
    case_counter = 1
    
    while len(rows) < num_records:
        district_name, court_name, station_name, base_lat, base_lng = random.choice(districts_courts)
        cat = random.choice(categories)
        cat_code = 1 if cat == "FIR" else (2 if cat == "UDR" else (3 if cat == "PAR" else 8))
        dist_code = random.randint(1000, 9999)
        unit_code = random.randint(1000, 9999)
        year = random.choice([2022, 2023, 2024, 2025, 2026])
        seq = case_counter
        
        crime_no = f"{cat_code}{dist_code}{unit_code}{year}{seq:05d}"
        case_no = f"{year}{seq:05d}"
        case_counter += 1
        
        reg_dt = base_date + timedelta(days=random.randint(0, 1400), hours=random.randint(0, 23))
        inc_from = reg_dt - timedelta(days=random.randint(1, 5), hours=random.randint(1, 12))
        inc_to = inc_from + timedelta(hours=random.randint(1, 8))
        info_rcvd = inc_from + timedelta(hours=random.randint(2, 24))
        
        c_group, c_head, act_code, act_desc, act_short, sec_code, sec_desc = random.choice(crime_heads)
        
        officer_kgid = f"KA{random.randint(10000, 99999)}"
        officer_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Determine number of accused per case (1 to 3) to test multi-row FIR cases
        num_accused = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        accused_list = []
        for i in range(num_accused):
            a_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            a_age = random.choice([random.randint(18, 75), None])
            a_gender = random.choice(genders)
            a_id = f"A{i+1}"
            accused_list.append((a_name, a_age, a_gender, a_id))
            
        primary_accused_name = accused_list[0][0]
        joint_accused_names = ",".join([a[0] for a in accused_list[1:]]) if num_accused > 1 else ""
        
        status = random.choice(case_statuses)
        cs_date = (reg_dt + timedelta(days=random.randint(15, 60))).strftime("%Y-%m-%dT%H:%M:%S") if status == "Chargesheet Filed" else ""
        cs_type = random.choice(["A", "B", "C"]) if status == "Chargesheet Filed" else ""
        
        lat = round(base_lat + random.uniform(-0.08, 0.08), 4)
        lng = round(base_lng + random.uniform(-0.08, 0.08), 4)
        
        comp_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        comp_age = random.randint(21, 80)
        
        vic_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        vic_age = random.randint(5, 75)
        
        for idx, (a_name, a_age, a_gender, a_id) in enumerate(accused_list):
            is_first = (idx == 0)
            row = {
                "case_category": cat,
                "gravity_offence": random.choice(gravities),
                "case_status": status,
                "state": "Karnataka",
                "district": district_name,
                "court": court_name,
                "unit_type": "Police Station",
                "unit": station_name,
                "officer_kgid": officer_kgid,
                "officer_name": officer_name,
                "officer_rank": random.choice(ranks),
                "officer_designation": random.choice(designations),
                "officer_dob": f"{random.randint(1970, 1998)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "officer_gender": random.choice(["Male", "Female"]),
                "officer_blood_group": random.choice(blood_groups),
                "officer_physically_challenged": random.choice([0, 0, 0, 1]),
                "officer_appointment_date": f"{random.randint(2000, 2020)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "crime_no": crime_no,
                "case_no": case_no,
                "registered_date": reg_dt.strftime("%Y-%m-%d"),
                "brief_facts": f"On {inc_from.strftime('%d-%m-%Y')}, a case of {c_head} was reported at {station_name}, {district_name} district.",
                "incident_from_date": inc_from.strftime("%Y-%m-%dT%H:%M:%S"),
                "incident_to_date": inc_to.strftime("%Y-%m-%dT%H:%M:%S"),
                "info_received_date": info_rcvd.strftime("%Y-%m-%dT%H:%M:%S"),
                "latitude": str(lat),
                "longitude": str(lng),
                "occurrence_brief_facts": f"Incident occurred near coordinates {lat}, {lng} within jurisdiction of {station_name}.",
                "crime_group_name": c_group,
                "crime_head_name": c_head,
                "act_code": act_code,
                "act_description": act_desc,
                "short_name": act_short,
                "section_code": sec_code,
                "section_description": sec_desc,
                "act_order": 1,
                "section_order": 1,
                "complainant_name": comp_name if is_first else "",
                "complainant_age": str(comp_age) if is_first else "",
                "complainant_occupation": "Private Employee" if is_first else "",
                "complainant_religion": "Hindu" if is_first else "",
                "complainant_caste": "General" if is_first else "",
                "complainant_gender": random.choice(genders) if is_first else "",
                "victim_name": vic_name if is_first else "",
                "victim_age": str(vic_age) if is_first else "",
                "victim_gender": random.choice(genders) if is_first else "",
                "victim_police": "0",
                "accused_name": a_name,
                "accused_age": str(a_age) if a_age else "",
                "accused_gender": a_gender,
                "accused_person_id": a_id,
                "arrest_type": "1.0" if is_first and status != "Undetected" else "",
                "arrest_date": (reg_dt + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S") if is_first and status != "Undetected" else "",
                "arrest_state": "Karnataka" if is_first and status != "Undetected" else "",
                "arrest_district": district_name if is_first and status != "Undetected" else "",
                "arrest_station": station_name if is_first and status != "Undetected" else "",
                "arrest_io_kgid": officer_kgid if is_first and status != "Undetected" else "",
                "arrest_court": court_name if is_first and status != "Undetected" else "",
                "arrest_primary_accused_name": primary_accused_name if is_first and status != "Undetected" else "",
                "arrest_joint_accused_names": joint_accused_names if is_first and status != "Undetected" else "",
                "chargesheet_date": cs_date if is_first else "",
                "chargesheet_type": cs_type if is_first else "",
                "chargesheet_officer_kgid": officer_kgid if is_first and status == "Chargesheet Filed" else ""
            }
            rows.append(row)
            if len(rows) >= num_records:
                break
                
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated synthetic test dataset with {len(rows)} rows at '{output_path}'.")

if __name__ == "__main__":
    generate_dataset("datasets/datasets_final/karnataka_crime_synthetic_5k.csv", num_records=5000)
