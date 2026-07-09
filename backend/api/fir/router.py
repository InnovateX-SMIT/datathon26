from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import json

from backend.core.database import get_db
from backend.core.logging import logger
from backend.api.auth.router import get_current_user
from backend.schemas.fir import (
    CaseMasterCreate, CaseMasterResponse,
    StateDTO, DistrictDTO, CourtDTO, UnitDTO, RankDTO, DesignationDTO, EmployeeDTO,
    CaseCategoryDTO, GravityOffenceDTO, CaseStatusDTO, CasteDTO, ReligionDTO, OccupationDTO,
    GenderDTO, NationalityDTO, BloodGroupDTO, ActDTO, SectionDTO, CrimeHeadDTO, CrimeSubHeadDTO
)
from backend.services.fir_service import FIRService
from backend.services.dataset_service import DatasetService

router = APIRouter()

# ── Case CRUD Endpoints ───────────────────────────────────────────────────────

@router.post("/", response_model=CaseMasterResponse, status_code=status.HTTP_201_CREATED)
def create_case_endpoint(
    case_dto: CaseMasterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = FIRService(db)
        user_id = getattr(current_user, "id", 0)
        
        from backend.core.dataset_resolver import DatasetResolver
        resolver = DatasetResolver(db)
        dataset_id = resolver.get_active_dataset_id_optional()
        
        return service.create_case(case_dto, dataset_id=dataset_id, user_id=user_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating FIR case: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create case.")

@router.get("/{case_id}", response_model=CaseMasterResponse)
def get_case_endpoint(
    case_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = FIRService(db)
    case = service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")
    return case

@router.put("/{case_id}", response_model=CaseMasterResponse)
def update_case_endpoint(
    case_id: int,
    case_dto: CaseMasterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = FIRService(db)
        user_id = getattr(current_user, "id", 0)
        return service.update_case(case_id, case_dto, user_id=user_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating FIR case: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update case.")

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case_endpoint(
    case_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = FIRService(db)
    user_id = getattr(current_user, "id", 0)
    success = service.delete_case(case_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")
    return

@router.get("/", response_model=dict)
def list_cases_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    district_id: Optional[int] = Query(None),
    case_status_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        service = FIRService(db)
        from backend.core.dataset_resolver import DatasetResolver
        resolver = DatasetResolver(db)
        active_dataset_id = resolver.get_active_dataset_id_optional()
        
        cases, count = service.list_cases(
            page=page,
            page_size=page_size,
            district_id=district_id,
            case_status_id=case_status_id,
            start_date=start_date,
            end_date=end_date,
            active_dataset_id=active_dataset_id
        )
        return {
            "records": [CaseMasterResponse.model_validate(c) for c in cases],
            "total": count,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"Error listing FIR cases: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list cases.")

# ── File Import Endpoint ─────────────────────────────────────────────────────

@router.post("/import", response_model=dict)
async def import_fir_dataset_endpoint(
    display_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    preview: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        file_bytes = await file.read()
        filename = file.filename
        
        if not (filename.lower().endswith(".csv") or filename.lower().endswith(".xlsx") or filename.lower().endswith(".xls")):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format.")
            
        service = DatasetService(db)
        user_id = getattr(current_user, "id", 0)
        
        res = service.import_dataset(
            display_name=display_name or filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title(),
            description=description,
            file_name=filename,
            file_bytes=file_bytes,
            user_id=user_id,
            preview=preview
        )
        
        if preview:
            return res
        else:
            summary = {}
            if res.import_summary:
                try:
                    summary = json.loads(res.import_summary)
                except Exception:
                    pass
            return {
                **summary,
                "dataset_id": res.id,
                "display_name": res.display_name,
                "status": res.status,
                "is_active": res.is_active,
                "schema_type": res.schema_type or "fir_normalized"
            }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error importing FIR dataset: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Import failed: {str(e)}")

# ── Lookup Endpoints ─────────────────────────────────────────────────────────

@router.get("/lookups/states", response_model=List[StateDTO])
def get_states_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_states()

@router.get("/lookups/districts", response_model=List[DistrictDTO])
def get_districts_endpoint(state_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_districts(state_id)

@router.get("/lookups/courts", response_model=List[CourtDTO])
def get_courts_endpoint(district_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_courts(district_id)

@router.get("/lookups/units", response_model=List[UnitDTO])
def get_units_endpoint(district_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_units(district_id)

@router.get("/lookups/ranks", response_model=List[RankDTO])
def get_ranks_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_ranks()

@router.get("/lookups/designations", response_model=List[DesignationDTO])
def get_designations_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_designations()

@router.get("/lookups/employees", response_model=List[EmployeeDTO])
def get_employees_endpoint(unit_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_employees(unit_id)

@router.get("/lookups/case-categories", response_model=List[CaseCategoryDTO])
def get_case_categories_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_case_categories()

@router.get("/lookups/gravity-offences", response_model=List[GravityOffenceDTO])
def get_gravity_offences_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_gravity_offences()

@router.get("/lookups/case-statuses", response_model=List[CaseStatusDTO])
def get_case_statuses_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_case_statuses()

@router.get("/lookups/castes", response_model=List[CasteDTO])
def get_castes_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_castes()

@router.get("/lookups/religions", response_model=List[ReligionDTO])
def get_religions_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_religions()

@router.get("/lookups/occupations", response_model=List[OccupationDTO])
def get_occupations_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_occupations()

@router.get("/lookups/genders", response_model=List[GenderDTO])
def get_genders_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_genders()

@router.get("/lookups/nationalities", response_model=List[NationalityDTO])
def get_nationalities_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_nationalities()

@router.get("/lookups/blood-groups", response_model=List[BloodGroupDTO])
def get_blood_groups_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_blood_groups()

@router.get("/lookups/acts", response_model=List[ActDTO])
def get_acts_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_acts()

@router.get("/lookups/sections", response_model=List[SectionDTO])
def get_sections_endpoint(act_code: Optional[str] = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_sections(act_code)

@router.get("/lookups/crime-heads", response_model=List[CrimeHeadDTO])
def get_crime_heads_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_crime_heads()

@router.get("/lookups/crime-sub-heads", response_model=List[CrimeSubHeadDTO])
def get_crime_sub_heads_endpoint(crime_head_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return FIRService(db).get_crime_sub_heads(crime_head_id)
