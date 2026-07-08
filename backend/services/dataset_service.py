from sqlalchemy.orm import Session
from typing import List, Optional, Union
import os
import io
import re
import json
import pandas as pd
import numpy as np
from datetime import datetime
from backend.models.dataset import Dataset
from backend.core.exceptions import NoActiveDatasetException
from backend.core.logging import logger

class DatasetService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_dataset_id(self) -> Optional[int]:
        """
        Resolves the currently active dataset ID.
        """
        active_row = self.db.query(Dataset.id).filter(Dataset.is_active == True).first()
        return active_row[0] if active_row else None

    def get_active_dataset_id_or_raise(self) -> int:
        """
        Resolves the currently active dataset ID, or raises NoActiveDatasetException if none is active.
        """
        active_id = self.get_active_dataset_id()
        if active_id is None:
            raise NoActiveDatasetException()
        return active_id

    def get_active_dataset(self) -> Optional[Dataset]:
        """
        Gets the currently active Dataset object.
        """
        return self.db.query(Dataset).filter(Dataset.is_active == True).first()

    def list_datasets(self) -> List[Dataset]:
        """
        Lists all datasets in the registry sorted by creation time.
        """
        return self.db.query(Dataset).order_by(Dataset.created_at.desc()).all()

    def activate_dataset(self, dataset_id: int) -> Dataset:
        """
        Sets the specified dataset as active. Enforces the maximum active datasets limit,
        deactivating the oldest active dataset(s) if necessary.
        """
        from backend.models.dataset import DatasetConfig
        from datetime import datetime

        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        if dataset.status == "Archived":
            raise ValueError("Cannot activate an archived dataset.")

        if dataset.status != "Ready":
            raise ValueError("Cannot activate a dataset that is not in Ready state.")

        if dataset.is_active:
            return dataset

        # Load config
        config = self.db.query(DatasetConfig).first()
        max_active = config.max_active_datasets if config else "1"

        if max_active != "All":
            limit = int(max_active)
            # Find currently active datasets ordered by upload_time ascending (oldest first)
            active_datasets = self.db.query(Dataset).filter(Dataset.is_active == True).order_by(Dataset.upload_time.asc()).all()
            if len(active_datasets) >= limit:
                # Deactivate oldest active datasets to make space
                num_to_deactivate = len(active_datasets) - limit + 1
                for i in range(num_to_deactivate):
                    old_ds = active_datasets[i]
                    old_ds.is_active = False
                    logger.info(f"[Dataset Activation Change] Dataset ID: {old_ds.id}, Timestamp: {datetime.utcnow().isoformat()}, Previous Status: Active, New Status: Inactive")

        # Activate this dataset
        dataset.is_active = True
        logger.info(f"[Dataset Activation Change] Dataset ID: {dataset.id}, Timestamp: {datetime.utcnow().isoformat()}, Previous Status: Inactive, New Status: Active")

        self.db.commit()
        return dataset

    def deactivate_dataset(self, dataset_id: int) -> Dataset:
        """
        Sets the specified dataset as inactive.
        """
        from datetime import datetime
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        if not dataset.is_active:
            return dataset

        # Deactivate
        dataset.is_active = False
        logger.info(f"[Dataset Activation Change] Dataset ID: {dataset.id}, Timestamp: {datetime.utcnow().isoformat()}, Previous Status: Active, New Status: Inactive")
        self.db.commit()
        return dataset

    def get_active_datasets(self) -> List[Dataset]:
        """
        Gets all currently active Dataset objects.
        """
        return self.db.query(Dataset).filter(Dataset.is_active == True).all()

    def get_active_dataset_ids(self) -> List[int]:
        """
        Gets the IDs of all currently active datasets.
        """
        active_ids = self.db.query(Dataset.id).filter(Dataset.is_active == True).all()
        return [row[0] for row in active_ids]

    def get_active_datasets_metadata(self) -> List[dict]:
        """
        Returns basic metadata dicts for all active datasets.
        """
        active_ds = self.get_active_datasets()
        return [
            {
                "id": ds.id,
                "name": ds.name,
                "display_name": ds.display_name,
                "original_filename": ds.original_filename,
                "row_count": ds.row_count,
                "column_count": ds.column_count,
                "file_size": ds.file_size
            }
            for ds in active_ds
        ]

    def get_dataset_config(self):
        """
        Retrieves the dataset settings configuration, creating the default one if missing.
        """
        from backend.models.dataset import DatasetConfig
        config = self.db.query(DatasetConfig).first()
        if not config:
            config = DatasetConfig(max_active_datasets="1")
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config

    def update_dataset_config(self, max_active: str):
        """
        Updates the dataset settings configuration and enforces active count limits.
        """
        from backend.models.dataset import DatasetConfig
        from datetime import datetime
        
        if max_active not in ["1", "2", "3", "All"]:
            raise ValueError("Invalid maximum active count. Options are '1', '2', '3', or 'All'.")

        config = self.get_dataset_config()
        config.max_active_datasets = max_active
        self.db.commit()

        # If the new limit is a number, we may need to deactivate some datasets
        if max_active != "All":
            limit = int(max_active)
            active_datasets = self.db.query(Dataset).filter(Dataset.is_active == True).order_by(Dataset.upload_time.asc()).all()
            if len(active_datasets) > limit:
                # Deactivate the oldest active datasets
                num_to_deactivate = len(active_datasets) - limit
                for i in range(num_to_deactivate):
                    old_ds = active_datasets[i]
                    old_ds.is_active = False
                    logger.info(f"[Dataset Activation Change] Dataset ID: {old_ds.id}, Timestamp: {datetime.utcnow().isoformat()}, Previous Status: Active, New Status: Inactive")
                self.db.commit()

        return config


    def delete_dataset(self, dataset_id: int) -> bool:
        """
        Soft-deletes (archives) the dataset from the registry. Sets status to 'Archived'
        and is_active to False.
        """
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        # If active, automatically fallback to another ready dataset
        if dataset.is_active:
            fallback_ds = self.db.query(Dataset).filter(
                Dataset.id != dataset_id,
                Dataset.status == "Ready"
            ).first()
            if fallback_ds:
                fallback_ds.is_active = True
                logger.info(f"Automatically fell back active context to dataset ID {fallback_ds.id} because dataset ID {dataset_id} is being archived.")
            dataset.is_active = False

        # Soft delete: set status to Archived
        dataset.status = "Archived"
        self.db.commit()

        logger.info(f"Dataset ID {dataset_id} soft-deleted/archived successfully.")
        return True

    def delete_dataset_permanent(self, dataset_id: int) -> bool:
        """
        Hard-deletes the dataset and all its associated child rows from the database.
        Also deletes the underlying uploaded file from disk.
        """
        import os
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        # If active, automatically fallback to another ready dataset
        if dataset.is_active:
            fallback_ds = self.db.query(Dataset).filter(
                Dataset.id != dataset_id,
                Dataset.status == "Ready"
            ).first()
            if fallback_ds:
                fallback_ds.is_active = True
                logger.info(f"Automatically fell back active context to dataset ID {fallback_ds.id} because dataset ID {dataset_id} is being permanently deleted.")
            dataset.is_active = False


        # Import models locally to avoid circular dependencies
        from backend.models.fir_case import CaseMaster, Inv_OccuranceTime
        from backend.models.fir_people import ComplainantDetails, FIRVictim, Accused
        from backend.models.fir_proceedings import ArrestSurrender, InvArrestSurrenderAccused, ChargesheetDetails
        from backend.models.fir_law import ActSectionAssociation
        from backend.models.crime import CrimeEvent
        from backend.models.criminal import Criminal
        from backend.models.victim import Victim
        from backend.models.crime_participation import CrimeParticipation

        case_ids = [c.id for c in dataset.cases]
        if case_ids:
            # 1. inv_arrestsurrenderaccused
            as_ids = [row[0] for row in self.db.query(ArrestSurrender.id).filter(ArrestSurrender.CaseMasterID.in_(case_ids)).all()]
            if as_ids:
                self.db.query(InvArrestSurrenderAccused).filter(InvArrestSurrenderAccused.ArrestSurrenderID.in_(as_ids)).delete(synchronize_session=False)
            
            # 2. arrest_surrender
            self.db.query(ArrestSurrender).filter(ArrestSurrender.CaseMasterID.in_(case_ids)).delete(synchronize_session=False)
            
            # 3. chargesheet_details
            self.db.query(ChargesheetDetails).filter(ChargesheetDetails.CaseMasterID.in_(case_ids)).delete(synchronize_session=False)
            
            # 4. complainant_details
            self.db.query(ComplainantDetails).filter(ComplainantDetails.CaseMasterID.in_(case_ids)).delete(synchronize_session=False)
            
            # 5. victim (FIRVictim)
            self.db.query(FIRVictim).filter(FIRVictim.CaseMasterID.in_(case_ids)).delete(synchronize_session=False)
            
            # 6. accused
            self.db.query(Accused).filter(Accused.CaseMasterID.in_(case_ids)).delete(synchronize_session=False)
            
            # 7. act_section_association
            self.db.query(ActSectionAssociation).filter(ActSectionAssociation.CaseMasterID.in_(case_ids)).delete(synchronize_session=False)
            
            # 8. inv_occurance_time
            self.db.query(Inv_OccuranceTime).filter(Inv_OccuranceTime.CaseMasterID.in_(case_ids)).delete(synchronize_session=False)

            # 9. Delete cases
            self.db.query(CaseMaster).filter(CaseMaster.id.in_(case_ids)).delete(synchronize_session=False)

        # Legacy data tables
        self.db.query(CrimeParticipation).filter(CrimeParticipation.dataset_id == dataset_id).delete(synchronize_session=False)
        self.db.query(CrimeEvent).filter(CrimeEvent.dataset_id == dataset_id).delete(synchronize_session=False)
        self.db.query(Criminal).filter(Criminal.dataset_id == dataset_id).delete(synchronize_session=False)
        self.db.query(Victim).filter(Victim.dataset_id == dataset_id).delete(synchronize_session=False)

        # Delete from disk if storage_path exists
        if dataset.storage_path and os.path.exists(dataset.storage_path):
            try:
                os.remove(dataset.storage_path)
            except Exception as io_err:
                logger.error(f"Error removing dataset file {dataset.storage_path}: {io_err}")

        # Delete dataset registry record
        self.db.delete(dataset)
        self.db.commit()
        return True

    def import_dataset(
        self,
        display_name: str,
        description: Optional[str],
        file_name: str,
        file_bytes: bytes,
        user_id: int,
        preview: bool = False
    ) -> Union[Dataset, dict]:
        """
        Registers an uploaded file in the registry under 'Uploading', dry-runs validations under 'Validating',
        and inserts CrimeEvent, Criminal, Victim, and CrimeParticipation records in transactional batches under 'Importing'.
        If any validation fails, rolls back completely and marks dataset as 'Failed'.
        """
        # Validate File Extension
        if not (file_name.lower().endswith(".csv") or file_name.lower().endswith(".xlsx") or file_name.lower().endswith(".xls")):
            raise ValueError("Unsupported file format. Only CSV and Excel (.xlsx, .xls) files are supported.")

        # Validate Empty File size
        if len(file_bytes) == 0:
            raise ValueError("File is empty. No data found.")

        # If preview mode, validate and return BulkUploadSummary without writing to DB or files
        if preview:
            if file_name.lower().endswith((".xlsx", ".xls")):
                try:
                    df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                except Exception as parse_err:
                    raise ValueError(f"Failed to parse Excel file: {str(parse_err)}")
            elif file_name.lower().endswith(".csv"):
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes))
                except Exception as parse_err:
                    raise ValueError(f"Failed to parse CSV file: {str(parse_err)}")
            else:
                raise ValueError("Unsupported format.")

            if df.empty or len(df) == 0:
                raise ValueError("File is empty.")

            df = df.replace({np.nan: None})

            from backend.services.fir_import_service import FIRImportService
            fir_importer = FIRImportService(self.db)
            detected_schema = fir_importer.detect_schema_type(df.columns)

            if detected_schema == "fir_normalized":
                ALIAS_MAP = {
                    "case_category": "case_category", "category": "case_category",
                    "gravity_offence": "gravity_offence", "gravity": "gravity_offence",
                    "case_status": "case_status", "status": "case_status",
                    "state": "state", "district": "district", "court": "court",
                    "unit_type": "unit_type", "unit": "unit", "police_station": "unit",
                    "officer_kgid": "officer_kgid", "kgid": "officer_kgid",
                    "officer_name": "officer_name", "officer_rank": "officer_rank",
                    "rank": "officer_rank", "officer_designation": "officer_designation",
                    "designation": "officer_designation", "officer_dob": "officer_dob",
                    "officer_gender": "officer_gender", "officer_blood_group": "officer_blood_group",
                    "officer_physically_challenged": "officer_physically_challenged",
                    "officer_appointment_date": "officer_appointment_date",
                    "crime_no": "crime_no", "crimeno": "crime_no", "case_no": "case_no", "caseno": "case_no",
                    "registered_date": "registered_date", "crime_registered_date": "registered_date",
                    "brief_facts": "brief_facts", "incident_from_date": "incident_from_date",
                    "incident_to_date": "incident_to_date", "info_received_date": "info_received_date",
                    "latitude": "latitude", "lat": "latitude", "longitude": "longitude", "lng": "longitude", "lon": "longitude",
                    "occurrence_brief_facts": "occurrence_brief_facts", "crime_group_name": "crime_group_name",
                    "crime_head_name": "crime_head_name", "act_code": "act_code", "act_description": "act_description",
                    "short_name": "short_name", "section_code": "section_code", "section_description": "section_description",
                    "act_order": "act_order", "section_order": "section_order", "complainant_name": "complainant_name",
                    "complainant_age": "complainant_age", "complainant_occupation": "complainant_occupation",
                    "complainant_religion": "complainant_religion", "complainant_caste": "complainant_caste",
                    "complainant_gender": "complainant_gender", "victim_name": "victim_name", "victim_age": "victim_age",
                    "victim_gender": "victim_gender", "victim_police": "victim_police", "accused_name": "accused_name",
                    "accused_age": "accused_age", "accused_gender": "accused_gender", "accused_person_id": "accused_person_id",
                    "arrest_type": "arrest_type", "arrest_date": "arrest_date", "arrest_state": "arrest_state",
                    "arrest_district": "arrest_district", "arrest_station": "arrest_station", "arrest_io_kgid": "arrest_io_kgid",
                    "arrest_court": "arrest_court", "arrest_primary_accused_name": "arrest_primary_accused_name",
                    "arrest_joint_accused_names": "arrest_joint_accused_names", "chargesheet_date": "chargesheet_date",
                    "chargesheet_type": "chargesheet_type", "chargesheet_officer_kgid": "chargesheet_officer_kgid"
                }

                def normalize_header(header: str) -> str:
                    h = str(header).strip().lower().lstrip('\ufeff')
                    h = h.replace(" ", "_").replace("-", "_").replace(".", "_")
                    h = re.sub(r'[^a-z0-9_]', '', h)
                    return re.sub(r'_+', '_', h).strip('_')

                df.columns = [normalize_header(c) for c in df.columns]
                rename_dict = {col: ALIAS_MAP[col] for col in df.columns if col in ALIAS_MAP}
                df = df.rename(columns=rename_dict)
                rows = df.to_dict(orient="records")

                val_errors = fir_importer.validate_rows(rows)
                formatted_errors = []
                for idx, e in enumerate(val_errors):
                    row_match = re.search(r"Row (\d+):", e)
                    row_num = int(row_match.group(1)) if row_match else (idx + 2)
                    formatted_errors.append({
                        "row": row_num,
                        "errors": {"validation": e},
                        "raw_data": rows[row_num - 2] if (0 <= row_num - 2 < len(rows)) else {}
                    })

                return {
                    "schema_type": "fir_normalized",
                    "total_rows": len(rows),
                    "valid_count": len(rows) - len(val_errors),
                    "invalid_count": len(val_errors),
                    "errors": formatted_errors,
                    "preview": rows[:10]
                }
            else:
                ALIAS_MAP = {
                    "fir_id": "fir_id", "firid": "fir_id", "fir_no": "fir_id", "fir_number": "fir_id", "firno": "fir_id",
                    "case_id": "fir_id", "case_number": "fir_id", "crime_type": "crime_type", "crimetype": "crime_type",
                    "type_of_crime": "crime_type", "offence_type": "crime_type", "offencetype": "crime_type",
                    "offense_type": "crime_type", "type": "crime_type", "crime": "crime_type", "crime_category": "crime_category",
                    "crimecategory": "crime_category", "category": "crime_category", "district": "district", "dist": "district",
                    "district_name": "district", "districtname": "district", "police_station": "police_station",
                    "policestation": "police_station", "ps": "police_station", "ps_name": "police_station", "station": "police_station",
                    "station_name": "police_station", "stationname": "police_station", "police_station_name": "police_station",
                    "policestationname": "police_station", "crime_date": "crime_date", "crimedate": "crime_date", "date": "crime_date",
                    "date_of_crime": "crime_date", "incident_date": "crime_date", "incidentdate": "crime_date", "offence_date": "crime_date",
                    "crime_time": "crime_time", "crimetime": "crime_time", "time": "crime_time", "time_of_crime": "crime_time",
                    "incident_time": "crime_time", "latitude": "latitude", "lat": "latitude", "longitude": "longitude",
                    "lng": "longitude", "lon": "longitude", "long": "longitude", "victim_age": "victim_age", "victimage": "victim_age",
                    "victim_s_age": "victim_age", "age_of_victim": "victim_age", "accused_age": "accused_age", "accusedage": "accused_age",
                    "accused_s_age": "accused_age", "age_of_accused": "accused_age", "criminal_age": "accused_age", "gender": "gender",
                    "sex": "gender", "victim_gender": "gender", "occupation": "occupation", "victim_occupation": "occupation",
                    "severity": "severity", "crime_severity": "severity", "crimeseverity": "severity", "seriousness": "severity",
                    "repeat_offender": "repeat_offender", "repeatoffender": "repeat_offender", "recidivist": "repeat_offender",
                    "repeat": "repeat_offender", "status": "status", "case_status": "status", "casestatus": "status",
                    "crime_status": "status"
                }

                def normalize_header(header: str) -> str:
                    h = str(header).strip().lower().lstrip('\ufeff')
                    h = h.replace(" ", "_").replace("-", "_").replace(".", "_")
                    h = re.sub(r'[^a-z0-9_]', '', h)
                    return re.sub(r'_+', '_', h)

                df.columns = [normalize_header(c) for c in df.columns]
                rename_dict = {col: ALIAS_MAP[col] for col in df.columns if col in ALIAS_MAP}
                df = df.rename(columns=rename_dict)
                rows = df.to_dict(orient="records")

                from backend.models.location import Location
                from backend.models.police_station import PoliceStation
                locations = self.db.query(Location).all()
                district_to_loc_id = {loc.district: loc.id for loc in locations}
                stations = self.db.query(PoliceStation).all()
                station_to_station_id = {s.station_name: s.id for s in stations}

                errors = []
                for idx, row in enumerate(rows):
                    row_num = idx + 2
                    err_dict = {}
                    
                    missing_fields = []
                    for field in ["district", "police_station", "crime_date", "crime_type"]:
                        val = row.get(field)
                        if val is None or (isinstance(val, str) and val.strip() == ""):
                            missing_fields.append(field)
                    if missing_fields:
                        err_dict["validation"] = f"Missing required fields: {', '.join(missing_fields)}"
                    else:
                        dist = str(row["district"]).strip()
                        ps = str(row["police_station"]).strip()
                        if dist not in district_to_loc_id:
                            err_dict["district"] = f"District '{dist}' not found in location master data."
                        if ps not in station_to_station_id:
                            err_dict["police_station"] = f"Police station '{ps}' not found in master data."
                        
                        date_str = str(row["crime_date"]).strip()
                        try:
                            if "/" in date_str:
                                datetime.strptime(date_str, "%d/%m/%Y").date()
                            elif "-" in date_str and len(date_str.split("-")[0]) == 2:
                                datetime.strptime(date_str, "%d-%m-%Y").date()
                            else:
                                datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                        except ValueError:
                            err_dict["crime_date"] = f"Invalid date format: {date_str}."

                    if err_dict:
                        errors.append({
                            "row": row_num,
                            "errors": err_dict,
                            "raw_data": row
                        })

                return {
                    "schema_type": "legacy_crime_intel",
                    "total_rows": len(rows),
                    "valid_count": len(rows) - len(errors),
                    "invalid_count": len(errors),
                    "errors": errors,
                    "preview": rows[:10]
                }


        # Validate Duplicate Filename (excluding failed and archived ones)
        duplicate_check = self.db.query(Dataset).filter(
            Dataset.original_filename == file_name,
            Dataset.status != "Failed",
            Dataset.status != "Archived"
        ).first()
        if duplicate_check:
            raise ValueError(f"A dataset with filename '{file_name}' has already been uploaded.")

        from backend.models.crime import CrimeEvent
        from backend.models.criminal import Criminal
        from backend.models.victim import Victim
        from backend.models.crime_participation import CrimeParticipation
        from backend.models.location import Location
        from backend.models.police_station import PoliceStation

        # 1. Create dataset record under 'Uploading' status
        db_dataset = Dataset(
            name=f"dataset_{int(datetime.utcnow().timestamp())}",
            original_filename=file_name,
            display_name=display_name,
            description=description,
            source_type="CSV" if file_name.lower().endswith(".csv") else "Excel",
            row_count=0,
            column_count=0,
            file_size=len(file_bytes),
            status="Uploading",
            upload_status="Uploading",
            storage_path=None,
            is_active=False
        )
        self.db.add(db_dataset)
        self.db.commit()
        self.db.refresh(db_dataset)

        try:
            # Create folder if not exists
            os.makedirs("datasets/uploaded", exist_ok=True)
            
            # Write file bytes
            storage_filename = f"{db_dataset.id}_{file_name}"
            storage_path = os.path.join("datasets", "uploaded", storage_filename)
            with open(storage_path, "wb") as f:
                f.write(file_bytes)
            
            db_dataset.storage_path = storage_path
            db_dataset.upload_status = "Completed"
            self.db.commit()

            # Transition to 'Validating'
            db_dataset.status = "Validating"
            self.db.commit()

            # Parse CSV or Excel
            if file_name.lower().endswith(".xlsx") or file_name.lower().endswith(".xls"):
                try:
                    df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                except Exception as parse_err:
                    raise ValueError(f"Failed to parse Excel file. It may be corrupted or invalid. Error: {str(parse_err)}")
            elif file_name.lower().endswith(".csv"):
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes))
                except Exception as parse_err:
                    raise ValueError(f"Failed to parse CSV file. It may be corrupted or invalid. Error: {str(parse_err)}")
            else:
                raise ValueError("Unsupported file format. Only CSV and Excel (.xlsx) are supported.")

            if df.empty or len(df) == 0:
                raise ValueError("File is empty. No data rows found.")

            # Record column count
            db_dataset.column_count = len(df.columns)
            self.db.commit()

            df = df.replace({np.nan: None})

            # 1.5 Route to FIR Import Service if normalized FIR schema is detected
            from backend.services.fir_import_service import FIRImportService
            fir_importer = FIRImportService(self.db)
            detected_schema = fir_importer.detect_schema_type(df.columns)

            if detected_schema == "fir_normalized":
                db_dataset.schema_type = "fir_normalized"
                self.db.commit()

                # Aliased Header Normalization mapping
                ALIAS_MAP = {
                    "case_category": "case_category",
                    "category": "case_category",
                    "gravity_offence": "gravity_offence",
                    "gravity": "gravity_offence",
                    "case_status": "case_status",
                    "status": "case_status",
                    "state": "state",
                    "district": "district",
                    "court": "court",
                    "unit_type": "unit_type",
                    "unit": "unit",
                    "police_station": "unit",
                    "officer_kgid": "officer_kgid",
                    "kgid": "officer_kgid",
                    "officer_name": "officer_name",
                    "officer_rank": "officer_rank",
                    "rank": "officer_rank",
                    "officer_designation": "officer_designation",
                    "designation": "officer_designation",
                    "officer_dob": "officer_dob",
                    "officer_gender": "officer_gender",
                    "officer_blood_group": "officer_blood_group",
                    "officer_physically_challenged": "officer_physically_challenged",
                    "officer_appointment_date": "officer_appointment_date",
                    "crime_no": "crime_no",
                    "crimeno": "crime_no",
                    "case_no": "case_no",
                    "caseno": "case_no",
                    "registered_date": "registered_date",
                    "crime_registered_date": "registered_date",
                    "brief_facts": "brief_facts",
                    "incident_from_date": "incident_from_date",
                    "incident_to_date": "incident_to_date",
                    "info_received_date": "info_received_date",
                    "latitude": "latitude",
                    "lat": "latitude",
                    "longitude": "longitude",
                    "lng": "longitude",
                    "lon": "longitude",
                    "occurrence_brief_facts": "occurrence_brief_facts",
                    "crime_group_name": "crime_group_name",
                    "crime_head_name": "crime_head_name",
                    "act_code": "act_code",
                    "act_description": "act_description",
                    "short_name": "short_name",
                    "section_code": "section_code",
                    "section_description": "section_description",
                    "act_order": "act_order",
                    "section_order": "section_order",
                    "complainant_name": "complainant_name",
                    "complainant_age": "complainant_age",
                    "complainant_occupation": "complainant_occupation",
                    "complainant_religion": "complainant_religion",
                    "complainant_caste": "complainant_caste",
                    "complainant_gender": "complainant_gender",
                    "victim_name": "victim_name",
                    "victim_age": "victim_age",
                    "victim_gender": "victim_gender",
                    "victim_police": "victim_police",
                    "accused_name": "accused_name",
                    "accused_age": "accused_age",
                    "accused_gender": "accused_gender",
                    "accused_person_id": "accused_person_id",
                    "arrest_type": "arrest_type",
                    "arrest_date": "arrest_date",
                    "arrest_state": "arrest_state",
                    "arrest_district": "arrest_district",
                    "arrest_station": "arrest_station",
                    "arrest_io_kgid": "arrest_io_kgid",
                    "arrest_court": "arrest_court",
                    "arrest_primary_accused_name": "arrest_primary_accused_name",
                    "arrest_joint_accused_names": "arrest_joint_accused_names",
                    "chargesheet_date": "chargesheet_date",
                    "chargesheet_type": "chargesheet_type",
                    "chargesheet_officer_kgid": "chargesheet_officer_kgid"
                }

                # Normalization alias mapping: normalized header name to the standard database column name
                def normalize_header(header: str) -> str:
                    h = str(header).strip().lower()
                    h = h.lstrip('\ufeff')
                    h = h.replace(" ", "_").replace("-", "_").replace(".", "_")
                    h = re.sub(r'[^a-z0-9_]', '', h)
                    h = re.sub(r'_+', '_', h)
                    return h.strip('_')

                df.columns = [normalize_header(c) for c in df.columns]
                rename_dict = {col: ALIAS_MAP[col] for col in df.columns if col in ALIAS_MAP}
                df = df.rename(columns=rename_dict)

                rows = df.to_dict(orient="records")

                # Dry-run Ingestion validations
                val_errors = fir_importer.validate_rows(rows)
                if val_errors:
                    raise ValueError("Validation errors: " + " | ".join(val_errors))

                # Transition to 'Importing'
                db_dataset.status = "Importing"
                self.db.commit()

                # Import via single transaction
                summary = fir_importer.import_normalized_dataset(rows, db_dataset.id, user_id)

                # Set dataset status to Ready
                db_dataset.status = "Ready"
                db_dataset.row_count = summary["cases_inserted"]
                db_dataset.import_summary = json.dumps(summary)
                self.db.commit()

                # Automatically activate dataset
                self.activate_dataset(db_dataset.id)
                return db_dataset

            # Normalization alias mapping: normalized header name to the standard database column name
            def normalize_header(header: str) -> str:
                h = str(header).strip().lower()
                # Remove BOM characters
                h = h.lstrip('\ufeff')
                # Replace various separators with underscore
                h = h.replace(" ", "_").replace("-", "_").replace(".", "_")
                # Remove non-alphanumeric, non-underscore characters
                h = re.sub(r'[^a-z0-9_]', '', h)
                # Collapse multiple underscores
                h = re.sub(r'_+', '_', h)
                # Strip leading/trailing underscores
                h = h.strip('_')
                return h

            ALIAS_MAP = {
                # FIR ID
                "fir_id": "fir_id",
                "firid": "fir_id",
                "fir_no": "fir_id",
                "fir_number": "fir_id",
                "firno": "fir_id",
                "case_id": "fir_id",
                "case_number": "fir_id",
                # Crime Type
                "crime_type": "crime_type",
                "crimetype": "crime_type",
                "type_of_crime": "crime_type",
                "offence_type": "crime_type",
                "offencetype": "crime_type",
                "offense_type": "crime_type",
                "type": "crime_type",
                "crime": "crime_type",
                # Crime Category
                "crime_category": "crime_category",
                "crimecategory": "crime_category",
                "category": "crime_category",
                # District
                "district": "district",
                "dist": "district",
                "district_name": "district",
                "districtname": "district",
                # Police Station
                "police_station": "police_station",
                "policestation": "police_station",
                "ps": "police_station",
                "ps_name": "police_station",
                "station": "police_station",
                "station_name": "police_station",
                "stationname": "police_station",
                "police_station_name": "police_station",
                "policestationname": "police_station",
                # Crime Date
                "crime_date": "crime_date",
                "crimedate": "crime_date",
                "date": "crime_date",
                "date_of_crime": "crime_date",
                "incident_date": "crime_date",
                "incidentdate": "crime_date",
                "offence_date": "crime_date",
                # Crime Time
                "crime_time": "crime_time",
                "crimetime": "crime_time",
                "time": "crime_time",
                "time_of_crime": "crime_time",
                "incident_time": "crime_time",
                # Latitude / Longitude
                "latitude": "latitude",
                "lat": "latitude",
                "longitude": "longitude",
                "lng": "longitude",
                "lon": "longitude",
                "long": "longitude",
                # Victim Age
                "victim_age": "victim_age",
                "victimage": "victim_age",
                "victim_s_age": "victim_age",
                "age_of_victim": "victim_age",
                # Accused Age
                "accused_age": "accused_age",
                "accusedage": "accused_age",
                "accused_s_age": "accused_age",
                "age_of_accused": "accused_age",
                "criminal_age": "accused_age",
                # Gender
                "gender": "gender",
                "sex": "gender",
                "victim_gender": "gender",
                # Occupation
                "occupation": "occupation",
                "victim_occupation": "occupation",
                # Severity
                "severity": "severity",
                "crime_severity": "severity",
                "crimeseverity": "severity",
                "seriousness": "severity",
                # Repeat Offender
                "repeat_offender": "repeat_offender",
                "repeatoffender": "repeat_offender",
                "recidivist": "repeat_offender",
                "repeat": "repeat_offender",
                # Status
                "status": "status",
                "case_status": "status",
                "casestatus": "status",
                "crime_status": "status",
            }

            df.columns = [normalize_header(c) for c in df.columns]
            rename_dict = {col: ALIAS_MAP[col] for col in df.columns if col in ALIAS_MAP}
            df = df.rename(columns=rename_dict)

            # Verify required columns exist after normalization
            required_cols = {"district", "police_station", "crime_date", "crime_type"}
            actual_cols = set(df.columns)
            missing_cols = required_cols - actual_cols
            if missing_cols:
                raise ValueError(
                    f"Missing required columns after header normalization: {sorted(missing_cols)}. "
                    f"Columns found in file: {sorted(actual_cols)}"
                )
            
            # Fetch location and station mappings
            locations = self.db.query(Location).all()
            district_to_loc_id = {loc.district: loc.id for loc in locations}

            stations = self.db.query(PoliceStation).all()
            station_to_station_id = {s.station_name: s.id for s in stations}

            first_names = ["Amit", "Rahul", "Vijay", "Sanjay", "Anil", "Sunil", "Rajesh", "Prakash", "Kiran", "Ramesh", "Deepak", "Suresh", "Priya", "Sunita", "Anita", "Geeta"]
            last_names = ["Kumar", "Sharma", "Singh", "Patil", "Gowda", "Reddy", "Nair", "Joshi", "Das", "Mehta", "Sen", "Rao", "Patel", "Chatterjee", "Mukherjee", "Pillai"]
            castes = ["General", "OBC", "SC", "ST"]

            rows = df.to_dict(orient="records")
            total_records = len(rows)
            batch_size = 5000
            
            # Perform strict dry-run validation of all rows first
            for idx, row in enumerate(rows):
                row_num = idx + 2
                
                # Required fields check (value must be non-empty after normalization)
                missing_fields = []
                for field in ["district", "police_station", "crime_date", "crime_type"]:
                    val = row.get(field)
                    if val is None or (isinstance(val, str) and val.strip() == ""):
                        missing_fields.append(field)
                if missing_fields:
                    raise ValueError(f"Row {row_num}: Missing required field values: {', '.join(missing_fields)}")

                dist = str(row["district"]).strip()
                ps = str(row["police_station"]).strip()

                loc_id = district_to_loc_id.get(dist)
                ps_id = station_to_station_id.get(ps)
                
                # Geographic mapping reference checks
                if not loc_id:
                    raise ValueError(f"Row {row_num}: District '{dist}' not found in location master data.")
                if not ps_id:
                    raise ValueError(f"Row {row_num}: Police Station '{ps}' not found in master data.")

                # Date syntax checking
                date_str = str(row["crime_date"]).strip()
                try:
                    if "/" in date_str:
                        datetime.strptime(date_str, "%d/%m/%Y").date()
                    elif "-" in date_str and len(date_str.split("-")[0]) == 2:
                        datetime.strptime(date_str, "%d-%m-%Y").date()
                    else:
                        datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Row {row_num}: Invalid date format: {date_str}. Expected YYYY-MM-DD or DD/MM/YYYY")

            # Transition to 'Importing'
            db_dataset.status = "Importing"
            self.db.commit()

            # 2. Perform Transactional Import
            successful_imports = 0
            
            for i in range(0, total_records, batch_size):
                batch_rows = rows[i:i+batch_size]
                
                crime_events = []
                victim_infos = []
                criminal_infos = []
                
                for idx, row in enumerate(batch_rows):
                    global_idx = i + idx
                    
                    dist = str(row["district"]).strip()
                    ps = str(row["police_station"]).strip()

                    loc_id = district_to_loc_id.get(dist)
                    ps_id = station_to_station_id.get(ps)

                    # Parse date and time
                    date_str = str(row["crime_date"]).strip()
                    if "/" in date_str:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                    elif "-" in date_str and len(date_str.split("-")[0]) == 2:
                        date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
                    else:
                        date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d").date()

                    time_obj = None
                    if row.get("crime_time"):
                        time_str = str(row["crime_time"]).strip()
                        try:
                            time_obj = datetime.strptime(time_str[:5], "%H:%M").time()
                        except ValueError:
                            try:
                                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                            except ValueError:
                                pass

                    # Create CrimeEvent model
                    crime = CrimeEvent(
                        crime_type=str(row["crime_type"]),
                        crime_category=str(row["crime_type"]),
                        crime_subcategory=f"{row['crime_type']} - Subcategory",
                        description=f"{row['crime_type']} incident registered under {row.get('fir_id', 'unknown')}",
                        severity=float(row["severity"]) if row.get("severity") else 1.0,
                        status=str(row.get("status", "reported")),
                        crime_date=date_obj,
                        crime_time=time_obj,
                        location_id=loc_id,
                        police_station_id=ps_id,
                        victim_count=1,
                        accused_count=1,
                        dataset_id=db_dataset.id
                    )
                    crime_events.append(crime)

                    # Prepare Victim and Criminal details
                    v_age = float(row["victim_age"]) if row.get("victim_age") else None
                    c_age = float(row["accused_age"]) if row.get("accused_age") else None
                    gender = str(row.get("gender", "Male"))
                    occ = str(row.get("occupation", "Unemployed"))

                    # Deterministic names and castes
                    c_name = f"{first_names[global_idx % len(first_names)]} {last_names[(global_idx * 3) % len(last_names)]}"
                    c_caste = castes[global_idx % len(castes)]
                    risk_score = 0.85 if str(row.get("repeat_offender")) == "1" else 0.15

                    victim_infos.append({
                        "gender": gender,
                        "age": v_age,
                        "occupation": occ,
                        "location_id": loc_id
                    })

                    criminal_infos.append({
                        "name": c_name,
                        "gender": gender,
                        "age": c_age,
                        "occupation": occ,
                        "caste": c_caste,
                        "risk_score": risk_score,
                        "status": "accused" if row.get("status") != "Closed" else "convicted"
                    })
                    successful_imports += 1

                # Insert batch
                if crime_events:
                    self.db.add_all(crime_events)
                    self.db.flush()

                    criminals_to_add = []
                    victims_to_add = []
                    for idx, crime in enumerate(crime_events):
                        c_info = criminal_infos[idx]
                        criminal = Criminal(
                            name=c_info["name"],
                            gender=c_info["gender"],
                            age=c_info["age"],
                            occupation=c_info["occupation"],
                            caste=c_info["caste"],
                            risk_score=c_info["risk_score"],
                            status=c_info["status"],
                            dataset_id=db_dataset.id
                        )
                        criminals_to_add.append(criminal)

                        v_info = victim_infos[idx]
                        victim = Victim(
                            crime_event_id=crime.id,
                            gender=v_info["gender"],
                            age=v_info["age"],
                            occupation=v_info["occupation"],
                            location_id=v_info["location_id"],
                            dataset_id=db_dataset.id
                        )
                        victims_to_add.append(victim)

                    self.db.add_all(criminals_to_add)
                    self.db.flush()

                    participations_to_add = []
                    for idx, crime in enumerate(crime_events):
                        criminal = criminals_to_add[idx]
                        participation = CrimeParticipation(
                            crime_event_id=crime.id,
                            criminal_id=criminal.id,
                            role="principal accused",
                            dataset_id=db_dataset.id
                        )
                        participations_to_add.append(participation)

                    self.db.add_all(victims_to_add + participations_to_add)
                    self.db.flush()

            # Set dataset status to Ready
            db_dataset.status = "Ready"
            db_dataset.row_count = successful_imports
            
            summary = {
                "total_rows": total_records,
                "successful_imports": successful_imports,
                "failed_imports": 0,
                "skipped_imports": 0,
                "errors": []
            }
            db_dataset.import_summary = json.dumps(summary)
            self.db.commit()
            
            # Make the newly imported dataset active so uploads immediately drive the UI.
            self.activate_dataset(db_dataset.id)
            self.db.refresh(db_dataset)

        except Exception as file_err:
            self.db.rollback()
            db_dataset.status = "Failed"
            db_dataset.upload_status = "Failed"
            
            # Parse row number for statistical tracking
            row_num_err = "unknown"
            match = re.search(r"Row (\d+):", str(file_err))
            if match:
                row_num_err = int(match.group(1))

            summary = {
                "total_rows": len(rows) if 'rows' in locals() else 0,
                "successful_imports": 0,
                "failed_imports": len(rows) if 'rows' in locals() else 1,
                "skipped_imports": 0,
                "errors": [{"row": row_num_err, "error": str(file_err)}]
            }
            db_dataset.import_summary = json.dumps(summary)
            self.db.commit()
            logger.error(f"Dataset import failed: {file_err}", exc_info=True)
            raise ValueError(f"Failed to process dataset file: {str(file_err)}")

        return db_dataset

    def get_dataset_summary(self, dataset_id: int) -> dict:
        """
        Compiles high-level statistical summary metrics for a given dataset,
        including total crimes, unique criminals, unique victims, geographic
        coverage, and date bounds.
        """
        from backend.models.crime import CrimeEvent
        from backend.models.criminal import Criminal
        from backend.models.victim import Victim
        from backend.models.location import Location
        from sqlalchemy import func

        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        total_crimes = self.db.query(CrimeEvent).filter(CrimeEvent.dataset_id == dataset_id).count()
        criminals = self.db.query(Criminal).filter(Criminal.dataset_id == dataset_id).count()
        victims = self.db.query(Victim).filter(Victim.dataset_id == dataset_id).count()

        # Date range bounds
        min_date, max_date = self.db.query(
            func.min(CrimeEvent.crime_date),
            func.max(CrimeEvent.crime_date)
        ).filter(CrimeEvent.dataset_id == dataset_id).first()

        # Unique districts list
        districts_query = self.db.query(Location.district).join(CrimeEvent).filter(
            CrimeEvent.dataset_id == dataset_id
        ).distinct().all()
        districts = [row[0] for row in districts_query if row[0]]

        return {
            "total_crimes": total_crimes,
            "criminals": criminals,
            "victims": victims,
            "date_range": {
                "min": min_date.isoformat() if min_date else None,
                "max": max_date.isoformat() if max_date else None
            },
            "districts": districts,
            "upload_time": dataset.upload_time,
            "file_size": dataset.file_size
        }

    def get_dataset_preview(self, dataset_id: int) -> dict:
        """
        Reads the first 20 rows and column metadata from the stored dataset file.
        """
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        # Resolve path
        path = dataset.storage_path
        if not path or not os.path.exists(path):
            raise ValueError(f"Dataset storage file not found for dataset ID {dataset_id}.")

        # Load file
        if path.lower().endswith(".xlsx") or path.lower().endswith(".xls"):
            df = pd.read_excel(path, engine="openpyxl")
        else:
            df = pd.read_csv(path)

        df = df.replace({np.nan: None})

        # Columns & Types
        dtypes_map = {}
        for col, dtype in df.dtypes.items():
            dtype_str = str(dtype)
            if "int" in dtype_str:
                dtypes_map[col] = "integer"
            elif "float" in dtype_str:
                dtypes_map[col] = "float"
            elif "datetime" in dtype_str:
                dtypes_map[col] = "datetime"
            elif "bool" in dtype_str:
                dtypes_map[col] = "boolean"
            else:
                dtypes_map[col] = "string"

        return {
            "first_20_rows": df.head(20).to_dict(orient="records"),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "data_types": dtypes_map
        }

    def get_dataset_statistics(self, dataset_id: int) -> dict:
        """
        Computes row/column count, missing values, duplicates, and numeric/categorical columns.
        """
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        # Resolve path
        path = dataset.storage_path
        if not path or not os.path.exists(path):
            raise ValueError(f"Dataset storage file not found for dataset ID {dataset_id}.")

        # Load file
        if path.lower().endswith(".xlsx") or path.lower().endswith(".xls"):
            df = pd.read_excel(path, engine="openpyxl")
        else:
            df = pd.read_csv(path)

        missing_values = {col: int(val) for col, val in df.isnull().sum().items()}
        duplicate_rows = int(df.duplicated().sum())
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()

        return {
            "total_rows": int(df.shape[0]),
            "total_columns": int(df.shape[1]),
            "missing_values": missing_values,
            "duplicate_rows": duplicate_rows,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns
        }

