from sqlalchemy.orm import Session
from typing import List, Optional
import os
import io
import re
import json
import pandas as pd
import numpy as np
from backend.models.dataset import Dataset
from backend.core.exceptions import NoActiveDatasetException
from backend.core.logging import logger

class DatasetService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_dataset_id(self) -> Optional[int]:
        """
        Resolves the currently active dataset ID. Auto-seeds a default active dataset if
        no datasets exist in the database (ensuring seamless operation and backward-compatibility).
        """
        active_id = self.db.query(Dataset.id).filter(Dataset.is_active == True).scalar()
        if active_id is None:
            try:
                first_any = self.db.query(Dataset.id).first()
                if not first_any:
                    # Seeding the default dataset row
                    default_ds = Dataset(
                        name="System Seed",
                        original_filename="crime_events.csv",
                        display_name="Synthetic 50K",
                        description="Auto-created default dataset",
                        source_type="System Seed",
                        status="Ready",
                        is_active=True,
                        row_count=50000,
                        file_size=5872123
                    )
                    self.db.add(default_ds)
                    self.db.commit()
                    self.db.refresh(default_ds)

                    # Update any existing orphaned rows in the test/dev DB
                    from backend.models.crime import CrimeEvent
                    from backend.models.criminal import Criminal
                    from backend.models.victim import Victim
                    from backend.models.crime_participation import CrimeParticipation

                    self.db.query(CrimeEvent).filter(CrimeEvent.dataset_id == None).update({CrimeEvent.dataset_id: default_ds.id})
                    self.db.query(Criminal).filter(Criminal.dataset_id == None).update({Criminal.dataset_id: default_ds.id})
                    self.db.query(Victim).filter(Victim.dataset_id == None).update({Victim.dataset_id: default_ds.id})
                    self.db.query(CrimeParticipation).filter(CrimeParticipation.dataset_id == None).update({CrimeParticipation.dataset_id: default_ds.id})
                    self.db.commit()
                    active_id = default_ds.id
                else:
                    # If datasets exist but none are active, activate the first one
                    first_ds = self.db.query(Dataset).order_by(Dataset.id.asc()).first()
                    if first_ds:
                        first_ds.is_active = True
                        self.db.commit()
                        active_id = first_ds.id
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error auto-seeding default active dataset: {e}")
        return active_id

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
        self.get_active_dataset_id()
        return self.db.query(Dataset).filter(Dataset.is_active == True).first()

    def list_datasets(self) -> List[Dataset]:
        """
        Lists all datasets in the registry sorted by creation time.
        """
        self.get_active_dataset_id()
        return self.db.query(Dataset).order_by(Dataset.created_at.desc()).all()

    def activate_dataset(self, dataset_id: int) -> Dataset:
        """
        Sets the specified dataset as active and deactivates all others.
        """
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        # Deactivate all datasets
        self.db.query(Dataset).update({Dataset.is_active: False})
        
        # Activate this dataset
        dataset.is_active = True
        self.db.commit()
        
        logger.info(f"Dataset ID {dataset_id} ('{dataset.display_name}') set as active.")
        return dataset

    def delete_dataset(self, dataset_id: int) -> bool:
        """
        Soft-deletes (archives) the dataset from the registry. Sets status to 'Archived'
        and is_active to False. Protected datasets like 'System Seed' are blocked from deletion.
        Active datasets must be deactivated first.
        """
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        # Prevent deletion of the System Seed dataset
        if dataset.name == "System Seed" or dataset.display_name == "Synthetic 50K":
            raise ValueError("The System Seed dataset is protected and cannot be deleted.")

        # Require active dataset to be deactivated before deletion
        if dataset.is_active:
            raise ValueError("Active dataset must be deactivated before deletion.")

        # Soft delete: set status to Archived
        dataset.status = "Archived"
        dataset.is_active = False
        self.db.commit()

        logger.info(f"Dataset ID {dataset_id} soft-deleted/archived successfully.")
        return True

    def import_dataset(
        self,
        display_name: str,
        description: Optional[str],
        file_name: str,
        file_bytes: bytes,
        user_id: int
    ) -> Dataset:
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

        # Validate Duplicate Filename (excluding failed ones)
        duplicate_check = self.db.query(Dataset).filter(
            Dataset.original_filename == file_name,
            Dataset.status != "Failed"
        ).first()
        if duplicate_check:
            raise ValueError(f"A dataset with filename '{file_name}' has already been uploaded.")

        from datetime import datetime
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
            batch_size = 1000
            
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
                    self.db.commit()

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
            
            # Automatically activate first dataset if none active
            active_dataset = self.db.query(Dataset).filter(Dataset.is_active == True).first()
            if not active_dataset:
                db_dataset.is_active = True
                self.db.commit()

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
        if not path and dataset.name == "System Seed":
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = os.path.join(base_dir, "datasets", "processed", "crime_events.csv")
        
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
        if not path and dataset.name == "System Seed":
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = os.path.join(base_dir, "datasets", "processed", "crime_events.csv")
        
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

