"""
generate_master_synthetic_dataset.py
=====================================
Generates the 'New Karnataka Crime Synthetic Dataset' (15,000 cases / rows)
strictly adhering to the 62 flat CSV schema headers and decomposing the data
into 31 normalized relational CSV tables for CrimeNexus / Police FIR schema.

Usage:
    python scripts/generate_master_synthetic_dataset.py --rows 15000
"""

import os
import sys
import random
import csv
import argparse
from datetime import datetime, timedelta
import pandas as pd

def generate_synthetic_dataset(num_cases: int = 15000, output_csv_path: str = None, normalized_out_dir: str = None):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if output_csv_path is None:
        output_csv_path = os.path.join(root_dir, "datasets", "datasets_final", "new_karnataka_crime_synthetic_dataset_15k.csv")
    
    if normalized_out_dir is None:
        normalized_out_dir = os.path.join(root_dir, "ClaudeForTheProject", "normalized_tables", "out")
        
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    os.makedirs(normalized_out_dir, exist_ok=True)

    print(f"Generating {num_cases} synthetic FIR cases for CrimeNexus platform...")

    categories = ["FIR", "UDR", "PAR", "Zero FIR"]
    gravities = ["Heinous", "Non-Heinous"]
    case_statuses = ["Under Investigation", "Chargesheet Filed", "Report Beece (B-Report)", "Undetected"]
    
    districts_courts = [
        ("Bengaluru Urban", "Principal City Civil & Sessions Court, Bengaluru", "Bengaluru City PS", 12.9716, 77.5946),
        ("Bengaluru Rural", "Bengaluru Rural District & Sessions Court", "Bengaluru Rural PS", 13.2846, 77.5534),
        ("Mysuru", "Mysuru District & Sessions Court", "Saraswathipuram PS", 12.2958, 76.6394),
        ("Mangaluru", "Dakshina Kannada District & Sessions Court", "Mangaluru Town PS", 12.9141, 74.8560),
        ("Belagavi", "Belagavi District & Sessions Court", "Belagavi City PS", 15.8497, 74.4977),
        ("Hubballi-Dharwad", "Dharwad District & Sessions Court", "Dharwad Town PS", 15.3647, 75.1240),
        ("Kalaburagi", "Kalaburagi District & Sessions Court", "Kalaburagi City PS", 17.3297, 76.8343),
        ("Ballari", "Ballari District & Sessions Court", "Ballari City PS", 15.1394, 76.9214),
        ("Udupi", "Udupi District & Sessions Court", "Udupi Town PS", 13.3409, 74.7421),
        ("Tumakuru", "Tumakuru District & Sessions Court", "Tumakuru Town PS", 13.3392, 77.1014),
        ("Shivamogga", "Shivamogga District & Sessions Court", "Shivamogga Town PS", 13.9299, 75.5681),
        ("Hassan", "Hassan District & Sessions Court", "Hassan Town PS", 13.0033, 76.1004),
        ("Mandya", "Mandya District & Sessions Court", "Mandya Town PS", 12.5218, 76.8951),
        ("Vijayapura", "Vijayapura District & Sessions Court", "Vijayapura Town PS", 16.8302, 75.7100),
        ("Bidar", "Bidar District & Sessions Court", "Bidar Town PS", 17.9104, 77.5199),
        ("Kolar", "Kolar District & Sessions Court", "Kolar Town PS", 13.1367, 78.1292),
        ("Chikkamagaluru", "Chikkamagaluru District & Sessions Court", "Chikkamagaluru PS", 13.3161, 75.7720),
        ("Davangere", "Davangere District & Sessions Court", "Davangere Extension PS", 14.4644, 75.9218),
        ("Bagalkote", "Bagalkote District & Sessions Court", "Bagalkote Town PS", 16.1852, 75.6961),
        ("Ramanagara", "Ramanagara District & Sessions Court", "Ramanagara Town PS", 12.7150, 77.2810)
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
        ("Property Crimes", "Burglary", "IPC", "Indian Penal Code", "IPC", "457", "Lurking house-trespass or house-breaking by night"),
        ("Crimes Against Body", "Murder", "IPC", "Indian Penal Code", "IPC", "302", "Punishment for murder"),
        ("Crimes Against Body", "Assault", "IPC", "Indian Penal Code", "IPC", "351", "Assault"),
        ("Crimes Against Body", "Grievous Hurt", "IPC", "Indian Penal Code", "IPC", "325", "Punishment for voluntarily causing grievous hurt"),
        ("Financial Crime", "Money Laundering", "PMLA", "Prevention of Money Laundering Act, 2002", "PMLA", "3", "Offence of money laundering"),
        ("Financial Crime", "Cheating", "IPC", "Indian Penal Code", "IPC", "420", "Cheating and dishonestly inducing delivery of property"),
        ("Narcotics", "Drug Offence", "NDPS", "Narcotic Drugs and Psychotropic Substances Act, 1985", "NDPS", "20", "Punishment for cannabis-related offences")
    ]

    first_names = ["Aarav", "Aditi", "Ananya", "Bhavya", "Chirag", "Dev", "Divya", "Esha", "Farhan", "Gautam", "Hari", "Isha", "Kavya", "Manish", "Nikhil", "Pooja", "Rahul", "Siddharth", "Tanvi", "Vikram", "Abhishek", "Deepak", "Kiran", "Meena", "Rajesh", "Suresh", "Priya", "Sanjay", "Anil", "Sunil"]
    last_names = ["Sharma", "Verma", "Rao", "Patil", "Gowda", "Kulkarni", "Nair", "Deshmukh", "Joshi", "Shetty", "Bhat", "Hegde", "Reddy", "Kumar", "Singh", "Das", "Naik", "Kamath", "Pai", "Shenoy"]

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
    
    while case_counter <= num_cases:
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
        
        # Determine number of accused per case (1 to 3)
        num_accused = random.choices([1, 2, 3], weights=[0.65, 0.25, 0.10])[0]
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

    print(f"Writing {len(rows)} flat rows to CSV: '{output_csv_path}'...")
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Successfully generated flat synthetic dataset CSV ({len(rows)} rows).")

    # Now decompose rows into 31 normalized tables
    print("Decomposing rows into 31 relational CSV tables...")
    decompose_to_normalized_csvs(rows, normalized_out_dir)
    return output_csv_path


def decompose_to_normalized_csvs(rows: list[dict], out_dir: str):
    df_flat = pd.DataFrame(rows)
    
    # 1. Master lookups
    gender_map = {"Male": 1, "Female": 2, "Transgender": 3}
    gender_master = pd.DataFrame([{"GenderID": v, "GenderName": k} for k, v in gender_map.items()])
    gender_master.to_csv(os.path.join(out_dir, "GenderMaster.csv"), index=False)

    blood_groups = ["A Positive", "B Positive", "O Positive", "AB Positive", "A Negative", "B Negative", "O Negative", "AB Negative"]
    blood_map = {bg: i+1 for i, bg in enumerate(blood_groups)}
    blood_master = pd.DataFrame([{"BloodGroupID": v, "BloodGroupName": k} for k, v in blood_map.items()])
    blood_master.to_csv(os.path.join(out_dir, "BloodGroupMaster.csv"), index=False)

    arrest_types = ["Arrested", "Surrendered"]
    arrest_type_map = {"1.0": 1, "2.0": 2, "1": 1, "2": 2}
    arrest_type_master = pd.DataFrame([{"ArrestSurrenderTypeID": 1, "TypeName": "Arrested"}, {"ArrestSurrenderTypeID": 2, "TypeName": "Surrendered"}])
    arrest_type_master.to_csv(os.path.join(out_dir, "ArrestSurrenderTypeMaster.csv"), index=False)

    caste_master = pd.DataFrame([{"caste_master_id": 1, "caste_master_name": "General"}, {"caste_master_id": 2, "caste_master_name": "OBC"}, {"caste_master_id": 3, "caste_master_name": "SC/ST"}])
    caste_master.to_csv(os.path.join(out_dir, "CasteMaster.csv"), index=False)
    caste_map = {"General": 1, "OBC": 2, "SC/ST": 3}

    religion_master = pd.DataFrame([{"ReligionID": 1, "ReligionName": "Hindu"}, {"ReligionID": 2, "ReligionName": "Muslim"}, {"ReligionID": 3, "ReligionName": "Christian"}])
    religion_master.to_csv(os.path.join(out_dir, "ReligionMaster.csv"), index=False)
    religion_map = {"Hindu": 1, "Muslim": 2, "Christian": 3}

    occ_master = pd.DataFrame([{"OccupationID": 1, "OccupationName": "Private Employee"}, {"OccupationID": 2, "OccupationName": "Business"}, {"OccupationID": 3, "OccupationName": "Farmer"}])
    occ_master.to_csv(os.path.join(out_dir, "OccupationMaster.csv"), index=False)
    occ_map = {"Private Employee": 1, "Business": 2, "Farmer": 3}

    cat_names = sorted(list(set(df_flat["case_category"].dropna())))
    cat_map = {name: i+1 for i, name in enumerate(cat_names)}
    case_category = pd.DataFrame([{"CaseCategoryID": v, "LookupValue": k} for k, v in cat_map.items()])
    case_category.to_csv(os.path.join(out_dir, "CaseCategory.csv"), index=False)

    grav_names = sorted(list(set(df_flat["gravity_offence"].dropna())))
    grav_map = {name: i+1 for i, name in enumerate(grav_names)}
    gravity_offence = pd.DataFrame([{"GravityOffenceID": v, "LookupValue": k} for k, v in grav_map.items()])
    gravity_offence.to_csv(os.path.join(out_dir, "GravityOffence.csv"), index=False)

    status_names = sorted(list(set(df_flat["case_status"].dropna())))
    status_map = {name: i+1 for i, name in enumerate(status_names)}
    case_status_master = pd.DataFrame([{"CaseStatusID": v, "CaseStatusName": k} for k, v in status_map.items()])
    case_status_master.to_csv(os.path.join(out_dir, "CaseStatusMaster.csv"), index=False)

    state = pd.DataFrame([{"StateID": 1, "StateName": "Karnataka", "NationalityID": 1, "Active": 1}])
    state.to_csv(os.path.join(out_dir, "State.csv"), index=False)

    unit_type = pd.DataFrame([{"UnitTypeID": 1, "UnitTypeName": "Police Station", "CityDistState": "District", "Hierarchy": 1, "Active": 1}])
    unit_type.to_csv(os.path.join(out_dir, "UnitType.csv"), index=False)

    rank_names = sorted(list(set(df_flat["officer_rank"].dropna())))
    rank_map = {name: i+1 for i, name in enumerate(rank_names)}
    rank_df = pd.DataFrame([{"RankID": v, "RankName": k, "Hierarchy": 1, "Active": 1} for k, v in rank_map.items()])
    rank_df.to_csv(os.path.join(out_dir, "Rank.csv"), index=False)

    desig_names = sorted(list(set(df_flat["officer_designation"].dropna())))
    desig_map = {name: i+1 for i, name in enumerate(desig_names)}
    desig_df = pd.DataFrame([{"DesignationID": v, "DesignationName": k, "Active": 1, "SortOrder": 1} for k, v in desig_map.items()])
    desig_df.to_csv(os.path.join(out_dir, "Designation.csv"), index=False)

    act_unique = df_flat[["act_code", "act_description", "short_name"]].drop_duplicates()
    act_df = pd.DataFrame({
        "ActCode": act_unique["act_code"],
        "ActDescription": act_unique["act_description"],
        "ShortName": act_unique["short_name"],
        "Active": 1
    })
    act_df.to_csv(os.path.join(out_dir, "Act.csv"), index=False)

    # 2. Level 1: Dependent masters
    dist_names = sorted(list(set(df_flat["district"].dropna())))
    dist_map = {name: i+1 for i, name in enumerate(dist_names)}
    dist_df = pd.DataFrame([{"DistrictID": v, "DistrictName": k, "StateID": 1, "Active": 1} for k, v in dist_map.items()])
    dist_df.to_csv(os.path.join(out_dir, "District.csv"), index=False)

    court_unique = df_flat[["court", "district"]].drop_duplicates()
    court_map = {}
    court_rows = []
    for i, (_, r) in enumerate(court_unique.iterrows()):
        c_id = i + 1
        court_map[r["court"]] = c_id
        court_rows.append({
            "CourtID": c_id,
            "CourtName": r["court"],
            "DistrictID": dist_map.get(r["district"], 1),
            "StateID": 1,
            "Active": 1
        })
    court_df = pd.DataFrame(court_rows)
    court_df.to_csv(os.path.join(out_dir, "Court.csv"), index=False)

    sec_unique = df_flat[["section_code", "act_code", "section_description"]].drop_duplicates()
    sec_df = pd.DataFrame({
        "SectionCode": sec_unique["section_code"],
        "ActCode": sec_unique["act_code"],
        "SectionDescription": sec_unique["section_description"],
        "Active": 1
    })
    sec_df.to_csv(os.path.join(out_dir, "Section.csv"), index=False)

    ch_names = sorted(list(set(df_flat["crime_group_name"].dropna())))
    ch_map = {name: i+1 for i, name in enumerate(ch_names)}
    ch_df = pd.DataFrame([{"CrimeHeadID": v, "CrimeGroupName": k, "Active": 1} for k, v in ch_map.items()])
    ch_df.to_csv(os.path.join(out_dir, "CrimeHead.csv"), index=False)

    # 3. Level 2: Dependent masters
    unit_unique = df_flat[["unit", "district"]].drop_duplicates()
    unit_map = {}
    unit_rows = []
    for i, (_, r) in enumerate(unit_unique.iterrows()):
        u_id = i + 1
        unit_map[r["unit"]] = u_id
        unit_rows.append({
            "UnitID": u_id,
            "UnitName": r["unit"],
            "TypeID": 1,
            "ParentUnit": None,
            "NationalityID": 1,
            "StateID": 1,
            "DistrictID": dist_map.get(r["district"], 1),
            "Active": 1
        })
    unit_df = pd.DataFrame(unit_rows)
    unit_df.to_csv(os.path.join(out_dir, "Unit.csv"), index=False)

    sub_unique = df_flat[["crime_head_name", "crime_group_name"]].drop_duplicates()
    sub_map = {}
    sub_rows = []
    for i, (_, r) in enumerate(sub_unique.iterrows()):
        sub_id = i + 1
        sub_map[r["crime_head_name"]] = sub_id
        sub_rows.append({
            "CrimeSubHeadID": sub_id,
            "CrimeHeadID": ch_map.get(r["crime_group_name"], 1),
            "CrimeHeadName": r["crime_head_name"],
            "SeqID": 1
        })
    sub_df = pd.DataFrame(sub_rows)
    sub_df.to_csv(os.path.join(out_dir, "CrimeSubHead.csv"), index=False)

    chas_unique = df_flat[["crime_group_name", "act_code", "section_code"]].drop_duplicates()
    chas_rows = []
    for _, r in chas_unique.iterrows():
        chas_rows.append({
            "CrimeHeadID": ch_map.get(r["crime_group_name"], 1),
            "ActCode": r["act_code"],
            "SectionCode": r["section_code"]
        })
    chas_df = pd.DataFrame(chas_rows)
    chas_df.to_csv(os.path.join(out_dir, "CrimeHeadActSection.csv"), index=False)

    # 4. Level 3: Employee & CaseMaster
    emp_unique = df_flat[["officer_kgid", "officer_name", "district", "unit", "officer_rank", "officer_designation", "officer_dob", "officer_gender", "officer_blood_group", "officer_physically_challenged", "officer_appointment_date"]].drop_duplicates(subset=["officer_kgid"])
    emp_map = {}
    emp_rows = []
    for i, (_, r) in enumerate(emp_unique.iterrows()):
        e_id = i + 1
        emp_map[r["officer_kgid"]] = e_id
        emp_rows.append({
            "EmployeeID": e_id,
            "DistrictID": dist_map.get(r["district"], 1),
            "UnitID": unit_map.get(r["unit"], 1),
            "RankID": rank_map.get(r["officer_rank"], 1),
            "DesignationID": desig_map.get(r["officer_designation"], 1),
            "KGID": r["officer_kgid"],
            "FirstName": r["officer_name"],
            "EmployeeDOB": r["officer_dob"],
            "GenderID": gender_map.get(r["officer_gender"], 1),
            "BloodGroupID": blood_map.get(r["officer_blood_group"], 1),
            "PhysicallyChallenged": r["officer_physically_challenged"],
            "AppointmentDate": r["officer_appointment_date"]
        })
    emp_df = pd.DataFrame(emp_rows)
    emp_df.to_csv(os.path.join(out_dir, "Employee.csv"), index=False)

    case_unique = df_flat.drop_duplicates(subset=["crime_no"])
    case_map = {}
    case_rows = []
    occur_rows = []
    comp_rows = []
    vic_rows = []
    act_sec_rows = []
    accused_rows = []
    arrest_rows = []
    arrest_junc_rows = []
    cs_rows = []

    accused_id_counter = 1
    victim_id_counter = 1
    comp_id_counter = 1
    arrest_id_counter = 1
    cs_id_counter = 1

    for i, (_, r) in enumerate(case_unique.iterrows()):
        cm_id = i + 1
        c_no = r["crime_no"]
        case_map[c_no] = cm_id
        
        case_rows.append({
            "CaseMasterID": cm_id,
            "CrimeNo": c_no,
            "CaseNo": r["case_no"],
            "CrimeRegisteredDate": r["registered_date"],
            "PolicePersonID": emp_map.get(r["officer_kgid"], 1),
            "PoliceStationID": unit_map.get(r["unit"], 1),
            "CaseCategoryID": cat_map.get(r["case_category"], 1),
            "GravityOffenceID": grav_map.get(r["gravity_offence"], 1),
            "CrimeMajorHeadID": ch_map.get(r["crime_group_name"], 1),
            "CrimeMinorHeadID": sub_map.get(r["crime_head_name"], 1),
            "CaseStatusID": status_map.get(r["case_status"], 1),
            "CourtID": court_map.get(r["court"], 1),
            "BriefFacts": r["brief_facts"]
        })

        occur_rows.append({
            "CaseMasterID": cm_id,
            "IncidentFromDate": r["incident_from_date"],
            "IncidentToDate": r["incident_to_date"],
            "InfoReceivedPSDate": r["info_received_date"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "OccurrenceBriefFacts": r["occurrence_brief_facts"]
        })

        if r["complainant_name"]:
            comp_rows.append({
                "ComplainantID": comp_id_counter,
                "CaseMasterID": cm_id,
                "ComplainantName": r["complainant_name"],
                "AgeYear": int(r["complainant_age"]) if r["complainant_age"] else None,
                "OccupationID": occ_map.get(r["complainant_occupation"], 1),
                "ReligionID": religion_map.get(r["complainant_religion"], 1),
                "CasteID": caste_map.get(r["complainant_caste"], 1),
                "GenderID": gender_map.get(r["complainant_gender"], 1)
            })
            comp_id_counter += 1

        if r["victim_name"]:
            vic_rows.append({
                "VictimMasterID": victim_id_counter,
                "CaseMasterID": cm_id,
                "VictimName": r["victim_name"],
                "AgeYear": int(r["victim_age"]) if r["victim_age"] else None,
                "GenderID": gender_map.get(r["victim_gender"], 1),
                "VictimPolice": int(r["victim_police"]) if r["victim_police"] else 0
            })
            victim_id_counter += 1

        act_sec_rows.append({
            "CaseMasterID": cm_id,
            "ActID": r["act_code"],
            "SectionID": r["section_code"],
            "ActOrderID": r["act_order"],
            "SectionOrderID": r["section_order"]
        })

        # All accused for this case
        case_accused_flat = df_flat[df_flat["crime_no"] == c_no]
        case_accused_ids = []
        primary_accused_master_id = None

        for idx, (_, a_row) in enumerate(case_accused_flat.iterrows()):
            a_master_id = accused_id_counter
            accused_id_counter += 1
            case_accused_ids.append(a_master_id)
            if idx == 0:
                primary_accused_master_id = a_master_id

            accused_rows.append({
                "AccusedMasterID": a_master_id,
                "CaseMasterID": cm_id,
                "AccusedName": a_row["accused_name"],
                "AgeYear": int(a_row["accused_age"]) if a_row["accused_age"] else None,
                "GenderID": gender_map.get(a_row["accused_gender"], 1),
                "PersonID": a_row["accused_person_id"]
            })

        if r["arrest_type"] and str(r["arrest_type"]).strip() != "":
            ar_id = arrest_id_counter
            arrest_id_counter += 1
            
            ar_type_val = arrest_type_map.get(str(r["arrest_type"]).strip(), 1)
            
            arrest_rows.append({
                "ArrestSurrenderID": ar_id,
                "CaseMasterID": cm_id,
                "ArrestSurrenderTypeID": ar_type_val,
                "ArrestSurrenderDate": r["arrest_date"],
                "ArrestSurrenderStateId": 1,
                "ArrestSurrenderDistrictId": dist_map.get(r["arrest_district"], 1),
                "PoliceStationID": unit_map.get(r["arrest_station"], 1),
                "IOID": emp_map.get(r["arrest_io_kgid"], 1),
                "CourtID": court_map.get(r["arrest_court"], 1),
                "AccusedMasterID": primary_accused_master_id,
                "IsAccused": 1,
                "IsComplainantAccused": 0
            })

            for a_m_id in case_accused_ids:
                arrest_junc_rows.append({
                    "ArrestSurrenderID": ar_id,
                    "AccusedMasterID": a_m_id
                })

        if r["chargesheet_date"] and str(r["chargesheet_date"]).strip() != "":
            cs_rows.append({
                "CSID": cs_id_counter,
                "CaseMasterID": cm_id,
                "csdate": r["chargesheet_date"],
                "cstype": r["chargesheet_type"],
                "PolicePersonID": emp_map.get(r["chargesheet_officer_kgid"], 1)
            })
            cs_id_counter += 1

    # Save operational tables
    pd.DataFrame(case_rows).to_csv(os.path.join(out_dir, "CaseMaster.csv"), index=False)
    pd.DataFrame(occur_rows).to_csv(os.path.join(out_dir, "Inv_OccuranceTime.csv"), index=False)
    pd.DataFrame(comp_rows).to_csv(os.path.join(out_dir, "ComplainantDetails.csv"), index=False)
    pd.DataFrame(vic_rows).to_csv(os.path.join(out_dir, "Victim.csv"), index=False)
    pd.DataFrame(act_sec_rows).to_csv(os.path.join(out_dir, "ActSectionAssociation.csv"), index=False)
    pd.DataFrame(accused_rows).to_csv(os.path.join(out_dir, "Accused.csv"), index=False)
    pd.DataFrame(arrest_rows).to_csv(os.path.join(out_dir, "ArrestSurrender.csv"), index=False)
    pd.DataFrame(arrest_junc_rows).to_csv(os.path.join(out_dir, "inv_arrestsurrenderaccused.csv"), index=False)
    pd.DataFrame(cs_rows).to_csv(os.path.join(out_dir, "ChargesheetDetails.csv"), index=False)

    print("All 31 normalized CSV tables exported successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate New Karnataka Crime Synthetic Dataset")
    parser.add_argument("--rows", type=int, default=15000, help="Number of synthetic FIR cases to generate")
    args = parser.parse_args()
    
    generate_synthetic_dataset(num_cases=args.rows)
