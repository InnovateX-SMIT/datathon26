from typing import Optional, List, Tuple
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from backend.models import (
    CaseMaster, Inv_OccuranceTime, ComplainantDetails, FIRVictim, Accused,
    ArrestSurrender, InvArrestSurrenderAccused, ChargesheetDetails,
    CaseCategory, GravityOffence, CaseStatusMaster, CasteMaster, ReligionMaster,
    OccupationMaster, GenderMaster, NationalityMaster, BloodGroupMaster,
    State, District, Court, UnitType, Unit, Rank, Designation, Employee,
    Act, Section, ActSectionAssociation, CrimeHead, CrimeSubHead, CrimeHeadActSection
)
from backend.repositories.admin_repository import AdminRepository
import json

class FIRRepository:
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)

    def _log_audit(self, user_id: Optional[int], action: str, entity_type: str, entity_id: int, details: dict):
        if user_id is not None:
            self.admin_repo.create_audit_log(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=json.dumps(details)
            )

    # ── CaseMaster CRUD & Eager Queries ──────────────────────────────────────────

    def create_case(
        self,
        crime_no: str,
        case_no: str,
        registered_date: date,
        police_person_id: int,
        police_station_id: int,
        case_category_id: int,
        gravity_offence_id: int,
        crime_major_head_id: int,
        crime_minor_head_id: int,
        case_status_id: int,
        court_id: int,
        brief_facts: Optional[str] = None,
        dataset_id: Optional[int] = None,
        # Occurance Time details
        incident_from_date: Optional[datetime] = None,
        incident_to_date: Optional[datetime] = None,
        info_received_ps_date: Optional[datetime] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        occurrence_brief_facts: Optional[str] = None,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> CaseMaster:
        """
        Creates a new CaseMaster record and its 1:1 companion Inv_OccuranceTime record.
        """
        case = CaseMaster(
            CrimeNo=crime_no,
            CaseNo=case_no,
            CrimeRegisteredDate=registered_date,
            PolicePersonID=police_person_id,
            PoliceStationID=police_station_id,
            CaseCategoryID=case_category_id,
            GravityOffenceID=gravity_offence_id,
            CrimeMajorHeadID=crime_major_head_id,
            CrimeMinorHeadID=crime_minor_head_id,
            CaseStatusID=case_status_id,
            CourtID=court_id,
            BriefFacts=brief_facts,
            dataset_id=dataset_id
        )
        self.db.add(case)
        self.db.flush()

        # Create occurrence time if mandatory dates are provided
        if incident_from_date is not None and info_received_ps_date is not None:
            occurrence = Inv_OccuranceTime(
                CaseMasterID=case.id,
                IncidentFromDate=incident_from_date,
                IncidentToDate=incident_to_date,
                InfoReceivedPSDate=info_received_ps_date,
                latitude=latitude,
                longitude=longitude,
                BriefFacts=occurrence_brief_facts if occurrence_brief_facts else brief_facts
            )
            self.db.add(occurrence)
            self.db.flush()

        if commit:
            self.db.commit()
            self.db.refresh(case)

        self._log_audit(
            user_id=performed_by_user_id,
            action="CASE_CREATED",
            entity_type="case_master",
            entity_id=case.id,
            details={"CrimeNo": crime_no, "CaseNo": case_no}
        )
        return case

    def get_case_by_id(self, case_id: int) -> Optional[CaseMaster]:
        """
        Retrieves a CaseMaster record with related entities eagerly loaded to avoid N+1 queries.
        """
        return (
            self.db.query(CaseMaster)
            .options(
                joinedload(CaseMaster.occurrence_time),
                selectinload(CaseMaster.complainants),
                selectinload(CaseMaster.victims),
                selectinload(CaseMaster.accused),
                selectinload(CaseMaster.arrest_surrenders).selectinload(ArrestSurrender.all_accused),
                selectinload(CaseMaster.chargesheets),
                selectinload(CaseMaster.act_sections)
            )
            .filter(CaseMaster.id == case_id)
            .first()
        )

    def delete_case(self, case_id: int, performed_by_user_id: Optional[int] = None) -> bool:
        """
        Deletes a CaseMaster record by ID. Manually deletes children first to avoid ForeignKey constraint failures.
        """
        case = self.db.query(CaseMaster).filter(CaseMaster.id == case_id).first()
        if not case:
            return False
        
        crime_no = case.CrimeNo
        case_no = case.CaseNo
        
        # Explicitly delete child records in correct order to respect ForeignKey constraints
        self.db.query(Inv_OccuranceTime).filter(Inv_OccuranceTime.CaseMasterID == case_id).delete()
        self.db.query(ComplainantDetails).filter(ComplainantDetails.CaseMasterID == case_id).delete()
        self.db.query(FIRVictim).filter(FIRVictim.CaseMasterID == case_id).delete()
        self.db.query(Accused).filter(Accused.CaseMasterID == case_id).delete()
        self.db.query(ArrestSurrender).filter(ArrestSurrender.CaseMasterID == case_id).delete()
        self.db.query(ChargesheetDetails).filter(ChargesheetDetails.CaseMasterID == case_id).delete()
        self.db.query(ActSectionAssociation).filter(ActSectionAssociation.CaseMasterID == case_id).delete()
        
        self.db.delete(case)
        self.db.commit()
        
        self._log_audit(
            user_id=performed_by_user_id,
            action="CASE_DELETED",
            entity_type="case_master",
            entity_id=case_id,
            details={"CrimeNo": crime_no, "CaseNo": case_no}
        )
        return True

    def update_case(
        self,
        case_id: int,
        crime_no: str,
        case_no: str,
        registered_date: date,
        police_person_id: int,
        police_station_id: int,
        case_category_id: int,
        gravity_offence_id: int,
        crime_major_head_id: int,
        crime_minor_head_id: int,
        case_status_id: int,
        court_id: int,
        brief_facts: Optional[str] = None,
        # Occurance Time details
        incident_from_date: Optional[datetime] = None,
        incident_to_date: Optional[datetime] = None,
        info_received_ps_date: Optional[datetime] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        occurrence_brief_facts: Optional[str] = None,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> Optional[CaseMaster]:
        """
        Updates an existing CaseMaster record and its 1:1 companion Inv_OccuranceTime record.
        """
        case = self.db.query(CaseMaster).filter(CaseMaster.id == case_id).first()
        if not case:
            return None
            
        case.CrimeNo = crime_no
        case.CaseNo = case_no
        case.CrimeRegisteredDate = registered_date
        case.PolicePersonID = police_person_id
        case.PoliceStationID = police_station_id
        case.CaseCategoryID = case_category_id
        case.GravityOffenceID = gravity_offence_id
        case.CrimeMajorHeadID = crime_major_head_id
        case.CrimeMinorHeadID = crime_minor_head_id
        case.CaseStatusID = case_status_id
        case.CourtID = court_id
        case.BriefFacts = brief_facts
        
        # Occurrence time updates
        if incident_from_date is not None and info_received_ps_date is not None:
            if not case.occurrence_time:
                occurrence = Inv_OccuranceTime(
                    CaseMasterID=case_id,
                    IncidentFromDate=incident_from_date,
                    IncidentToDate=incident_to_date,
                    InfoReceivedPSDate=info_received_ps_date,
                    latitude=latitude,
                    longitude=longitude,
                    BriefFacts=occurrence_brief_facts if occurrence_brief_facts else brief_facts
                )
                self.db.add(occurrence)
            else:
                case.occurrence_time.IncidentFromDate = incident_from_date
                case.occurrence_time.IncidentToDate = incident_to_date
                case.occurrence_time.InfoReceivedPSDate = info_received_ps_date
                case.occurrence_time.latitude = latitude
                case.occurrence_time.longitude = longitude
                case.occurrence_time.BriefFacts = occurrence_brief_facts if occurrence_brief_facts else brief_facts
        
        if commit:
            self.db.commit()
            self.db.refresh(case)
            
        self._log_audit(
            user_id=performed_by_user_id,
            action="CASE_UPDATED",
            entity_type="case_master",
            entity_id=case.id,
            details={"CrimeNo": crime_no, "CaseNo": case_no}
        )
        return case

    def list_cases(
        self,
        page: int = 1,
        page_size: int = 10,
        district_id: Optional[int] = None,
        case_status_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        active_dataset_id: Optional[int] = None
    ) -> Tuple[List[CaseMaster], int]:
        """
        Lists and paginates CaseMaster records with optional filters.
        """
        query = self.db.query(CaseMaster)

        if active_dataset_id is not None:
            query = query.filter(CaseMaster.dataset_id == active_dataset_id)

        if district_id is not None:
            query = query.join(CaseMaster.police_station).filter(Unit.DistrictID == district_id)

        if case_status_id is not None:
            query = query.filter(CaseMaster.CaseStatusID == case_status_id)

        if start_date is not None or end_date is not None:
            query = query.join(CaseMaster.occurrence_time)
            if start_date is not None:
                query = query.filter(Inv_OccuranceTime.IncidentFromDate >= start_date)
            if end_date is not None:
                query = query.filter(Inv_OccuranceTime.IncidentFromDate <= end_date)

        total_count = query.count()
        offset = (page - 1) * page_size
        
        # Eager load relations for the paginated result
        cases = (
            query.options(
                joinedload(CaseMaster.occurrence_time),
                selectinload(CaseMaster.complainants),
                selectinload(CaseMaster.victims),
                selectinload(CaseMaster.accused)
            )
            .order_by(CaseMaster.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return cases, total_count

    # ── Transactional Scoped Adders ──────────────────────────────────────────────

    def add_accused_to_case(
        self,
        case_id: int,
        name: str,
        age: Optional[int] = None,
        gender_id: Optional[int] = None,
        person_id: Optional[str] = None,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> Accused:
        accused = Accused(
            CaseMasterID=case_id,
            AccusedName=name,
            AgeYear=age,
            GenderID=gender_id,
            PersonID=person_id
        )
        self.db.add(accused)
        if commit:
            self.db.commit()
            self.db.refresh(accused)
        else:
            self.db.flush()

        self._log_audit(
            user_id=performed_by_user_id,
            action="ACCUSED_ADDED_TO_CASE",
            entity_type="accused",
            entity_id=accused.id,
            details={"case_id": case_id, "name": name}
        )
        return accused

    def add_victim_to_case(
        self,
        case_id: int,
        name: str,
        age: Optional[int] = None,
        gender_id: Optional[int] = None,
        victim_police: Optional[str] = None,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> FIRVictim:
        victim = FIRVictim(
            CaseMasterID=case_id,
            VictimName=name,
            AgeYear=age,
            GenderID=gender_id,
            VictimPolice=victim_police
        )
        self.db.add(victim)
        if commit:
            self.db.commit()
            self.db.refresh(victim)
        else:
            self.db.flush()

        self._log_audit(
            user_id=performed_by_user_id,
            action="VICTIM_ADDED_TO_CASE",
            entity_type="victim",
            entity_id=victim.id,
            details={"case_id": case_id, "name": name}
        )
        return victim

    def add_complainant_to_case(
        self,
        case_id: int,
        name: str,
        age: Optional[int] = None,
        occupation_id: Optional[int] = None,
        religion_id: Optional[int] = None,
        caste_id: Optional[int] = None,
        gender_id: Optional[int] = None,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> ComplainantDetails:
        complainant = ComplainantDetails(
            CaseMasterID=case_id,
            ComplainantName=name,
            AgeYear=age,
            OccupationID=occupation_id,
            ReligionID=religion_id,
            CasteID=caste_id,
            GenderID=gender_id
        )
        self.db.add(complainant)
        if commit:
            self.db.commit()
            self.db.refresh(complainant)
        else:
            self.db.flush()

        self._log_audit(
            user_id=performed_by_user_id,
            action="COMPLAINANT_ADDED_TO_CASE",
            entity_type="complainant_details",
            entity_id=complainant.id,
            details={"case_id": case_id, "name": name}
        )
        return complainant

    def record_arrest_surrender(
        self,
        case_id: int,
        type_id: int,
        date_val: date,
        state_id: int,
        district_id: int,
        station_id: int,
        io_id: int,
        court_id: int,
        accused_master_id: int,
        is_accused: bool = True,
        is_complainant_accused: bool = False,
        other_accused_ids: Optional[List[int]] = None,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> ArrestSurrender:
        """
        Persists an ArrestSurrender event, mapping the primary accused and any joint accused.
        """
        arrest = ArrestSurrender(
            CaseMasterID=case_id,
            ArrestSurrenderTypeID=type_id,
            ArrestSurrenderDate=date_val,
            ArrestSurrenderStateId=state_id,
            ArrestSurrenderDistrictId=district_id,
            PoliceStationID=station_id,
            IOID=io_id,
            CourtID=court_id,
            AccusedMasterID=accused_master_id,
            IsAccused=is_accused,
            IsComplainantAccused=is_complainant_accused
        )
        self.db.add(arrest)
        self.db.flush()

        # Track mappings in the junction table via all_accused ORM collection
        primary_acc = self.db.query(Accused).filter(Accused.id == accused_master_id).first()
        if primary_acc:
            arrest.all_accused.append(primary_acc)

        if other_accused_ids:
            for aid in other_accused_ids:
                if aid != accused_master_id:
                    other_acc = self.db.query(Accused).filter(Accused.id == aid).first()
                    if other_acc:
                        arrest.all_accused.append(other_acc)

        if commit:
            self.db.commit()
            self.db.refresh(arrest)
        else:
            self.db.flush()

        self._log_audit(
            user_id=performed_by_user_id,
            action="ARREST_SURRENDER_RECORDED",
            entity_type="arrest_surrender",
            entity_id=arrest.id,
            details={"case_id": case_id, "primary_accused_id": accused_master_id}
        )
        return arrest

    def record_chargesheet(
        self,
        case_id: int,
        date_val: datetime,
        cs_type: str,
        police_person_id: int,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> ChargesheetDetails:
        cs = ChargesheetDetails(
            CaseMasterID=case_id,
            csdate=date_val,
            cstype=cs_type,
            PolicePersonID=police_person_id
        )
        self.db.add(cs)
        if commit:
            self.db.commit()
            self.db.refresh(cs)
        else:
            self.db.flush()

        self._log_audit(
            user_id=performed_by_user_id,
            action="CHARGESHEET_RECORDED",
            entity_type="chargesheet_details",
            entity_id=cs.id,
            details={"case_id": case_id, "cstype": cs_type}
        )
        return cs

    def associate_act_section_with_case(
        self,
        case_id: int,
        act_code: str,
        section_code: str,
        act_order_id: Optional[int] = None,
        section_order_id: Optional[int] = None,
        performed_by_user_id: Optional[int] = None,
        commit: bool = True
    ) -> ActSectionAssociation:
        association = ActSectionAssociation(
            CaseMasterID=case_id,
            ActCode=act_code,
            SectionCode=section_code,
            ActOrderID=act_order_id,
            SectionOrderID=section_order_id
        )
        self.db.add(association)
        if commit:
            self.db.commit()
            self.db.refresh(association)
        else:
            self.db.flush()

        self._log_audit(
            user_id=performed_by_user_id,
            action="ACT_SECTION_ASSOCIATED",
            entity_type="act_section_association",
            entity_id=case_id,
            details={"case_id": case_id, "act_code": act_code, "section_code": section_code}
        )
        return association

    # ── Lookup / Master Tables Query Methods ─────────────────────────────────────

    def list_case_categories(self) -> List[CaseCategory]:
        return self.db.query(CaseCategory).filter(CaseCategory.active == True).order_by(CaseCategory.sort_order.asc()).all()

    def list_gravity_offences(self) -> List[GravityOffence]:
        return self.db.query(GravityOffence).filter(GravityOffence.active == True).order_by(GravityOffence.sort_order.asc()).all()

    def list_case_statuses(self) -> List[CaseStatusMaster]:
        return self.db.query(CaseStatusMaster).filter(CaseStatusMaster.active == True).order_by(CaseStatusMaster.sort_order.asc()).all()

    def list_castes(self) -> List[CasteMaster]:
        return self.db.query(CasteMaster).filter(CasteMaster.active == True).order_by(CasteMaster.sort_order.asc()).all()

    def list_religions(self) -> List[ReligionMaster]:
        return self.db.query(ReligionMaster).filter(ReligionMaster.active == True).order_by(ReligionMaster.sort_order.asc()).all()

    def list_occupations(self) -> List[OccupationMaster]:
        return self.db.query(OccupationMaster).filter(OccupationMaster.active == True).order_by(OccupationMaster.sort_order.asc()).all()

    def list_genders(self) -> List[GenderMaster]:
        return self.db.query(GenderMaster).filter(GenderMaster.active == True).order_by(GenderMaster.sort_order.asc()).all()

    def list_nationalities(self) -> List[NationalityMaster]:
        return self.db.query(NationalityMaster).filter(NationalityMaster.active == True).order_by(NationalityMaster.sort_order.asc()).all()

    def list_blood_groups(self) -> List[BloodGroupMaster]:
        return self.db.query(BloodGroupMaster).filter(BloodGroupMaster.active == True).order_by(BloodGroupMaster.sort_order.asc()).all()

    def list_states(self) -> List[State]:
        return self.db.query(State).filter(State.active == True).order_by(State.sort_order.asc()).all()

    def list_districts(self, state_id: Optional[int] = None) -> List[District]:
        q = self.db.query(District).filter(District.active == True)
        if state_id is not None:
            q = q.filter(District.StateID == state_id)
        return q.order_by(District.sort_order.asc()).all()

    def list_courts(self, district_id: Optional[int] = None) -> List[Court]:
        q = self.db.query(Court).filter(Court.active == True)
        if district_id is not None:
            q = q.filter(Court.DistrictID == district_id)
        return q.order_by(Court.sort_order.asc()).all()

    def list_units(self, district_id: Optional[int] = None) -> List[Unit]:
        q = self.db.query(Unit).filter(Unit.active == True)
        if district_id is not None:
            q = q.filter(Unit.DistrictID == district_id)
        return q.order_by(Unit.sort_order.asc()).all()

    def list_ranks(self) -> List[Rank]:
        return self.db.query(Rank).filter(Rank.active == True).order_by(Rank.sort_order.asc()).all()

    def list_designations(self) -> List[Designation]:
        return self.db.query(Designation).filter(Designation.active == True).order_by(Designation.sort_order.asc()).all()

    def list_employees(self, unit_id: Optional[int] = None) -> List[Employee]:
        q = self.db.query(Employee).filter(Employee.active == True)
        if unit_id is not None:
            q = q.filter(Employee.UnitID == unit_id)
        return q.order_by(Employee.id.desc()).all()

    def list_acts(self) -> List[Act]:
        return self.db.query(Act).filter(Act.active == True).all()

    def list_sections(self, act_code: Optional[str] = None) -> List[Section]:
        q = self.db.query(Section).filter(Section.active == True)
        if act_code is not None:
            q = q.filter(Section.ActCode == act_code)
        return q.all()

    def list_crime_heads(self) -> List[CrimeHead]:
        return self.db.query(CrimeHead).filter(CrimeHead.active == True).order_by(CrimeHead.CrimeGroupName.asc()).all()

    def list_crime_sub_heads(self, crime_head_id: Optional[int] = None) -> List[CrimeSubHead]:
        q = self.db.query(CrimeSubHead)
        if crime_head_id is not None:
            q = q.filter(CrimeSubHead.CrimeHeadID == crime_head_id)
        return q.order_by(CrimeSubHead.SeqID.asc()).all()
