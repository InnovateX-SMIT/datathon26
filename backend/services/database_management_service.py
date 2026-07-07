import io
import json
import logging
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any, Tuple

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_, or_, desc, asc

from backend.core.logging import logger
from backend.repositories.admin_repository import AdminRepository
from backend.models.user import User
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.victim import Victim
from backend.models.location import Location
from backend.models.police_station import PoliceStation
from backend.models.fir_case import CaseMaster
from backend.models.fir_people import ComplainantDetails, FIRVictim, Accused
from backend.models.fir_proceedings import ArrestSurrender, ChargesheetDetails

from backend.schemas.crime import CrimeEventCreate
from backend.schemas.criminal import CriminalCreate
from backend.schemas.victim import VictimCreate
from backend.schemas.location import LocationCreate
from backend.schemas.police_station import PoliceStationCreate
from backend.schemas.fir import (
    CaseMasterCreate, ComplainantDetailsCreate, FIRVictimCreate, AccusedCreate,
    ArrestSurrenderCreate, ChargesheetDetailsCreate
)

TABLE_MODELS: Dict[str, Any] = {
    "crime_events": CrimeEvent,
    "criminals": Criminal,
    "victims": Victim,
    "locations": Location,
    "police_stations": PoliceStation,
    "cases": CaseMaster,
    "complainants": ComplainantDetails,
    "fir_victims": FIRVictim,
    "accused": Accused,
    "arrests": ArrestSurrender,
    "chargesheets": ChargesheetDetails,
}

TABLE_SCHEMAS: Dict[str, Any] = {
    "crime_events": CrimeEventCreate,
    "criminals": CriminalCreate,
    "victims": VictimCreate,
    "locations": LocationCreate,
    "police_stations": PoliceStationCreate,
    "cases": CaseMasterCreate,
    "complainants": ComplainantDetailsCreate,
    "fir_victims": FIRVictimCreate,
    "accused": AccusedCreate,
    "arrests": ArrestSurrenderCreate,
    "chargesheets": ChargesheetDetailsCreate,
}

# Fields to match during a generic keyword search
SEARCH_FIELDS: Dict[str, List[str]] = {
    "crime_events": ["crime_type", "crime_category", "crime_subcategory", "description", "status"],
    "criminals": ["name", "gender", "occupation", "caste", "status"],
    "victims": ["gender", "occupation"],
    "locations": ["state", "district"],
    "police_stations": ["station_name", "district", "beat", "availability"],
    "cases": ["CrimeNo", "CaseNo", "BriefFacts"],
    "complainants": ["ComplainantName"],
    "fir_victims": ["VictimName"],
    "accused": ["AccusedName", "PersonID"],
    "arrests": [],
    "chargesheets": ["cstype"],
}


class DatabaseManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)

    def _get_model_and_schema(self, table: str) -> Tuple[Any, Any]:
        if table not in TABLE_MODELS:
            raise ValueError(f"Unsupported table: {table}")
        return TABLE_MODELS[table], TABLE_SCHEMAS[table]

    # ── 1. Dashboard / Stats ──────────────────────────────────────────────────

    def get_dashboard_stats(self, performed_by_user_id: int) -> Dict[str, Any]:
        """
        Gathers database health, record counts, and last updated timestamps.
        """
        # Test DB connection
        db_status = "healthy"
        try:
            self.db.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "unhealthy"

        counts = {}
        last_updated = {}

        for name, model in TABLE_MODELS.items():
            # Get count
            try:
                count = self.db.query(func.count(model.id)).scalar() or 0
                counts[name] = count
            except Exception:
                counts[name] = 0

            # Get max updated_at
            try:
                max_update = self.db.query(func.max(model.updated_at)).scalar()
                if max_update:
                    if isinstance(max_update, datetime):
                        last_updated[name] = max_update.isoformat()
                    else:
                        last_updated[name] = str(max_update)
                else:
                    last_updated[name] = None
            except Exception:
                last_updated[name] = None

        # Add audit log
        self.admin_repo.create_audit_log(
            user_id=performed_by_user_id,
            action="DATABASE_DASHBOARD_VIEWED",
            entity_type="system",
            details=json.dumps({"db_status": db_status})
        )

        return {
            "health": db_status,
            "counts": counts,
            "last_updated": last_updated,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ── 2. Search / Paginated list ────────────────────────────────────────────

    def list_records(
        self,
        table: str,
        page: int = 1,
        page_size: int = 10,
        search_query: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        model_class, _ = self._get_model_and_schema(table)
        query = self.db.query(model_class)

        # Apply Column Filters
        if filters:
            for field, val in filters.items():
                if val is not None and hasattr(model_class, field):
                    # For strings, support partial case-insensitive match; for numbers/dates, support exact match
                    col = getattr(model_class, field)
                    if isinstance(val, str) and val.strip() != "":
                        query = query.filter(col.ilike(f"%{val}%"))
                    elif val != "":
                        query = query.filter(col == val)

        # Apply Generic Search Query
        if search_query and search_query.strip() != "":
            search_cols = SEARCH_FIELDS.get(table, [])
            or_filters = []
            for col_name in search_cols:
                col = getattr(model_class, col_name)
                or_filters.append(col.ilike(f"%{search_query}%"))
            
            # Special case: allow searching by ID if the query is a number
            if search_query.isdigit() and hasattr(model_class, "id"):
                or_filters.append(getattr(model_class, "id") == int(search_query))

            if or_filters:
                query = query.filter(or_(*or_filters))

        # Total record count for this query
        total = query.count()

        # Apply Sorting
        if sort_by and hasattr(model_class, sort_by):
            col = getattr(model_class, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))
        else:
            # Default sorting by primary key desc
            if hasattr(model_class, "id"):
                query = query.order_by(desc(model_class.id))

        # Apply Pagination
        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()

        return {
            "records": records,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    # ── 3. Read Specific Record ──────────────────────────────────────────────

    def get_record_by_id(self, table: str, record_id: int) -> Any:
        model_class, _ = self._get_model_and_schema(table)
        record = self.db.query(model_class).filter(model_class.id == record_id).first()
        return record

    # ── 4. Create Record ──────────────────────────────────────────────────────

    def create_record(self, table: str, payload_data: Dict[str, Any], performed_by_user_id: int) -> Any:
        model_class, schema_class = self._get_model_and_schema(table)

        # Custom date/time parsing if string is passed
        cleaned_payload = self._parse_payload_types(payload_data, schema_class)

        # Validation via Pydantic
        validated = schema_class(**cleaned_payload)
        
        # Intercept case creation and delegate to FIRService
        if table == "cases":
            from backend.services.fir_service import FIRService
            from backend.core.dataset_resolver import DatasetResolver
            
            resolver = DatasetResolver(self.db)
            active_dataset_id = resolver.get_active_dataset_id_optional()
            
            fir_service = FIRService(self.db)
            created_case_dto = fir_service.create_case(
                validated,
                dataset_id=active_dataset_id,
                user_id=performed_by_user_id
            )
            # Query the database to retrieve the ORM instance
            db_record = self.db.query(model_class).filter(model_class.id == created_case_dto.id).first()
        else:
            # Instantiate and save
            db_record = model_class(**validated.model_dump())
            self.db.add(db_record)
            self.db.commit()
            self.db.refresh(db_record)

        # Audit Log
        self.admin_repo.create_audit_log(
            user_id=performed_by_user_id,
            action="DATABASE_RECORD_CREATED",
            entity_type=table,
            entity_id=db_record.id,
            details=json.dumps({"fields": cleaned_payload}, default=str)
        )

        return db_record

    # ── 5. Update Record ──────────────────────────────────────────────────────

    def update_record(self, table: str, record_id: int, payload_data: Dict[str, Any], performed_by_user_id: int) -> Any:
        model_class, schema_class = self._get_model_and_schema(table)
        db_record = self.db.query(model_class).filter(model_class.id == record_id).first()
        if not db_record:
            raise ValueError(f"Record with ID {record_id} not found in {table}")

        # Custom date/time parsing
        cleaned_payload = self._parse_payload_types(payload_data, schema_class)

        # Validation via Pydantic
        # Since update can be partial, we want to allow validating a full object constructed from merge
        current_data = {c.name: getattr(db_record, c.name) for c in db_record.__table__.columns}
        # Ignore database managed audit columns and primary key during verification
        for col in ["id", "created_at", "updated_at"]:
            current_data.pop(col, None)
        
        merged_data = {**current_data, **cleaned_payload}
        validated = schema_class(**merged_data)

        # Apply updates to DB instance
        for key, val in validated.model_dump().items():
            setattr(db_record, key, val)

        self.db.commit()
        self.db.refresh(db_record)

        # Audit Log
        self.admin_repo.create_audit_log(
            user_id=performed_by_user_id,
            action="DATABASE_RECORD_UPDATED",
            entity_type=table,
            entity_id=record_id,
            details=json.dumps({"updates": cleaned_payload}, default=str)
        )

        return db_record

    # ── 6. Delete Record ──────────────────────────────────────────────────────

    def delete_record(self, table: str, record_id: int, performed_by_user_id: int) -> bool:
        model_class, _ = self._get_model_and_schema(table)
        db_record = self.db.query(model_class).filter(model_class.id == record_id).first()
        if not db_record:
            raise ValueError(f"Record with ID {record_id} not found in {table}")

        self.db.delete(db_record)
        self.db.commit()

        # Audit Log
        self.admin_repo.create_audit_log(
            user_id=performed_by_user_id,
            action="DATABASE_RECORD_DELETED",
            entity_type=table,
            entity_id=record_id,
            details=f"Record deleted from {table}"
        )

        return True

    # ── 7. Bulk Upload ────────────────────────────────────────────────────────

    def bulk_upload(
        self,
        table: str,
        file_bytes: bytes,
        filename: str,
        performed_by_user_id: int,
        preview: bool = False
    ) -> Dict[str, Any]:
        """
        Parses CSV/XLSX, validates with Pydantic, skips invalid rows,
        and saves valid rows. Returns full row-level details and summary.
        """
        model_class, schema_class = self._get_model_and_schema(table)

        # Parse file into DataFrame
        if filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        elif filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel (.xlsx) are supported.")

        # Clean NaN/Null values
        df = df.replace({np.nan: None})

        total_rows = len(df)
        valid_records: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        preview_rows: List[Dict[str, Any]] = []

        # Iterate rows
        for idx, row in df.iterrows():
            row_num = idx + 2 # row number in sheet (header is row 1)
            row_dict = row.to_dict()

            # Clean keys (trim whitespaces in headers)
            row_dict = {str(k).strip(): v for k, v in row_dict.items()}

            # Parse types for date/time/numeric columns
            try:
                row_dict = self._parse_payload_types(row_dict, schema_class)
            except Exception as pe:
                errors.append({
                    "row": row_num,
                    "errors": {"formatting": str(pe)},
                    "raw_data": row_dict
                })
                continue

            # Validate against Pydantic schema
            try:
                validated = schema_class(**row_dict)
                valid_records.append(validated.model_dump())
                
                # Keep preview of first 10 valid records
                if len(preview_rows) < 10:
                    preview_rows.append(row_dict)
            except Exception as e:
                # Capture specific validation errors
                err_dict = {}
                # Handle pydantic ValidationError mapping
                if hasattr(e, "errors") and callable(e.errors):
                    for error_item in e.errors():
                        field_name = " -> ".join(map(str, error_item["loc"]))
                        err_dict[field_name] = error_item["msg"]
                else:
                    err_dict["validation"] = str(e)

                errors.append({
                    "row": row_num,
                    "errors": err_dict,
                    "raw_data": row_dict
                })

        summary = {
            "total_rows": total_rows,
            "valid_count": len(valid_records),
            "invalid_count": len(errors),
            "errors": errors,
            "preview": preview_rows
        }

        # If preview only, return details without committing
        if preview:
            return summary

        # Perform Transactional Import of valid rows only
        if valid_records:
            try:
                # Start transaction explicit context
                for rec in valid_records:
                    db_rec = model_class(**rec)
                    self.db.add(db_rec)
                self.db.commit()

                # Audit Log
                self.admin_repo.create_audit_log(
                    user_id=performed_by_user_id,
                    action="DATABASE_RECORD_BULK_IMPORTED",
                    entity_type=table,
                    details=json.dumps({
                        "filename": filename,
                        "total_rows": total_rows,
                        "imported_count": len(valid_records),
                        "skipped_count": len(errors)
                    })
                )
            except Exception as ex:
                self.db.rollback()
                logger.error(f"Bulk insert failed, rolled back: {ex}", exc_info=True)
                raise ValueError(f"Failed to save records to database: {str(ex)}")

        return summary

    # ── 8. Export Data ────────────────────────────────────────────────────────

    def export_data(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        export_format: str = "csv"
    ) -> Tuple[bytes, str]:
        """
        Fetches all records matching filters and returns them as CSV or Excel bytes.
        """
        model_class, _ = self._get_model_and_schema(table)
        query = self.db.query(model_class)

        # Apply Column Filters
        if filters:
            for field, val in filters.items():
                if val is not None and hasattr(model_class, field):
                    col = getattr(model_class, field)
                    if isinstance(val, str) and val.strip() != "":
                        query = query.filter(col.ilike(f"%{val}%"))
                    elif val != "":
                        query = query.filter(col == val)

        records = query.order_by(model_class.id.desc()).all()

        # Convert records to list of dicts
        data_list = []
        for r in records:
            r_dict = {c.name: getattr(r, c.name) for c in r.__table__.columns}
            data_list.append(r_dict)

        df = pd.DataFrame(data_list)

        # Format date/time columns for clean presentation
        for col in df.columns:
            if df[col].dtype == object:
                # convert datetime objects
                df[col] = df[col].apply(lambda x: x.isoformat() if isinstance(x, (datetime, date, time)) else x)

        filename_prefix = f"export_{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if export_format.lower() == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name=table)
            excel_bytes = output.getvalue()
            return excel_bytes, f"{filename_prefix}.xlsx"
        else:
            # default CSV
            csv_str = df.to_csv(index=False)
            return csv_str.encode("utf-8"), f"{filename_prefix}.csv"

    # ── Helper: Parse input payloads ──────────────────────────────────────────

    def _parse_payload_types(self, payload: Dict[str, Any], schema_class: Any) -> Dict[str, Any]:
        """
        Safely convert date/time strings, coordinate strings, or empty fields
        into appropriate datatypes matching schema expectations.
        """
        cleaned = {}
        for key, value in payload.items():
            # Strip string values
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    value = None

            if value is None:
                cleaned[key] = None
                continue

            # Fetch the field type from schema
            field_info = schema_class.model_fields.get(key)
            if not field_info:
                # Field doesn't belong to schema, let's keep it or skip it (skip is safer)
                continue

            field_type = field_info.annotation

            try:
                # String conversion logic for specific classes
                str_type = str(field_type)
                
                # Check date
                if "date" in str_type and not isinstance(value, date):
                    if isinstance(value, str):
                        # Handle YYYY-MM-DD
                        cleaned[key] = datetime.strptime(value.split("T")[0], "%Y-%m-%d").date()
                    else:
                        cleaned[key] = value
                
                # Check time
                elif "time" in str_type and not isinstance(value, time):
                    if isinstance(value, str):
                        # Try HH:MM:SS or HH:MM
                        parts = value.split(":")
                        if len(parts) >= 3:
                            cleaned[key] = time(int(parts[0]), int(parts[1]), int(parts[2].split(".")[0]))
                        elif len(parts) == 2:
                            cleaned[key] = time(int(parts[0]), int(parts[1]))
                        else:
                            cleaned[key] = value
                    else:
                        cleaned[key] = value

                # Check float/int
                elif "float" in str_type:
                    cleaned[key] = float(value)
                elif "int" in str_type:
                    cleaned[key] = int(value)
                else:
                    cleaned[key] = value
            except Exception as e:
                raise ValueError(f"Field '{key}' has invalid format. Details: {e}")

        return cleaned
