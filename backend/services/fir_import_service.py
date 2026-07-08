import io
import re
import time
from typing import Optional
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from backend.models import (
    State, District, Court, UnitType, Unit, Rank, Designation, Employee,
    CaseCategory, GravityOffence, CaseStatusMaster, CasteMaster, ReligionMaster,
    OccupationMaster, GenderMaster, NationalityMaster, BloodGroupMaster,
    Act, Section, CrimeHead, CrimeSubHead, CaseMaster, Inv_OccuranceTime,
    ComplainantDetails, FIRVictim, Accused, ArrestSurrender, ChargesheetDetails,
    ActSectionAssociation
)
from backend.repositories.fir_repository import FIRRepository
from backend.core.validation import validate_crime_no, validate_case_no, generate_case_no

class FIRImportService:
    """
    Ingests and normalizes flat CSV/Excel datasets conforming to the Karnataka 
    Police schema, validating parameters, caching lookup tables, enforcing dependency 
    orderings, and returning a structured import summary report.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = FIRRepository(db)
        
        # In-memory caches for lookup resolutions to prevent duplicate N+1 lookups/inserts
        self.nationality_cache = {}
        self.gender_cache = {}
        self.blood_group_cache = {}
        self.caste_cache = {}
        self.religion_cache = {}
        self.occupation_cache = {}
        self.category_cache = {}
        self.gravity_cache = {}
        self.status_cache = {}
        
        self.state_cache = {}
        self.district_cache = {}
        self.court_cache = {}
        self.unit_type_cache = {}
        self.unit_cache = {}
        self.rank_cache = {}
        self.designation_cache = {}
        self.employee_cache = {}
        
        self.act_cache = {}
        self.section_cache = {}
        self.crime_head_cache = {}
        self.crime_sub_head_cache = {}

        # Counter for reporting new inserts
        self.lookups_inserted = 0

    # ── Master Lookup Resolver Helpers (with auto-insert fallback & caching) ───

    def get_nationality(self, name: str) -> int:
        name = str(name).strip()
        if name in self.nationality_cache:
            return self.nationality_cache[name]
        obj = self.db.query(NationalityMaster).filter(NationalityMaster.name == name).first()
        if not obj:
            obj = NationalityMaster(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.nationality_cache[name] = obj.id
        return obj.id

    def get_gender(self, name: str) -> int:
        name = str(name).strip()
        if name in self.gender_cache:
            return self.gender_cache[name]
        obj = self.db.query(GenderMaster).filter(GenderMaster.name == name).first()
        if not obj:
            obj = GenderMaster(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.gender_cache[name] = obj.id
        return obj.id

    def get_blood_group(self, name: Optional[str]) -> Optional[int]:
        if not name:
            return None
        name = str(name).strip()
        if name in self.blood_group_cache:
            return self.blood_group_cache[name]
        obj = self.db.query(BloodGroupMaster).filter(BloodGroupMaster.name == name).first()
        if not obj:
            obj = BloodGroupMaster(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.blood_group_cache[name] = obj.id
        return obj.id

    def get_caste(self, name: Optional[str]) -> Optional[int]:
        if not name:
            return None
        name = str(name).strip()
        if name in self.caste_cache:
            return self.caste_cache[name]
        obj = self.db.query(CasteMaster).filter(CasteMaster.name == name).first()
        if not obj:
            obj = CasteMaster(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.caste_cache[name] = obj.id
        return obj.id

    def get_religion(self, name: Optional[str]) -> Optional[int]:
        if not name:
            return None
        name = str(name).strip()
        if name in self.religion_cache:
            return self.religion_cache[name]
        obj = self.db.query(ReligionMaster).filter(ReligionMaster.name == name).first()
        if not obj:
            obj = ReligionMaster(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.religion_cache[name] = obj.id
        return obj.id

    def get_occupation(self, name: Optional[str]) -> Optional[int]:
        if not name:
            return None
        name = str(name).strip()
        if name in self.occupation_cache:
            return self.occupation_cache[name]
        obj = self.db.query(OccupationMaster).filter(OccupationMaster.name == name).first()
        if not obj:
            obj = OccupationMaster(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.occupation_cache[name] = obj.id
        return obj.id

    def get_case_category(self, name: str) -> int:
        name = str(name).strip()
        if name in self.category_cache:
            return self.category_cache[name]
        obj = self.db.query(CaseCategory).filter(CaseCategory.name == name).first()
        if not obj:
            obj = CaseCategory(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.category_cache[name] = obj.id
        return obj.id

    def get_gravity_offence(self, name: str) -> int:
        name = str(name).strip()
        if name in self.gravity_cache:
            return self.gravity_cache[name]
        obj = self.db.query(GravityOffence).filter(GravityOffence.name == name).first()
        if not obj:
            obj = GravityOffence(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.gravity_cache[name] = obj.id
        return obj.id

    def get_case_status(self, name: str) -> int:
        name = str(name).strip()
        if name in self.status_cache:
            return self.status_cache[name]
        obj = self.db.query(CaseStatusMaster).filter(CaseStatusMaster.name == name).first()
        if not obj:
            obj = CaseStatusMaster(name=name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.status_cache[name] = obj.id
        return obj.id

    def get_state(self, name: str) -> int:
        name = str(name).strip()
        if name in self.state_cache:
            return self.state_cache[name]
        obj = self.db.query(State).filter(State.name == name).first()
        if not obj:
            nat_id = self.get_nationality("Indian")
            obj = State(name=name, NationalityID=nat_id)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.state_cache[name] = obj.id
        return obj.id

    def get_district(self, name: str, state_name: str) -> int:
        name = str(name).strip()
        if name in self.district_cache:
            return self.district_cache[name]
        obj = self.db.query(District).filter(District.name == name).first()
        if not obj:
            state_id = self.get_state(state_name)
            obj = District(name=name, StateID=state_id)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.district_cache[name] = obj.id
        return obj.id

    def get_court(self, name: str, district_name: str, state_name: str) -> int:
        name = str(name).strip()
        if name in self.court_cache:
            return self.court_cache[name]
        obj = self.db.query(Court).filter(Court.name == name).first()
        if not obj:
            dist_id = self.get_district(district_name, state_name)
            state_id = self.get_state(state_name)
            obj = Court(name=name, DistrictID=dist_id, StateID=state_id)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.court_cache[name] = obj.id
        return obj.id

    def get_unit_type(self, name: str) -> int:
        name = str(name).strip()
        if name in self.unit_type_cache:
            return self.unit_type_cache[name]
        obj = self.db.query(UnitType).filter(UnitType.name == name).first()
        if not obj:
            obj = UnitType(name=name, CityDistState="District", Hierarchy=1)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.unit_type_cache[name] = obj.id
        return obj.id

    def get_unit(self, name: str, district_name: str, state_name: str) -> int:
        name = str(name).strip()
        if name in self.unit_cache:
            return self.unit_cache[name]
        obj = self.db.query(Unit).filter(Unit.name == name).first()
        if not obj:
            type_id = self.get_unit_type("Police Station")
            nat_id = self.get_nationality("Indian")
            state_id = self.get_state(state_name)
            dist_id = self.get_district(district_name, state_name)
            obj = Unit(
                name=name,
                TypeID=type_id,
                NationalityID=nat_id,
                StateID=state_id,
                DistrictID=dist_id
            )
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.unit_cache[name] = obj.id
        return obj.id

    def get_rank(self, name: str) -> int:
        name = str(name).strip()
        if name in self.rank_cache:
            return self.rank_cache[name]
        obj = self.db.query(Rank).filter(Rank.name == name).first()
        if not obj:
            obj = Rank(name=name, Hierarchy=1)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.rank_cache[name] = obj.id
        return obj.id

    def get_designation(self, name: str) -> int:
        name = str(name).strip()
        if name in self.designation_cache:
            return self.designation_cache[name]
        obj = self.db.query(Designation).filter(Designation.name == name).first()
        if not obj:
            obj = Designation(name=name, SortOrder=1)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.designation_cache[name] = obj.id
        return obj.id

    def get_employee(
        self,
        kgid: str,
        name: str,
        rank_name: str,
        desig_name: str,
        district_name: str,
        state_name: str,
        unit_name: str,
        gender_name: str = "Male"
    ) -> int:
        kgid = str(kgid).strip()
        if kgid in self.employee_cache:
            return self.employee_cache[kgid]
        obj = self.db.query(Employee).filter(Employee.KGID == kgid).first()
        if not obj:
            dist_id = self.get_district(district_name, state_name)
            unit_id = self.get_unit(unit_name, district_name, state_name)
            rank_id = self.get_rank(rank_name)
            desig_id = self.get_designation(desig_name)
            gen_id = self.get_gender(gender_name)
            
            obj = Employee(
                DistrictID=dist_id,
                UnitID=unit_id,
                RankID=rank_id,
                DesignationID=desig_id,
                KGID=kgid,
                FirstName=name,
                GenderID=gen_id,
                AppointmentDate=date.today() - timedelta(days=365 * 5)
            )
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.employee_cache[kgid] = obj.id
        return obj.id

    def get_act(self, code: str, description: Optional[str]) -> str:
        code = str(code).strip()
        if code in self.act_cache:
            return self.act_cache[code]
        obj = self.db.query(Act).filter(Act.ActCode == code).first()
        if not obj:
            obj = Act(ActCode=code, ActDescription=description or code, ShortName=code)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.act_cache[code] = obj.ActCode
        return obj.ActCode

    def get_section(self, act_code: str, sec_code: str, description: Optional[str]) -> str:
        key = (act_code, sec_code)
        if key in self.section_cache:
            return self.section_cache[key]
        obj = self.db.query(Section).filter(Section.ActCode == act_code, Section.SectionCode == sec_code).first()
        if not obj:
            self.get_act(act_code, None)
            obj = Section(ActCode=act_code, SectionCode=sec_code, SectionDescription=description or sec_code)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.section_cache[key] = obj.SectionCode
        return obj.SectionCode

    def get_crime_head(self, group_name: str) -> int:
        group_name = str(group_name).strip()
        if group_name in self.crime_head_cache:
            return self.crime_head_cache[group_name]
        obj = self.db.query(CrimeHead).filter(CrimeHead.CrimeGroupName == group_name).first()
        if not obj:
            obj = CrimeHead(CrimeGroupName=group_name)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.crime_head_cache[group_name] = obj.id
        return obj.id

    def get_crime_sub_head(self, head_name: str, major_head_group_name: str) -> int:
        head_name = str(head_name).strip()
        if head_name in self.crime_sub_head_cache:
            return self.crime_sub_head_cache[head_name]
        obj = self.db.query(CrimeSubHead).filter(CrimeSubHead.CrimeHeadName == head_name).first()
        if not obj:
            crime_head_id = self.get_crime_head(major_head_group_name)
            obj = CrimeSubHead(CrimeHeadID=crime_head_id, CrimeHeadName=head_name, SeqID=1)
            self.db.add(obj)
            self.db.flush()
            self.lookups_inserted += 1
        self.crime_sub_head_cache[head_name] = obj.id
        return obj.id

    # ── Ingestion Logic ────────────────────────────────────────────────────────

    def parse_file_to_rows(self, file_bytes: bytes, file_name: str) -> list[dict]:
        """
        Parses raw CSV or Excel data bytes, converts them into a list of row dicts.
        """
        if file_name.lower().endswith((".xlsx", ".xls")):
            try:
                df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
            except Exception as e:
                raise ValueError(f"Failed to parse Excel file: {str(e)}")
        elif file_name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(file_bytes))
            except Exception as e:
                raise ValueError(f"Failed to parse CSV file: {str(e)}")
        else:
            raise ValueError("Unsupported format. Only CSV and Excel (.xlsx, .xls) are supported.")
            
        df = df.replace({np.nan: None})
        return df.to_dict(orient="records")

    def detect_schema_type(self, columns: list[str]) -> str:
        """
        Robust schema detection using multiple required headers sets.
        """
        cols = {str(c).strip().lower() for c in columns}
        fir_indicators = {"crime_no", "registered_date", "act_code", "section_code"}
        if fir_indicators.issubset(cols):
            return "fir_normalized"
        return "legacy_crime_intel"

    def validate_rows(self, rows: list[dict]) -> list[str]:
        """
        Dry-run validation checks across all rows in the dataset.
        """
        errors = []
        required_cols = {"crime_no", "registered_date", "unit", "act_code", "section_code", "district", "state"}
        
        if not rows:
            return ["Uploaded file contains no data rows."]
            
        # Inspect columns of first row to check required sets
        actual_cols = {str(k).strip().lower() for k in rows[0].keys()}
        missing = required_cols - actual_cols
        if missing:
            return [f"Missing required schema columns: {sorted(missing)}"]

        for idx, r in enumerate(rows):
            row_num = idx + 2
            
            # Check mandatory values
            for col in required_cols:
                val = r.get(col)
                if val is None or str(val).strip() == "":
                    errors.append(f"Row {row_num}: Column '{col}' is blank.")
            
            # Check CrimeNo and CaseNo format
            c_no = r.get("crime_no")
            if c_no and not validate_crime_no(str(c_no)):
                errors.append(f"Row {row_num}: CrimeNo '{c_no}' does not conform to the 18-digit official spec.")
                
            cs_no = r.get("case_no")
            if cs_no and not validate_case_no(str(cs_no)):
                errors.append(f"Row {row_num}: CaseNo '{cs_no}' does not conform to the 9-digit official spec.")

            # Validate coordinate bounds
            lat = r.get("latitude")
            if lat is not None:
                try:
                    lat_f = float(lat)
                    if not (-90 <= lat_f <= 90):
                        errors.append(f"Row {row_num}: Latitude {lat} is out of bounds [-90, 90].")
                except ValueError:
                    errors.append(f"Row {row_num}: Latitude {lat} is not a valid number.")

            lon = r.get("longitude")
            if lon is not None:
                try:
                    lon_f = float(lon)
                    if not (-180 <= lon_f <= 180):
                        errors.append(f"Row {row_num}: Longitude {lon} is out of bounds [-180, 180].")
                except ValueError:
                    errors.append(f"Row {row_num}: Longitude {lon} is not a valid number.")

            # Validate logical age bounds (complainant, victim, accused)
            for age_col in ["complainant_age", "victim_age", "accused_age", "officer_age"]:
                age = r.get(age_col)
                if age is not None:
                    try:
                        age_i = int(float(age))
                        if not (0 <= age_i <= 125):
                            errors.append(f"Row {row_num}: '{age_col}' {age} is out of bounds [0, 125].")
                    except ValueError:
                        errors.append(f"Row {row_num}: '{age_col}' {age} is not a valid integer.")
                        
        return errors

    def import_normalized_dataset(
        self,
        rows: list[dict],
        dataset_id: int,
        user_id: Optional[int] = None
    ) -> dict:
        """
        Ingests flat normalized records inside a single transaction, resolving 
        relational dependencies and outputting a detailed import report.
        """
        start_time = time.time()
        
        # 1. Group rows by unique CrimeNo
        grouped_cases = {}
        for r in rows:
            c_no = str(r["crime_no"]).strip()
            if c_no not in grouped_cases:
                grouped_cases[c_no] = []
            grouped_cases[c_no].append(r)

        # Counter metrics
        cases_inserted = 0
        victim_count = 0
        accused_count = 0
        complainant_count = 0
        arrest_count = 0
        chargesheet_count = 0
        warnings = []

        try:
            for crime_no, case_rows in grouped_cases.items():
                first_row = case_rows[0]
                
                # Check duplicate case in DB
                dup = self.db.query(CaseMaster).filter(CaseMaster.CrimeNo == crime_no).first()
                if dup:
                    warnings.append(f"CrimeNo '{crime_no}' already exists in database. Skipped duplicate import.")
                    continue

                # 2. Resolve lookup tables for CaseMaster
                cat_id = self.get_case_category(first_row.get("case_category", "FIR"))
                grav_id = self.get_gravity_offence(first_row.get("gravity_offence", "Non-Heinous"))
                status_id = self.get_case_status(first_row.get("case_status", "Under Investigation"))
                
                # Geography and unit hierarchy
                state_name = first_row.get("state", "Karnataka")
                dist_name = first_row.get("district", "Mysuru")
                court_name = first_row.get("court", "JMFC Court")
                unit_name = first_row.get("unit", "Devaraja PS")
                
                court_id = self.get_court(court_name, dist_name, state_name)
                unit_id = self.get_unit(unit_name, dist_name, state_name)
                
                # Registering Officer Employee ID
                officer_kgid = first_row.get("officer_kgid", "KA0001")
                officer_name = first_row.get("officer_name", "Officer")
                officer_rank = first_row.get("officer_rank", "Sub-Inspector")
                officer_desig = first_row.get("officer_designation", "Officer")
                
                officer_id = self.get_employee(
                    kgid=officer_kgid,
                    name=officer_name,
                    rank_name=officer_rank,
                    desig_name=officer_desig,
                    district_name=dist_name,
                    state_name=state_name,
                    unit_name=unit_name,
                    gender_name=first_row.get("officer_gender", "Male")
                )
                
                # Major & Minor crime heads
                major_head = first_row.get("crime_group_name", "Property Crimes")
                minor_head = first_row.get("crime_head_name", "House Theft")
                major_head_id = self.get_crime_head(major_head)
                minor_head_id = self.get_crime_sub_head(minor_head, major_head)

                # Parse dates
                reg_date = date.fromisoformat(first_row["registered_date"][:10])
                
                # 3. Create CaseMaster and Inv_OccuranceTime
                case_no = first_row.get("case_no") or generate_case_no(crime_no)
                
                inc_from = datetime.fromisoformat(first_row["incident_from_date"]) if first_row.get("incident_from_date") else None
                inc_to = datetime.fromisoformat(first_row["incident_to_date"]) if first_row.get("incident_to_date") else None
                info_received = datetime.fromisoformat(first_row["info_received_date"]) if first_row.get("info_received_date") else None
                
                case = self.repo.create_case(
                    crime_no=crime_no,
                    case_no=case_no,
                    registered_date=reg_date,
                    police_person_id=officer_id,
                    police_station_id=unit_id,
                    case_category_id=cat_id,
                    gravity_offence_id=grav_id,
                    crime_major_head_id=major_head_id,
                    crime_minor_head_id=minor_head_id,
                    case_status_id=status_id,
                    court_id=court_id,
                    brief_facts=first_row.get("brief_facts"),
                    dataset_id=dataset_id,
                    incident_from_date=inc_from,
                    incident_to_date=inc_to,
                    info_received_ps_date=info_received,
                    latitude=first_row.get("latitude"),
                    longitude=first_row.get("longitude"),
                    occurrence_brief_facts=first_row.get("occurrence_brief_facts"),
                    performed_by_user_id=user_id,
                    commit=False
                )
                cases_inserted += 1

                # 4. Insert Unique Child Records
                seen_complainants = set()
                seen_victims = set()
                seen_accused = set()
                seen_act_sections = set()
                accused_id_map = {} # name -> id

                for r in case_rows:
                    # Complainants
                    comp_name = r.get("complainant_name")
                    if comp_name and comp_name not in seen_complainants:
                        seen_complainants.add(comp_name)
                        comp_gender = self.get_gender(r.get("complainant_gender", "Male"))
                        comp_occ = self.get_occupation(r.get("complainant_occupation"))
                        comp_rel = self.get_religion(r.get("complainant_religion"))
                        comp_caste = self.get_caste(r.get("complainant_caste"))
                        
                        self.repo.add_complainant_to_case(
                            case_id=case.id,
                            name=comp_name,
                            age=int(float(r["complainant_age"])) if r.get("complainant_age") is not None else None,
                            occupation_id=comp_occ,
                            religion_id=comp_rel,
                            caste_id=comp_caste,
                            gender_id=comp_gender,
                            performed_by_user_id=user_id,
                            commit=False
                        )
                        complainant_count += 1

                    # Victims
                    vic_name = r.get("victim_name")
                    if vic_name and vic_name not in seen_victims:
                        seen_victims.add(vic_name)
                        vic_gender = self.get_gender(r.get("victim_gender", "Male"))
                        
                        self.repo.add_victim_to_case(
                            case_id=case.id,
                            name=vic_name,
                            age=int(float(r["victim_age"])) if r.get("victim_age") is not None else None,
                            gender_id=vic_gender,
                            victim_police=str(r.get("victim_police", "0")),
                            performed_by_user_id=user_id,
                            commit=False
                        )
                        victim_count += 1

                    # Accused
                    acc_name = r.get("accused_name")
                    if acc_name and acc_name not in seen_accused:
                        seen_accused.add(acc_name)
                        acc_gender = self.get_gender(r.get("accused_gender", "Male"))
                        
                        acc = self.repo.add_accused_to_case(
                            case_id=case.id,
                            name=acc_name,
                            age=int(float(r["accused_age"])) if r.get("accused_age") is not None else None,
                            gender_id=acc_gender,
                            person_id=r.get("accused_person_id"),
                            performed_by_user_id=user_id,
                            commit=False
                        )
                        accused_count += 1
                        accused_id_map[acc_name] = acc.id

                    # Acts and Sections
                    act_code = r.get("act_code")
                    sec_code = r.get("section_code")
                    if act_code and sec_code:
                        act_sec_key = (act_code, sec_code)
                        if act_sec_key not in seen_act_sections:
                            seen_act_sections.add(act_sec_key)
                            self.get_section(act_code, sec_code, r.get("section_description"))
                            self.repo.associate_act_section_with_case(
                                case_id=case.id,
                                act_code=act_code,
                                section_code=sec_code,
                                act_order_id=r.get("act_order", 1),
                                section_order_id=r.get("section_order", 1),
                                performed_by_user_id=user_id,
                                commit=False
                            )

                    # Arrest & Surrenders (only recorded on first row to prevent duplicate event inserts)
                    if r.get("arrest_date") and r.get("arrest_primary_accused_name"):
                        arrest_type_id = int(r["arrest_type"])
                        arrest_dt = date.fromisoformat(r["arrest_date"][:10])
                        
                        arrest_state_id = self.get_state(r.get("arrest_state", "Karnataka"))
                        arrest_dist_id = self.get_district(r.get("arrest_district", "Mysuru"), r.get("arrest_state", "Karnataka"))
                        arrest_unit_id = self.get_unit(r.get("arrest_station", "Devaraja PS"), r.get("arrest_district", "Mysuru"), r.get("arrest_state", "Karnataka"))
                        
                        # Arrest IO Employee ID
                        io_kgid = r.get("arrest_io_kgid", officer_kgid)
                        arrest_io_id = self.get_employee(
                            kgid=io_kgid,
                            name=officer_name,
                            rank_name=officer_rank,
                            desig_name=officer_desig,
                            district_name=dist_name,
                            state_name=state_name,
                            unit_name=unit_name
                        )
                        
                        arrest_court_id = self.get_court(r.get("arrest_court", court_name), dist_name, state_name)
                        
                        # Resolve primary accused id
                        prim_acc_name = r["arrest_primary_accused_name"]
                        prim_id = accused_id_map.get(prim_acc_name)
                        if not prim_id:
                            # Search in database or fallback
                            prim_id = self.db.query(Accused.id).filter(Accused.CaseMasterID == case.id, Accused.AccusedName == prim_acc_name).scalar()
                            
                        # Resolve joint accused ids
                        joint_ids = []
                        joint_str = r.get("arrest_joint_accused_names")
                        if joint_str:
                            for name in str(joint_str).split(","):
                                name = name.strip()
                                jid = accused_id_map.get(name)
                                if not jid:
                                    jid = self.db.query(Accused.id).filter(Accused.CaseMasterID == case.id, Accused.AccusedName == name).scalar()
                                if jid:
                                    joint_ids.append(jid)
                                    
                        if prim_id:
                            self.repo.record_arrest_surrender(
                                case_id=case.id,
                                type_id=arrest_type_id,
                                date_val=arrest_dt,
                                state_id=arrest_state_id,
                                district_id=arrest_dist_id,
                                station_id=arrest_unit_id,
                                io_id=arrest_io_id,
                                court_id=arrest_court_id,
                                accused_master_id=prim_id,
                                is_accused=True,
                                is_complainant_accused=False,
                                other_accused_ids=joint_ids,
                                performed_by_user_id=user_id,
                                commit=False
                            )
                            arrest_count += 1

                    # Chargesheets
                    if r.get("chargesheet_date") and r.get("chargesheet_type"):
                        cs_dt = datetime.fromisoformat(r["chargesheet_date"])
                        cs_officer_kgid = r.get("chargesheet_officer_kgid", officer_kgid)
                        cs_officer_id = self.get_employee(
                            kgid=cs_officer_kgid,
                            name=officer_name,
                            rank_name=officer_rank,
                            desig_name=officer_desig,
                            district_name=dist_name,
                            state_name=state_name,
                            unit_name=unit_name
                        )
                        self.repo.record_chargesheet(
                            case_id=case.id,
                            date_val=cs_dt,
                            cs_type=r["chargesheet_type"],
                            police_person_id=cs_officer_id,
                            performed_by_user_id=user_id,
                            commit=False
                        )
                        chargesheet_count += 1
                        
            # Final Transaction Commit
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e

        duration = round(time.time() - start_time, 2)
        
        return {
            "lookup_records_inserted": self.lookups_inserted,
            "cases_inserted": cases_inserted,
            "victims_inserted": victim_count,
            "accused_inserted": accused_count,
            "complainants_inserted": complainant_count,
            "arrests_inserted": arrest_count,
            "chargesheets_inserted": chargesheet_count,
            "processing_time_seconds": duration,
            "warnings": warnings
        }
