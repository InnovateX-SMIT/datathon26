from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List, Tuple

from backend.repositories.fir_repository import FIRRepository
from backend.models import CaseMaster, Unit, ComplainantDetails, FIRVictim, Accused
from backend.schemas.fir import (
    CaseMasterCreate, CaseMasterResponse,
    StateDTO, DistrictDTO, CourtDTO, UnitDTO, RankDTO, DesignationDTO, EmployeeDTO,
    CaseCategoryDTO, GravityOffenceDTO, CaseStatusDTO, CasteDTO, ReligionDTO, OccupationDTO,
    GenderDTO, NationalityDTO, BloodGroupDTO, ActDTO, SectionDTO, CrimeHeadDTO, CrimeSubHeadDTO
)
from backend.core.validation import (
    validate_crime_no, validate_case_no, generate_crime_no, generate_case_no,
    validate_latitude, validate_longitude, validate_age
)

class FIRService:
    """
    FIR Service orchestrating validations, CrimeNo/CaseNo autogeneration, 
    business logic rules, and DTO serializations.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = FIRRepository(db)

    def get_next_serial_number(self, station_id: int, year: int) -> int:
        """
        Calculates the next incremental serial number for the given PS unit and year.
        """
        cases = self.db.query(CaseMaster).filter(
            CaseMaster.PoliceStationID == station_id,
            CaseMaster.CrimeNo.like(f"_________{year:04d}%")
        ).all()
        
        serials = []
        for c in cases:
            if c.CrimeNo and len(c.CrimeNo) == 18:
                try:
                    # Serial is the last 5 digits per official spec
                    serials.append(int(c.CrimeNo[-5:]))
                except ValueError:
                    pass
        return max(serials) + 1 if serials else 1

    def create_case(
        self, 
        case_dto: CaseMasterCreate, 
        dataset_id: Optional[int] = None, 
        user_id: Optional[int] = None
    ) -> CaseMasterResponse:
        """
        Creates a new FIR case, enforcing latitude/longitude/age validations, 
        generating CrimeNo/CaseNo, inserting child associations, and returning Response DTO.
        """
        # Validate coordinates
        if case_dto.occurrence_time:
            if not validate_latitude(case_dto.occurrence_time.latitude):
                raise ValueError(f"Invalid latitude: {case_dto.occurrence_time.latitude}. Must be between -90 and 90.")
            if not validate_longitude(case_dto.occurrence_time.longitude):
                raise ValueError(f"Invalid longitude: {case_dto.occurrence_time.longitude}. Must be between -180 and 180.")

        # Validate ages
        for comp in case_dto.complainants:
            if not validate_age(comp.AgeYear):
                raise ValueError(f"Invalid complainant age: {comp.AgeYear}. Must be between 0 and 125.")
        for vic in case_dto.victims:
            if not validate_age(vic.AgeYear):
                raise ValueError(f"Invalid victim age: {vic.AgeYear}. Must be between 0 and 125.")
        for acc in case_dto.accused:
            if not validate_age(acc.AgeYear):
                raise ValueError(f"Invalid accused age: {acc.AgeYear}. Must be between 0 and 125.")

        # Derive or validate CrimeNo and CaseNo
        crime_no = case_dto.CrimeNo
        case_no = case_dto.CaseNo

        if crime_no:
            if not validate_crime_no(crime_no):
                raise ValueError(f"Invalid CrimeNo format: {crime_no}. Must be 18 digits containing a valid year.")
            if not case_no:
                case_no = generate_case_no(crime_no)
            elif not validate_case_no(case_no):
                raise ValueError(f"Invalid CaseNo format: {case_no}. Must be 9 digits containing a valid year.")
        else:
            # Look up Unit's District
            unit = self.db.query(Unit).filter(Unit.id == case_dto.PoliceStationID).first()
            if not unit:
                raise ValueError(f"Police station Unit with ID {case_dto.PoliceStationID} not found.")
            
            category = case_dto.CaseCategoryID
            district = unit.DistrictID
            station = case_dto.PoliceStationID
            year = case_dto.CrimeRegisteredDate.year if case_dto.CrimeRegisteredDate else datetime.utcnow().year
            
            serial = self.get_next_serial_number(station, year)
            crime_no = generate_crime_no(category, district, station, year, serial)
            case_no = generate_case_no(crime_no)

        # Validate uniqueness of CrimeNo
        existing = self.db.query(CaseMaster).filter(CaseMaster.CrimeNo == crime_no).first()
        if existing:
            raise ValueError(f"Duplicate Case: A CaseMaster with CrimeNo {crime_no} already exists.")

        # Extract occurrence fields
        incident_from = None
        incident_to = None
        info_received = None
        lat = None
        lon = None
        occ_facts = None
        if case_dto.occurrence_time:
            incident_from = case_dto.occurrence_time.IncidentFromDate
            incident_to = case_dto.occurrence_time.IncidentToDate
            info_received = case_dto.occurrence_time.InfoReceivedPSDate
            lat = case_dto.occurrence_time.latitude
            lon = case_dto.occurrence_time.longitude
            occ_facts = case_dto.occurrence_time.BriefFacts

        # Create master case
        case_record = self.repo.create_case(
            crime_no=crime_no,
            case_no=case_no,
            registered_date=case_dto.CrimeRegisteredDate or date.today(),
            police_person_id=case_dto.PolicePersonID,
            police_station_id=case_dto.PoliceStationID,
            case_category_id=case_dto.CaseCategoryID,
            gravity_offence_id=case_dto.GravityOffenceID,
            crime_major_head_id=case_dto.CrimeMajorHeadID,
            crime_minor_head_id=case_dto.CrimeMinorHeadID,
            case_status_id=case_dto.CaseStatusID,
            court_id=case_dto.CourtID,
            brief_facts=case_dto.BriefFacts,
            dataset_id=dataset_id or case_dto.dataset_id,
            incident_from_date=incident_from,
            incident_to_date=incident_to,
            info_received_ps_date=info_received,
            latitude=lat,
            longitude=lon,
            occurrence_brief_facts=occ_facts,
            performed_by_user_id=user_id
        )

        # Add complainants
        for comp in case_dto.complainants:
            self.repo.add_complainant_to_case(
                case_id=case_record.id,
                name=comp.ComplainantName,
                age=comp.AgeYear,
                occupation_id=comp.OccupationID,
                religion_id=comp.ReligionID,
                caste_id=comp.CasteID,
                gender_id=comp.GenderID,
                performed_by_user_id=user_id
            )

        # Add victims
        for vic in case_dto.victims:
            self.repo.add_victim_to_case(
                case_id=case_record.id,
                name=vic.VictimName,
                age=vic.AgeYear,
                gender_id=vic.GenderID,
                victim_police=vic.VictimPolice,
                performed_by_user_id=user_id
            )

        # Add accused and build mapping
        accused_map = {}
        for idx, acc in enumerate(case_dto.accused):
            created = self.repo.add_accused_to_case(
                case_id=case_record.id,
                name=acc.AccusedName,
                age=acc.AgeYear,
                gender_id=acc.GenderID,
                person_id=acc.PersonID,
                performed_by_user_id=user_id
            )
            accused_map[idx] = created

        # Add act/sections
        for act_sec in case_dto.act_sections:
            self.repo.associate_act_section_with_case(
                case_id=case_record.id,
                act_code=act_sec.ActCode,
                section_code=act_sec.SectionCode,
                act_order_id=act_sec.ActOrderID,
                section_order_id=act_sec.SectionOrderID,
                performed_by_user_id=user_id
            )

        # Add arrest/surrenders
        for arrest in case_dto.arrest_surrenders:
            # Map primary accused index or ID
            primary_id = accused_map[arrest.AccusedMasterID].id if arrest.AccusedMasterID in accused_map else arrest.AccusedMasterID
            
            # Map other accused indices or IDs
            other_ids = [
                accused_map[oid].id if oid in accused_map else oid 
                for oid in arrest.associated_accused_ids
            ]
            
            self.repo.record_arrest_surrender(
                case_id=case_record.id,
                type_id=arrest.ArrestSurrenderTypeID,
                date_val=arrest.ArrestSurrenderDate,
                state_id=arrest.ArrestSurrenderStateId,
                district_id=arrest.ArrestSurrenderDistrictId,
                station_id=arrest.PoliceStationID,
                io_id=arrest.IOID,
                court_id=arrest.CourtID,
                accused_master_id=primary_id,
                is_accused=arrest.IsAccused,
                is_complainant_accused=arrest.IsComplainantAccused,
                other_accused_ids=other_ids,
                performed_by_user_id=user_id
            )

        # Add chargesheets
        for cs in case_dto.chargesheets:
            self.repo.record_chargesheet(
                case_id=case_record.id,
                date_val=cs.csdate,
                cs_type=cs.cstype,
                police_person_id=cs.PolicePersonID,
                performed_by_user_id=user_id
            )

        # Reload with joins and validate response
        refreshed = self.repo.get_case_by_id(case_record.id)
        return CaseMasterResponse.model_validate(refreshed)

    def get_case(self, case_id: int) -> Optional[CaseMasterResponse]:
        """
        Fetches an FIR case by ID, eager loading children.
        """
        case = self.repo.get_case_by_id(case_id)
        if not case:
            return None
        return CaseMasterResponse.model_validate(case)

    def list_cases(
        self,
        page: int = 1,
        page_size: int = 10,
        district_id: Optional[int] = None,
        case_status_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        active_dataset_id: Optional[int] = None
    ) -> Tuple[List[CaseMasterResponse], int]:
        """
        Query and paginate case listings.
        """
        records, count = self.repo.list_cases(
            page=page,
            page_size=page_size,
            district_id=district_id,
            case_status_id=case_status_id,
            start_date=start_date,
            end_date=end_date,
            active_dataset_id=active_dataset_id
        )
        return [CaseMasterResponse.model_validate(r) for r in records], count

    # ── Lookup Expositions ───────────────────────────────────────────────────────

    def get_states(self) -> List[StateDTO]:
        return [StateDTO.model_validate(x) for x in self.repo.list_states()]

    def get_districts(self, state_id: Optional[int] = None) -> List[DistrictDTO]:
        return [DistrictDTO.model_validate(x) for x in self.repo.list_districts(state_id)]

    def get_courts(self, district_id: Optional[int] = None) -> List[CourtDTO]:
        return [CourtDTO.model_validate(x) for x in self.repo.list_courts(district_id)]

    def get_units(self, district_id: Optional[int] = None) -> List[UnitDTO]:
        return [UnitDTO.model_validate(x) for x in self.repo.list_units(district_id)]

    def get_ranks(self) -> List[RankDTO]:
        return [RankDTO.model_validate(x) for x in self.repo.list_ranks()]

    def get_designations(self) -> List[DesignationDTO]:
        return [DesignationDTO.model_validate(x) for x in self.repo.list_designations()]

    def get_employees(self, unit_id: Optional[int] = None) -> List[EmployeeDTO]:
        return [EmployeeDTO.model_validate(x) for x in self.repo.list_employees(unit_id)]

    def get_case_categories(self) -> List[CaseCategoryDTO]:
        return [CaseCategoryDTO.model_validate(x) for x in self.repo.list_case_categories()]

    def get_gravity_offences(self) -> List[GravityOffenceDTO]:
        return [GravityOffenceDTO.model_validate(x) for x in self.repo.list_gravity_offences()]

    def get_case_statuses(self) -> List[CaseStatusDTO]:
        return [CaseStatusDTO.model_validate(x) for x in self.repo.list_case_statuses()]

    def get_castes(self) -> List[CasteDTO]:
        return [CasteDTO.model_validate(x) for x in self.repo.list_castes()]

    def get_religions(self) -> List[ReligionDTO]:
        return [ReligionDTO.model_validate(x) for x in self.repo.list_religions()]

    def get_occupations(self) -> List[OccupationDTO]:
        return [OccupationDTO.model_validate(x) for x in self.repo.list_occupations()]

    def get_genders(self) -> List[GenderDTO]:
        return [GenderDTO.model_validate(x) for x in self.repo.list_genders()]

    def get_nationalities(self) -> List[NationalityDTO]:
        return [NationalityDTO.model_validate(x) for x in self.repo.list_nationalities()]

    def get_blood_groups(self) -> List[BloodGroupDTO]:
        return [BloodGroupDTO.model_validate(x) for x in self.repo.list_blood_groups()]

    def get_acts(self) -> List[ActDTO]:
        return [ActDTO.model_validate(x) for x in self.repo.list_acts()]

    def get_sections(self, act_code: Optional[str] = None) -> List[SectionDTO]:
        return [SectionDTO.model_validate(x) for x in self.repo.list_sections(act_code)]

    def get_crime_heads(self) -> List[CrimeHeadDTO]:
        return [CrimeHeadDTO.model_validate(x) for x in self.repo.list_crime_heads()]

    def get_crime_sub_heads(self, crime_head_id: Optional[int] = None) -> List[CrimeSubHeadDTO]:
        return [CrimeSubHeadDTO.model_validate(x) for x in self.repo.list_crime_sub_heads(crime_head_id)]

    def update_case(
        self, 
        case_id: int,
        case_dto: CaseMasterCreate, 
        user_id: Optional[int] = None
    ) -> CaseMasterResponse:
        """
        Updates an existing FIR case, enforcing validations, and returning the Response DTO.
        """
        # Validate coordinates
        if case_dto.occurrence_time:
            if not validate_latitude(case_dto.occurrence_time.latitude):
                raise ValueError(f"Invalid latitude: {case_dto.occurrence_time.latitude}. Must be between -90 and 90.")
            if not validate_longitude(case_dto.occurrence_time.longitude):
                raise ValueError(f"Invalid longitude: {case_dto.occurrence_time.longitude}. Must be between -180 and 180.")

        # Validate ages
        for comp in case_dto.complainants:
            if not validate_age(comp.AgeYear):
                raise ValueError(f"Invalid complainant age: {comp.AgeYear}. Must be between 0 and 125.")
        for vic in case_dto.victims:
            if not validate_age(vic.AgeYear):
                raise ValueError(f"Invalid victim age: {vic.AgeYear}. Must be between 0 and 125.")
        for acc in case_dto.accused:
            if not validate_age(acc.AgeYear):
                raise ValueError(f"Invalid accused age: {acc.AgeYear}. Must be between 0 and 125.")

        # Resolve or validate CrimeNo and CaseNo
        crime_no = case_dto.CrimeNo
        case_no = case_dto.CaseNo

        if crime_no:
            if not validate_crime_no(crime_no):
                raise ValueError(f"Invalid CrimeNo format: {crime_no}. Must be 18 digits containing a valid year.")
            if not case_no:
                case_no = generate_case_no(crime_no)
            elif not validate_case_no(case_no):
                raise ValueError(f"Invalid CaseNo format: {case_no}. Must be 9 digits containing a valid year.")
        else:
            raise ValueError("CrimeNo is required to update a case.")

        # Update case master and occurrence time in repo
        repo = FIRRepository(self.db)
        case = repo.update_case(
            case_id=case_id,
            crime_no=crime_no,
            case_no=case_no,
            registered_date=case_dto.CrimeRegisteredDate,
            police_person_id=case_dto.PolicePersonID,
            police_station_id=case_dto.PoliceStationID,
            case_category_id=case_dto.CaseCategoryID,
            gravity_offence_id=case_dto.GravityOffenceID,
            crime_major_head_id=case_dto.CrimeMajorHeadID,
            crime_minor_head_id=case_dto.CrimeMinorHeadID,
            case_status_id=case_dto.CaseStatusID,
            court_id=case_dto.CourtID,
            brief_facts=case_dto.BriefFacts,
            incident_from_date=case_dto.occurrence_time.IncidentFromDate if case_dto.occurrence_time else None,
            incident_to_date=case_dto.occurrence_time.IncidentToDate if case_dto.occurrence_time else None,
            info_received_ps_date=case_dto.occurrence_time.InfoReceivedPSDate if case_dto.occurrence_time else None,
            latitude=case_dto.occurrence_time.latitude if case_dto.occurrence_time else None,
            longitude=case_dto.occurrence_time.longitude if case_dto.occurrence_time else None,
            occurrence_brief_facts=case_dto.occurrence_time.BriefFacts if case_dto.occurrence_time else None,
            performed_by_user_id=user_id,
            commit=False
        )

        if not case:
            raise ValueError(f"Case with ID {case_id} not found.")

        # Sync/update complainants
        self.db.query(ComplainantDetails).filter(ComplainantDetails.CaseMasterID == case_id).delete()
        for comp in case_dto.complainants:
            repo.add_complainant_to_case(
                case_id=case_id,
                name=comp.ComplainantName,
                gender_id=comp.GenderID,
                age=comp.AgeYear,
                occupation_id=comp.OccupationID,
                religion_id=comp.ReligionID,
                caste_id=comp.CasteID,
                commit=False
            )

        # Sync/update victims
        self.db.query(FIRVictim).filter(FIRVictim.CaseMasterID == case_id).delete()
        for vic in case_dto.victims:
            repo.add_victim_to_case(
                case_id=case_id,
                name=vic.VictimName,
                gender_id=vic.GenderID,
                age=vic.AgeYear,
                is_police=vic.IsPolice,
                commit=False
            )

        # Sync/update accused
        self.db.query(Accused).filter(Accused.CaseMasterID == case_id).delete()
        for acc in case_dto.accused:
            repo.add_accused_to_case(
                case_id=case_id,
                name=acc.AccusedName,
                gender_id=acc.GenderID,
                age=acc.AgeYear,
                commit=False
            )

        self.db.commit()
        self.db.refresh(case)

        # Fetch eagerly loaded updated case
        updated_case = repo.get_case_by_id(case_id)
        return CaseMasterResponse.model_validate(updated_case)

    def delete_case(self, case_id: int, user_id: Optional[int] = None) -> bool:
        """
        Deletes a case and returns True if successful, False otherwise.
        """
        repo = FIRRepository(self.db)
        return repo.delete_case(case_id=case_id, performed_by_user_id=user_id)
