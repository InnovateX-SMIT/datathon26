"""
seed_fir_lookups.py
====================
Seeds all FIR lookup master tables with realistic Karnataka Police data
so that the /fir/cases/new and /fir/cases/:id/edit forms load correctly
without requiring a full CSV/Excel dataset import.

Run from project root:
    python scripts/seed_fir_lookups.py
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, engine, Base
from backend.models import (
    NationalityMaster, GenderMaster, BloodGroupMaster, CasteMaster,
    ReligionMaster, OccupationMaster, CaseCategory, GravityOffence,
    CaseStatusMaster, State, District, Court, UnitType, Unit, Rank,
    Designation, Employee, Act, Section, CrimeHead, CrimeSubHead,
)


def seed_fir_lookups(db):
    print("Seeding FIR lookup tables...")

    # ── Nationality ────────────────────────────────────────────────────────────
    nationalities = ["Indian", "Nepalese", "Bangladeshi", "Sri Lankan", "Others"]
    nat_ids = {}
    for n in nationalities:
        obj = db.query(NationalityMaster).filter(NationalityMaster.name == n).first()
        if not obj:
            obj = NationalityMaster(name=n)
            db.add(obj)
    db.flush()
    for n in nationalities:
        obj = db.query(NationalityMaster).filter(NationalityMaster.name == n).first()
        nat_ids[n] = obj.id
    print(f"  Nationalities: {len(nationalities)}")

    # ── Gender ─────────────────────────────────────────────────────────────────
    genders = ["Male", "Female", "Transgender"]
    for g in genders:
        if not db.query(GenderMaster).filter(GenderMaster.name == g).first():
            db.add(GenderMaster(name=g))
    db.flush()
    print(f"  Genders: {len(genders)}")

    # ── Blood Group ────────────────────────────────────────────────────────────
    blood_groups = ["O Positive", "A Positive", "B Positive", "AB Positive",
                    "O Negative", "A Negative", "B Negative", "AB Negative"]
    for b in blood_groups:
        if not db.query(BloodGroupMaster).filter(BloodGroupMaster.name == b).first():
            db.add(BloodGroupMaster(name=b))
    db.flush()
    print(f"  Blood Groups: {len(blood_groups)}")

    # ── Caste ──────────────────────────────────────────────────────────────────
    castes = ["General", "OBC", "SC", "ST", "EWS"]
    for c in castes:
        if not db.query(CasteMaster).filter(CasteMaster.name == c).first():
            db.add(CasteMaster(name=c))
    db.flush()
    print(f"  Castes: {len(castes)}")

    # ── Religion ───────────────────────────────────────────────────────────────
    religions = ["Hindu", "Muslim", "Christian", "Sikh", "Jain", "Buddhist", "Others"]
    for r in religions:
        if not db.query(ReligionMaster).filter(ReligionMaster.name == r).first():
            db.add(ReligionMaster(name=r))
    db.flush()
    print(f"  Religions: {len(religions)}")

    # ── Occupation ─────────────────────────────────────────────────────────────
    occupations = ["Farmer", "Business", "Labourer", "Driver", "IT Professional",
                   "Government Employee", "Unemployed", "Student", "Homemaker", "Retired"]
    for o in occupations:
        if not db.query(OccupationMaster).filter(OccupationMaster.name == o).first():
            db.add(OccupationMaster(name=o))
    db.flush()
    print(f"  Occupations: {len(occupations)}")

    # ── Case Category ──────────────────────────────────────────────────────────
    categories = ["FIR", "UDR", "PAR", "Complaint", "Suo Motu"]
    for c in categories:
        if not db.query(CaseCategory).filter(CaseCategory.name == c).first():
            db.add(CaseCategory(name=c))
    db.flush()
    print(f"  Case Categories: {len(categories)}")

    # ── Gravity Offence ────────────────────────────────────────────────────────
    gravities = ["Heinous", "Non-Heinous", "Minor", "Economic Offence"]
    for g in gravities:
        if not db.query(GravityOffence).filter(GravityOffence.name == g).first():
            db.add(GravityOffence(name=g))
    db.flush()
    print(f"  Gravity Offences: {len(gravities)}")

    # ── Case Status ────────────────────────────────────────────────────────────
    statuses = [
        "Under Investigation", "Chargesheeted", "Report Beece (B-Report)",
        "Undetected", "True Case Pending Trial", "Referred to JMFC", "Closed"
    ]
    for s in statuses:
        if not db.query(CaseStatusMaster).filter(CaseStatusMaster.name == s).first():
            db.add(CaseStatusMaster(name=s))
    db.flush()
    print(f"  Case Statuses: {len(statuses)}")

    # ── State ──────────────────────────────────────────────────────────────────
    state_data = [
        ("Karnataka", "Indian"),
        ("Maharashtra", "Indian"),
        ("Tamil Nadu", "Indian"),
        ("Andhra Pradesh", "Indian"),
        ("Kerala", "Indian"),
        ("Goa", "Indian"),
        ("Telangana", "Indian"),
    ]
    state_ids = {}
    for state_name, nat_name in state_data:
        obj = db.query(State).filter(State.name == state_name).first()
        if not obj:
            nat_id = nat_ids.get(nat_name, nat_ids.get("Indian"))
            obj = State(name=state_name, NationalityID=nat_id)
            db.add(obj)
    db.flush()
    for state_name, _ in state_data:
        obj = db.query(State).filter(State.name == state_name).first()
        if obj:
            state_ids[state_name] = obj.id
    print(f"  States: {len(state_data)}")

    # ── District ───────────────────────────────────────────────────────────────
    karnataka_id = state_ids.get("Karnataka")
    district_data = [
        ("Bengaluru Urban", "Karnataka"),
        ("Bengaluru Rural", "Karnataka"),
        ("Mysuru", "Karnataka"),
        ("Belagavi", "Karnataka"),
        ("Dharwad", "Karnataka"),
        ("Ballari", "Karnataka"),
        ("Kalaburagi", "Karnataka"),
        ("Mangaluru", "Karnataka"),
        ("Shivamogga", "Karnataka"),
        ("Davanagere", "Karnataka"),
    ]
    district_ids = {}
    for dist_name, state_name in district_data:
        obj = db.query(District).filter(District.name == dist_name).first()
        if not obj:
            s_id = state_ids.get(state_name)
            if s_id:
                obj = District(name=dist_name, StateID=s_id)
                db.add(obj)
    db.flush()
    for dist_name, _ in district_data:
        obj = db.query(District).filter(District.name == dist_name).first()
        if obj:
            district_ids[dist_name] = obj.id
    print(f"  Districts: {len(district_data)}")

    # ── Court ──────────────────────────────────────────────────────────────────
    court_data = [
        ("JMFC I Court, Bengaluru", "Bengaluru Urban", "Karnataka"),
        ("JMFC II Court, Bengaluru", "Bengaluru Urban", "Karnataka"),
        ("City Civil Court, Bengaluru", "Bengaluru Urban", "Karnataka"),
        ("District Session Court, Mysuru", "Mysuru", "Karnataka"),
        ("JMFC Court, Mysuru", "Mysuru", "Karnataka"),
        ("District Court, Belagavi", "Belagavi", "Karnataka"),
        ("High Court of Karnataka, Bengaluru", "Bengaluru Urban", "Karnataka"),
    ]
    for court_name, dist_name, state_name in court_data:
        obj = db.query(Court).filter(Court.name == court_name).first()
        if not obj:
            d_id = district_ids.get(dist_name)
            s_id = state_ids.get(state_name)
            if d_id and s_id:
                obj = Court(name=court_name, DistrictID=d_id, StateID=s_id)
                db.add(obj)
    db.flush()
    print(f"  Courts: {len(court_data)}")

    # ── Unit Type ──────────────────────────────────────────────────────────────
    unit_type_obj = db.query(UnitType).filter(UnitType.name == "Police Station").first()
    if not unit_type_obj:
        unit_type_obj = UnitType(name="Police Station", CityDistState="District", Hierarchy=1)
        db.add(unit_type_obj)
    db.flush()
    unit_type_id = unit_type_obj.id

    # ── Unit (Police Station) ──────────────────────────────────────────────────
    unit_data = [
        ("Cubbon Park PS", "Bengaluru Urban", "Karnataka"),
        ("Commercial Street PS", "Bengaluru Urban", "Karnataka"),
        ("Shivajinagar PS", "Bengaluru Urban", "Karnataka"),
        ("Koramangala PS", "Bengaluru Urban", "Karnataka"),
        ("Whitefield PS", "Bengaluru Urban", "Karnataka"),
        ("Indiranagar PS", "Bengaluru Urban", "Karnataka"),
        ("Malleshwaram PS", "Bengaluru Urban", "Karnataka"),
        ("Devaraja PS", "Mysuru", "Karnataka"),
        ("Nazarbad PS", "Mysuru", "Karnataka"),
        ("Jayalakshmipuram PS", "Mysuru", "Karnataka"),
        ("Tilak Nagar PS", "Belagavi", "Karnataka"),
        ("Market PS", "Belagavi", "Karnataka"),
    ]
    unit_ids = {}
    nat_indian = nat_ids.get("Indian")
    for unit_name, dist_name, state_name in unit_data:
        obj = db.query(Unit).filter(Unit.name == unit_name).first()
        if not obj:
            d_id = district_ids.get(dist_name)
            s_id = state_ids.get(state_name)
            if d_id and s_id:
                obj = Unit(
                    name=unit_name,
                    TypeID=unit_type_id,
                    NationalityID=nat_indian,
                    StateID=s_id,
                    DistrictID=d_id
                )
                db.add(obj)
    db.flush()
    for unit_name, _, _ in unit_data:
        obj = db.query(Unit).filter(Unit.name == unit_name).first()
        if obj:
            unit_ids[unit_name] = obj.id
    print(f"  Police Stations (Units): {len(unit_data)}")

    # ── Rank ───────────────────────────────────────────────────────────────────
    ranks = [
        ("Constable", 1), ("Head Constable", 2), ("Assistant Sub-Inspector", 3),
        ("Sub-Inspector", 4), ("Inspector", 5), ("Deputy Superintendent of Police", 6),
        ("Superintendent of Police", 7),
    ]
    rank_ids = {}
    for rank_name, hierarchy in ranks:
        obj = db.query(Rank).filter(Rank.name == rank_name).first()
        if not obj:
            obj = Rank(name=rank_name, Hierarchy=hierarchy)
            db.add(obj)
    db.flush()
    for rank_name, _ in ranks:
        obj = db.query(Rank).filter(Rank.name == rank_name).first()
        if obj:
            rank_ids[rank_name] = obj.id
    print(f"  Ranks: {len(ranks)}")

    # ── Designation ────────────────────────────────────────────────────────────
    designations = [
        ("Station Writer", 1), ("Investigating Officer", 2),
        ("Station House Officer (SHO)", 3), ("Circle Inspector", 4),
        ("Crime Inspector", 5),
    ]
    desig_ids = {}
    for desig_name, sort_order in designations:
        obj = db.query(Designation).filter(Designation.name == desig_name).first()
        if not obj:
            obj = Designation(name=desig_name, SortOrder=sort_order)
            db.add(obj)
    db.flush()
    for desig_name, _ in designations:
        obj = db.query(Designation).filter(Designation.name == desig_name).first()
        if obj:
            desig_ids[desig_name] = obj.id
    print(f"  Designations: {len(designations)}")

    # ── Employee ───────────────────────────────────────────────────────────────
    male_id = db.query(GenderMaster).filter(GenderMaster.name == "Male").first()
    male_id = male_id.id if male_id else None
    female_id = db.query(GenderMaster).filter(GenderMaster.name == "Female").first()
    female_id = female_id.id if female_id else None

    employee_data = [
        ("KA10001", "Rajesh Kumar", "Sub-Inspector", "Investigating Officer", "Cubbon Park PS", "Bengaluru Urban", "Karnataka", male_id),
        ("KA10002", "Priya Sharma", "Inspector", "Station House Officer (SHO)", "Cubbon Park PS", "Bengaluru Urban", "Karnataka", female_id),
        ("KA10003", "Suresh Patil", "Head Constable", "Station Writer", "Commercial Street PS", "Bengaluru Urban", "Karnataka", male_id),
        ("KA10004", "Anitha Gowda", "Sub-Inspector", "Investigating Officer", "Commercial Street PS", "Bengaluru Urban", "Karnataka", female_id),
        ("KA10005", "Vikram Singh", "Inspector", "Station House Officer (SHO)", "Shivajinagar PS", "Bengaluru Urban", "Karnataka", male_id),
        ("KA10006", "Deepak Reddy", "Sub-Inspector", "Investigating Officer", "Koramangala PS", "Bengaluru Urban", "Karnataka", male_id),
        ("KA10007", "Kavitha Nair", "Assistant Sub-Inspector", "Station Writer", "Whitefield PS", "Bengaluru Urban", "Karnataka", female_id),
        ("KA10008", "Mohan Das", "Sub-Inspector", "Investigating Officer", "Indiranagar PS", "Bengaluru Urban", "Karnataka", male_id),
        ("KA10009", "Ramesh Rao", "Inspector", "Circle Inspector", "Devaraja PS", "Mysuru", "Karnataka", male_id),
        ("KA10010", "Sunita Patel", "Sub-Inspector", "Investigating Officer", "Devaraja PS", "Mysuru", "Karnataka", female_id),
        ("KA10011", "Anil Joshi", "Head Constable", "Station Writer", "Nazarbad PS", "Mysuru", "Karnataka", male_id),
        ("KA10012", "Geeta Mehta", "Sub-Inspector", "Investigating Officer", "Tilak Nagar PS", "Belagavi", "Karnataka", female_id),
    ]
    for (kgid, name, rank_name, desig_name, unit_name, dist_name, state_name, gender_id) in employee_data:
        obj = db.query(Employee).filter(Employee.KGID == kgid).first()
        if not obj:
            u_id = unit_ids.get(unit_name)
            d_id = district_ids.get(dist_name)
            r_id = rank_ids.get(rank_name)
            dg_id = desig_ids.get(desig_name)
            if u_id and d_id and r_id and dg_id:
                obj = Employee(
                    KGID=kgid,
                    FirstName=name,
                    UnitID=u_id,
                    DistrictID=d_id,
                    RankID=r_id,
                    DesignationID=dg_id,
                    GenderID=gender_id,
                    AppointmentDate=date(2015, 6, 1),
                )
                db.add(obj)
    db.flush()
    print(f"  Employees: {len(employee_data)}")

    # ── Acts ───────────────────────────────────────────────────────────────────
    acts = [
        ("IPC", "Indian Penal Code", "IPC"),
        ("KPA", "Karnataka Police Act", "KPA"),
        ("NDPS", "Narcotic Drugs and Psychotropic Substances Act", "NDPS"),
        ("POCSO", "Protection of Children from Sexual Offences Act", "POCSO"),
        ("IT_ACT", "Information Technology Act", "IT Act"),
        ("SC_ST", "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act", "SC/ST Act"),
        ("MV_ACT", "Motor Vehicles Act", "MV Act"),
    ]
    for act_code, act_desc, short_name in acts:
        obj = db.query(Act).filter(Act.ActCode == act_code).first()
        if not obj:
            obj = Act(ActCode=act_code, ActDescription=act_desc, ShortName=short_name)
            db.add(obj)
    db.flush()
    print(f"  Acts: {len(acts)}")

    # ── Sections ───────────────────────────────────────────────────────────────
    sections = [
        ("IPC", "302", "Murder"),
        ("IPC", "307", "Attempt to murder"),
        ("IPC", "324", "Voluntarily causing hurt by dangerous weapons"),
        ("IPC", "379", "Theft"),
        ("IPC", "380", "Theft in dwelling house"),
        ("IPC", "392", "Robbery"),
        ("IPC", "395", "Dacoity"),
        ("IPC", "420", "Cheating and dishonestly inducing delivery of property"),
        ("IPC", "498A", "Husband or relative of husband of a woman subjecting her to cruelty"),
        ("IPC", "506", "Criminal intimidation"),
        ("IPC", "376", "Rape"),
        ("IPC", "354", "Assault or criminal force to woman"),
        ("KPA", "92", "Punishment for street offences"),
        ("KPA", "102", "Police may arrest without warrant"),
        ("NDPS", "20", "Punishment for cannabis possession"),
        ("NDPS", "22", "Punishment for contravention of psychotropic substances"),
        ("POCSO", "4", "Penetrative sexual assault"),
        ("POCSO", "8", "Sexual assault"),
        ("IT_ACT", "66", "Computer related offences"),
        ("IT_ACT", "66C", "Identity theft"),
        ("SC_ST", "3", "Offences atrocities"),
        ("MV_ACT", "112", "Driving at excessive speed"),
        ("MV_ACT", "184", "Driving dangerously"),
    ]
    for act_code, sec_code, sec_desc in sections:
        obj = db.query(Section).filter(Section.ActCode == act_code, Section.SectionCode == sec_code).first()
        if not obj:
            obj = Section(ActCode=act_code, SectionCode=sec_code, SectionDescription=sec_desc)
            db.add(obj)
    db.flush()
    print(f"  Sections: {len(sections)}")

    # ── Crime Heads (Major) ────────────────────────────────────────────────────
    crime_head_data = [
        "Crimes Against Body",
        "Crimes Against Property",
        "Crimes Against Women",
        "Crimes Against Children",
        "Narcotics",
        "Economic Offences",
        "Cyber Crimes",
        "Public Nuisance",
        "Road Accidents",
    ]
    crime_head_ids = {}
    for ch_name in crime_head_data:
        obj = db.query(CrimeHead).filter(CrimeHead.CrimeGroupName == ch_name).first()
        if not obj:
            obj = CrimeHead(CrimeGroupName=ch_name)
            db.add(obj)
    db.flush()
    for ch_name in crime_head_data:
        obj = db.query(CrimeHead).filter(CrimeHead.CrimeGroupName == ch_name).first()
        if obj:
            crime_head_ids[ch_name] = obj.id
    print(f"  Crime Major Heads: {len(crime_head_data)}")

    # ── Crime Sub Heads (Minor) ────────────────────────────────────────────────
    crime_sub_head_data = [
        ("Murder", "Crimes Against Body", 1),
        ("Attempt to Murder", "Crimes Against Body", 2),
        ("Assault", "Crimes Against Body", 3),
        ("Kidnapping", "Crimes Against Body", 4),
        ("House Theft", "Crimes Against Property", 1),
        ("Chain Snatching", "Crimes Against Property", 2),
        ("Robbery", "Crimes Against Property", 3),
        ("Dacoity", "Crimes Against Property", 4),
        ("Vehicle Theft", "Crimes Against Property", 5),
        ("Burglary", "Crimes Against Property", 6),
        ("Dowry Harassment", "Crimes Against Women", 1),
        ("Rape", "Crimes Against Women", 2),
        ("Molestation", "Crimes Against Women", 3),
        ("Domestic Violence", "Crimes Against Women", 4),
        ("Sexual Assault on Minor", "Crimes Against Children", 1),
        ("Child Trafficking", "Crimes Against Children", 2),
        ("Drug Peddling", "Narcotics", 1),
        ("Possession", "Narcotics", 2),
        ("Fraud", "Economic Offences", 1),
        ("Cheating", "Economic Offences", 2),
        ("Online Fraud", "Cyber Crimes", 1),
        ("Hacking", "Cyber Crimes", 2),
        ("Street Fighting", "Public Nuisance", 1),
        ("Public Drunkenness", "Public Nuisance", 2),
        ("Hit and Run", "Road Accidents", 1),
        ("Rash Driving", "Road Accidents", 2),
    ]
    for sub_name, major_name, seq in crime_sub_head_data:
        obj = db.query(CrimeSubHead).filter(CrimeSubHead.CrimeHeadName == sub_name).first()
        if not obj:
            major_id = crime_head_ids.get(major_name)
            if major_id:
                obj = CrimeSubHead(CrimeHeadID=major_id, CrimeHeadName=sub_name, SeqID=seq)
                db.add(obj)
    db.flush()
    print(f"  Crime Sub Heads (Minor): {len(crime_sub_head_data)}")

    db.commit()
    print("\n[SUCCESS] FIR lookup seeding complete!")
    print("   All FIR form dropdowns will now populate correctly.")


if __name__ == "__main__":
    # Ensure all model tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_fir_lookups(db)
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
