import random
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from backend.core.validation import generate_crime_no, generate_case_no

class FIRSyntheticDataGenerator:
    """
    Generates realistic, relational synthetic datasets conforming strictly to 
    the official Karnataka Police schema. It is fully configurable in dataset size 
    and export output paths.
    """
    def __init__(self):
        # Seed lookups lists
        self.states = ["Karnataka", "Maharashtra", "Tamil Nadu"]
        self.districts = ["Mysuru", "Ballari", "Bengaluru City", "Dharwad", "Belagavi"]
        self.courts = ["JMFC I Court", "District Session Court", "High Court Bengaluru"]
        self.unit_types = ["Police Station", "Circle Office", "District Office"]
        self.units = ["Devaraja PS", "Gandhinagar PS", "Town PS", "Cantonment PS", "Rural PS"]
        self.ranks = ["Constable", "Head Constable", "Sub-Inspector", "Inspector", "Deputy Superintendent"]
        self.designations = ["Station Writer", "Investigating Officer", "SHO", "Circle Inspector"]
        self.first_names = ["Amit", "Rahul", "Vijay", "Sanjay", "Anil", "Sunil", "Rajesh", "Prakash", "Kiran", "Ramesh", "Deepak", "Suresh", "Priya", "Sunita", "Anita", "Geeta"]
        self.last_names = ["Kumar", "Sharma", "Singh", "Patil", "Gowda", "Reddy", "Nair", "Joshi", "Das", "Mehta", "Sen", "Rao", "Patel", "Chatterjee", "Mukherjee", "Pillai"]
        self.castes = ["General", "OBC", "SC", "ST"]
        self.religions = ["Hindu", "Muslim", "Christian", "Sikh", "Jain"]
        self.occupations = ["Farmer", "Business", "Labourer", "Driver", "Techie", "Unemployed"]
        self.genders = ["Male", "Female", "Transgender"]
        self.nationalities = ["Indian", "Nepalese", "Others"]
        self.blood_groups = ["O Positive", "A Positive", "B Positive", "AB Positive", "O Negative"]
        
        self.acts = {
            "IPC": "Indian Penal Code",
            "KPA": "Karnataka Police Act",
            "NDPS": "Narcotic Drugs and Psychotropic Substances Act"
        }
        self.sections = {
            "IPC": [("379", "Theft"), ("302", "Murder"), ("324", "Voluntarily causing hurt"), ("506", "Criminal intimidation")],
            "KPA": [("92", "Punishment for street offences")],
            "NDPS": [("20", "Punishment for cannabis possession")]
        }
        self.crime_heads = ["Crimes Against Body", "Property Crimes", "Narcotics", "Public Nuisance"]
        self.crime_sub_heads = {
            "Crimes Against Body": ["Murder", "Assault", "Kidnapping"],
            "Property Crimes": ["House Theft", "Chain Snatching", "Robbery"],
            "Narcotics": ["Drug Peddling", "Possession"],
            "Public Nuisance": ["Street Fighting", "Public Drunkenness"]
        }
        
        self.categories = ["FIR", "UDR", "PAR"]
        self.gravities = ["Heinous", "Non-Heinous"]
        self.statuses = ["Under Investigation", "Chargesheeted", "Report Beece (B-Report)", "Undetected"]
        
        # Load Karnataka state boundary geometry
        import os
        import geopandas as gpd
        geojson_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "karnataka_boundary.geojson")
        if os.path.exists(geojson_path):
            gdf = gpd.read_file(geojson_path)
            self.karnataka_geom = gdf.geometry.iloc[0]
        else:
            self.karnataka_geom = None

    def generate(self, num_records: int = 100) -> list[dict]:
        """
        Generates a flat representation of normalized relational records. 
        Accommodates multi-valued children by outputting rows grouped under the same CrimeNo.
        """
        rows = []
        random.seed(42) # Deterministic generation
        
        # Build registry of generated CrimeNo serial count to prevent duplicates
        serial_tracker = {} # (station_idx, year) -> current_serial_int
        
        # We want to generate 'num_records' distinct cases.
        for case_idx in range(num_records):
            # Choose org details
            state_val = random.choice(self.states)
            dist_idx = random.randint(0, len(self.districts) - 1)
            district_val = self.districts[dist_idx]
            
            unit_idx = random.randint(0, len(self.units) - 1)
            unit_val = self.units[unit_idx]
            court_val = self.courts[random.randint(0, len(self.courts) - 1)]
            
            # Category index
            cat_idx = random.randint(1, len(self.categories)) # 1-based index
            cat_val = self.categories[cat_idx - 1]
            
            # Year & Serial resolution
            year = random.choice([2024, 2025, 2026])
            tracker_key = (unit_idx, year)
            serial = serial_tracker.get(tracker_key, 0) + 1
            serial_tracker[tracker_key] = serial
            
            # Generate CrimeNo/CaseNo
            crime_no = generate_crime_no(
                category=cat_idx,
                district=dist_idx + 1,
                station=unit_idx + 1,
                year=year,
                serial=serial
            )
            case_no = generate_case_no(crime_no)
            
            # Crime details
            reg_date = date(year, random.randint(1, 12), random.randint(1, 28))
            brief_facts = f"Occurrence reported at {unit_val} under major head. Action taken."
            gravity_val = random.choice(self.gravities)
            status_val = random.choice(self.statuses)
            
            major_head_val = random.choice(self.crime_heads)
            minor_head_val = random.choice(self.crime_sub_heads[major_head_val])
            
            # Occurrence dates
            inc_from = datetime.combine(reg_date - timedelta(days=1), datetime.min.time()) + timedelta(hours=random.randint(0, 23))
            inc_to = inc_from + timedelta(hours=random.randint(1, 3))
            info_received = datetime.combine(reg_date, datetime.min.time()) + timedelta(hours=random.randint(8, 12))
            lat, lon = None, None
            if self.karnataka_geom is not None:
                from shapely.geometry import Point
                for attempt in range(100):
                    cand_lat = round(random.uniform(11.5, 18.5), 4)
                    cand_lon = round(random.uniform(74.0, 78.5), 4)
                    if self.karnataka_geom.contains(Point(cand_lon, cand_lat)):
                        lat, lon = cand_lat, cand_lon
                        break
                if lat is None:
                    import logging
                    logging.warning(f"Failed to generate coordinate in Karnataka after 100 attempts at case {case_idx}")
                    lat, lon = 12.9716, 77.5946
            else:
                lat = round(random.uniform(12.0, 15.0), 4)
                lon = round(random.uniform(74.0, 78.0), 4)
            occ_facts = f"Incident details at lat {lat}, lon {lon}."
            
            # Officer details
            officer_kgid = f"KA{random.randint(10000, 99999)}"
            officer_name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
            officer_rank = random.choice(self.ranks)
            officer_designation = random.choice(self.designations)
            officer_dob = reg_date - timedelta(days=365 * random.randint(30, 55))
            officer_gender = random.choice(self.genders)
            officer_bg = random.choice(self.blood_groups)
            officer_physically_challenged = random.choice([True, False])
            officer_app = officer_dob + timedelta(days=365 * random.randint(22, 28))
            
            # Complainants
            num_comps = random.randint(1, 2)
            comps = []
            for _ in range(num_comps):
                comps.append({
                    "complainant_name": f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                    "complainant_age": random.randint(20, 70),
                    "complainant_occupation": random.choice(self.occupations),
                    "complainant_religion": random.choice(self.religions),
                    "complainant_caste": random.choice(self.castes),
                    "complainant_gender": random.choice(self.genders)
                })
                
            # Victims
            num_vics = random.randint(1, 2)
            vics = []
            for _ in range(num_vics):
                vics.append({
                    "victim_name": f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                    "victim_age": random.randint(5, 75),
                    "victim_gender": random.choice(self.genders),
                    "victim_police": random.choice(["0", "1"])
                })
                
            # Accused
            num_accs = random.randint(1, 3)
            accs = []
            for a_idx in range(num_accs):
                accs.append({
                    "accused_name": f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                    "accused_age": random.randint(18, 65),
                    "accused_gender": random.choice(self.genders),
                    "accused_person_id": f"A{a_idx + 1}"
                })
                
            # Acts & Sections
            act_code = random.choice(list(self.sections.keys()))
            sec_pair = random.choice(self.sections[act_code])
            sec_code = sec_pair[0]
            sec_desc = sec_pair[1]
            act_desc = self.acts[act_code]
            
            # Arrest
            arrest_date = reg_date + timedelta(days=random.randint(1, 5))
            arrest_type = random.choice([1, 2]) # 1 -> Arrest, 2 -> Surrender
            arrest_state = state_val
            arrest_district = district_val
            arrest_station = unit_val
            arrest_io_kgid = officer_kgid
            arrest_court = court_val
            arrest_primary_accused_name = accs[0]["accused_name"]
            arrest_joint_accused_names = ",".join([a["accused_name"] for a in accs[1:]]) if len(accs) > 1 else ""
            
            # Chargesheet
            chargesheet_date = datetime.combine(reg_date + timedelta(days=random.randint(15, 60)), datetime.min.time()) + timedelta(hours=11)
            chargesheet_type = "A" if status_val == "Chargesheeted" else ("B" if status_val.startswith("Report") else "C")
            chargesheet_officer_kgid = officer_kgid
            
            # Max child length to flatten
            max_len = max(len(comps), len(vics), len(accs))
            for i in range(max_len):
                row = {
                    "case_category": cat_val,
                    "gravity_offence": gravity_val,
                    "case_status": status_val,
                    "state": state_val,
                    "district": district_val,
                    "court": court_val,
                    "unit_type": "Police Station",
                    "unit": unit_val,
                    
                    "officer_kgid": officer_kgid,
                    "officer_name": officer_name,
                    "officer_rank": officer_rank,
                    "officer_designation": officer_designation,
                    "officer_dob": officer_dob.isoformat(),
                    "officer_gender": officer_gender,
                    "officer_blood_group": officer_bg,
                    "officer_physically_challenged": int(officer_physically_challenged),
                    "officer_appointment_date": officer_app.isoformat(),
                    
                    "crime_no": crime_no,
                    "case_no": case_no,
                    "registered_date": reg_date.isoformat(),
                    "brief_facts": brief_facts,
                    
                    "incident_from_date": inc_from.isoformat(),
                    "incident_to_date": inc_to.isoformat(),
                    "info_received_date": info_received.isoformat(),
                    "latitude": lat,
                    "longitude": lon,
                    "occurrence_brief_facts": occ_facts,
                    
                    "crime_group_name": major_head_val,
                    "crime_head_name": minor_head_val,
                    "act_code": act_code,
                    "act_description": act_desc,
                    "short_name": act_code,
                    "section_code": sec_code,
                    "section_description": sec_desc,
                    "act_order": 1,
                    "section_order": 1
                }
                
                # Complainants
                if i < len(comps):
                    row.update(comps[i])
                else:
                    row.update({k: None for k in comps[0].keys()})
                    
                # Victims
                if i < len(vics):
                    row.update(vics[i])
                else:
                    row.update({k: None for k in vics[0].keys()})
                    
                # Accused
                if i < len(accs):
                    row.update(accs[i])
                else:
                    row.update({k: None for k in accs[0].keys()})
                    
                # Proceedings (only on first row of the case to prevent duplicate event inserts)
                if i == 0:
                    row.update({
                        "arrest_type": arrest_type,
                        "arrest_date": arrest_date.isoformat(),
                        "arrest_state": arrest_state,
                        "arrest_district": arrest_district,
                        "arrest_station": arrest_station,
                        "arrest_io_kgid": arrest_io_kgid,
                        "arrest_court": arrest_court,
                        "arrest_primary_accused_name": arrest_primary_accused_name,
                        "arrest_joint_accused_names": arrest_joint_accused_names,
                        "chargesheet_date": chargesheet_date.isoformat(),
                        "chargesheet_type": chargesheet_type,
                        "chargesheet_officer_kgid": chargesheet_officer_kgid
                    })
                else:
                    row.update({
                        "arrest_type": None,
                        "arrest_date": None,
                        "arrest_state": None,
                        "arrest_district": None,
                        "arrest_station": None,
                        "arrest_io_kgid": None,
                        "arrest_court": None,
                        "arrest_primary_accused_name": None,
                        "arrest_joint_accused_names": None,
                        "chargesheet_date": None,
                        "chargesheet_type": None,
                        "chargesheet_officer_kgid": None
                    })
                rows.append(row)
                
        return rows

    def generate_and_export(self, csv_path: str, excel_path: str, num_records: int = 100):
        """
        Generates and saves the synthetic dataset to CSV and Excel formats.
        """
        rows = self.generate(num_records)
        df = pd.DataFrame(rows)
        
        # Ensure directories exist
        import os
        for path in [csv_path, excel_path]:
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
                
        # Export CSV
        df.to_csv(csv_path, index=False)
        
        # Export Excel
        df.to_excel(excel_path, index=False, engine="openpyxl")
        return csv_path, excel_path
