import os
import joblib
import pandas as pd
import numpy as np
import time
import traceback
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import SessionLocal
from backend.core.logging import logger
from backend.core.exceptions import NoActiveDatasetException
from backend.models.dataset import Dataset
from backend.models.ml_model import MLModel
from backend.models.crime import CrimeEvent
from backend.models.criminal import Criminal
from backend.models.location import Location
from backend.models.crime_participation import CrimeParticipation

# SKlearn & XGBoost
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, r2_score
from xgboost import XGBClassifier, XGBRegressor

class MLTrainingService:
    def __init__(self, db: Session):
        self.db = db

    def _get_active_ids(self) -> List[int]:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db).get_active_dataset_ids()

    def validate_dataset_for_ml(self, model_type: str, active_ids: List[int]) -> None:
        """
        Validates database records for features, sample sizes, target columns, and nulls.
        Raises ValueError on failures.
        """
        if not active_ids:
            raise NoActiveDatasetException("No active dataset selected.")

        # Check dataset statuses
        for aid in active_ids:
            if aid is None:
                continue
            ds = self.db.query(Dataset).filter(Dataset.id == aid).first()
            if not ds or ds.status != "Ready":
                raise ValueError(f"Active dataset with ID {aid} is not ready or is incompatible.")

        from backend.core.dataset_resolver import DatasetResolver
        schema_type = DatasetResolver(self.db).get_active_dataset_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_people import Accused

            if model_type == "repeat_offender":
                # Accused has no risk_score target column, so we raise ValueError early rather than fabricating targets.
                raise ValueError("Offender 'risk_score' (target column) is completely empty.")

            elif model_type in ["crime_type", "crime_risk", "hotspot"]:
                count = self.db.query(CaseMaster.id).filter(
                    CaseMaster.dataset_id.in_(active_ids)
                ).count()

                if count < 10:
                    raise ValueError(f"Insufficient samples for {model_type} training. Required: >= 10, Found: {count}.")

                # Check for critical columns
                sample_types = self.db.query(CaseMaster.id).filter(
                    CaseMaster.dataset_id.in_(active_ids),
                    CaseMaster.CrimeMinorHeadID.isnot(None)
                ).limit(10).all()
                
                if not sample_types:
                    raise ValueError("Crime type target field is completely empty.")

                if model_type == "crime_risk":
                    sample_sevs = self.db.query(CaseMaster.id).filter(
                        CaseMaster.dataset_id.in_(active_ids),
                        CaseMaster.GravityOffenceID.isnot(None)
                    ).limit(10).all()
                    if not sample_sevs:
                        raise ValueError("Severity score target field is completely empty.")
        else:
            if model_type == "repeat_offender":
                # Check criminal participations
                count = self.db.query(Criminal.id).join(
                    CrimeParticipation, Criminal.id == CrimeParticipation.criminal_id
                ).join(
                    CrimeEvent, CrimeParticipation.crime_event_id == CrimeEvent.id
                ).join(
                    Location, CrimeEvent.location_id == Location.id
                ).filter(
                    Criminal.dataset_id.in_(active_ids)
                ).count()
                
                if count < 10:
                    raise ValueError(f"Insufficient samples for offender training. Required: >= 10, Found: {count}.")

                # Validate target column values
                sample_scores = self.db.query(Criminal.risk_score).filter(
                    Criminal.dataset_id.in_(active_ids),
                    Criminal.risk_score.isnot(None)
                ).limit(20).all()
                
                if not sample_scores:
                    raise ValueError("Offender 'risk_score' (target column) is completely empty.")

            elif model_type in ["crime_type", "crime_risk", "hotspot"]:
                count = self.db.query(CrimeEvent.id).join(
                    Location, CrimeEvent.location_id == Location.id
                ).filter(
                    CrimeEvent.dataset_id.in_(active_ids)
                ).count()

                if count < 10:
                    raise ValueError(f"Insufficient samples for {model_type} training. Required: >= 10, Found: {count}.")

                # Check for critical columns
                sample_types = self.db.query(CrimeEvent.crime_type).filter(
                    CrimeEvent.dataset_id.in_(active_ids),
                    CrimeEvent.crime_type.isnot(None)
                ).limit(10).all()
                
                if not sample_types:
                    raise ValueError("Crime type target field is completely empty.")

                if model_type == "crime_risk":
                    sample_sevs = self.db.query(CrimeEvent.severity).filter(
                        CrimeEvent.dataset_id.in_(active_ids),
                        CrimeEvent.severity.isnot(None)
                    ).limit(10).all()
                    if not sample_sevs:
                        raise ValueError("Severity score target field is completely empty.")

    def trigger_retraining(self, model_type: str) -> MLModel:
        """
        Triggers training in the background. Creates queued model.
        """
        active_ids = self._get_active_ids()
        self.validate_dataset_for_ml(model_type, active_ids)

        version = f"v_{model_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        dataset_ids_str = ",".join(str(i) for i in active_ids)

        model_record = MLModel(
            version=version,
            model_type=model_type,
            training_dataset_ids=dataset_ids_str,
            algorithm="XGBoost",
            status="Queued",
            is_production=False,
            training_logs=f"[{datetime.utcnow().isoformat()}] Training task initialized in queue.\n"
        )
        self.db.add(model_record)
        self.db.commit()
        self.db.refresh(model_record)

        # Launch background thread
        thread = threading.Thread(
            target=self._run_training_pipeline_thread,
            args=(model_record.id, active_ids),
            daemon=True
        )
        thread.start()

        return model_record

    def _run_training_pipeline_thread(self, model_id: int, active_ids: List[int]):
        db = SessionLocal()
        logs = []
        
        def append_log(msg: str):
            timestamp = datetime.utcnow().isoformat()
            full_msg = f"[{timestamp}] {msg}"
            logs.append(full_msg)
            logger.info(f"[ML Training Model {model_id}] {msg}")
            
            # Write progress directly to DB
            db.query(MLModel).filter(MLModel.id == model_id).update({
                MLModel.training_logs: "\n".join(logs) + "\n"
            })
            db.commit()

        start_time = time.time()
        try:
            model_record = db.query(MLModel).filter(MLModel.id == model_id).first()
            if not model_record:
                logger.error(f"Model record {model_id} not found in background training thread.")
                return

            # Stage 1: Preparing Data
            db.query(MLModel).filter(MLModel.id == model_id).update({MLModel.status: "Preparing Data"})
            db.commit()
            append_log(f"Starting data preparation for model type: {model_record.model_type}")
            append_log(f"Active dataset IDs scope: {active_ids}")

            df = self._load_dataframe(db, model_record.model_type, active_ids, append_log)
            append_log(f"Successfully loaded dataframe containing {len(df)} rows.")

            # Stage 2: Preprocessing
            db.query(MLModel).filter(MLModel.id == model_id).update({MLModel.status: "Preprocessing"})
            db.commit()
            append_log("Starting automated feature engineering & preprocessing pipeline...")
            
            preprocess_result = self._preprocess_and_split(model_record.model_type, df, append_log)

            # Stage 3: Training
            db.query(MLModel).filter(MLModel.id == model_id).update({MLModel.status: "Training"})
            db.commit()
            append_log("Fitting XGBoost model...")

            model_obj = self._train_model_object(
                model_record.model_type,
                preprocess_result["X_train_proc"],
                preprocess_result["y_train"],
                append_log
            )

            # Stage 4: Evaluating
            db.query(MLModel).filter(MLModel.id == model_id).update({MLModel.status: "Evaluating"})
            db.commit()
            append_log("Evaluating model performance on test split...")
            
            metrics = self._evaluate_metrics(
                model_record.model_type,
                model_obj,
                preprocess_result["X_test_proc"],
                preprocess_result["y_test"],
                append_log
            )

            # Stage 5: Saving Model
            db.query(MLModel).filter(MLModel.id == model_id).update({MLModel.status: "Saving Model"})
            db.commit()
            append_log("Packaging model artifacts...")

            # Save models to directory
            model_dir = os.path.join("datasets", "models")
            os.makedirs(model_dir, exist_ok=True)
            model_filename = f"{model_record.model_type}_{model_record.version}.pkl"
            model_filepath = os.path.join(model_dir, model_filename)

            artifact_dict = {
                "preprocessor": preprocess_result["preprocessor"],
                "model": model_obj,
                "feature_names": preprocess_result["feature_names"]
            }
            if "label_encoder" in preprocess_result:
                artifact_dict["label_encoder"] = preprocess_result["label_encoder"]

            joblib.dump(artifact_dict, model_filepath)
            append_log(f"Model artifact successfully written to: {model_filepath}")

            duration = time.time() - start_time
            append_log(f"Training completed successfully in {duration:.2f} seconds.")

            # Update final success status in DB
            db.query(MLModel).filter(MLModel.id == model_id).update({
                MLModel.status: "Completed",
                MLModel.accuracy: metrics.get("accuracy"),
                MLModel.precision: metrics.get("precision"),
                MLModel.recall: metrics.get("recall"),
                MLModel.f1_score: metrics.get("f1_score"),
                MLModel.roc_auc: metrics.get("roc_auc"),
                MLModel.training_duration: duration,
                MLModel.model_path: model_filepath
            })
            db.commit()

            # Automatically set as production model if no other production model of this type exists
            prod_exists = db.query(MLModel).filter(
                MLModel.model_type == model_record.model_type,
                MLModel.status == "Completed",
                MLModel.is_production == True
            ).first()
            if not prod_exists:
                append_log("No active production model found of this type. Autoseeding this version as production.")
                db.query(MLModel).filter(MLModel.id == model_id).update({MLModel.is_production: True})
                db.commit()

        except Exception as e:
            tb_str = traceback.format_exc()
            append_log(f"CRITICAL ERROR: Training pipeline failed.\nException: {str(e)}\nTraceback:\n{tb_str}")
            db.query(MLModel).filter(MLModel.id == model_id).update({
                MLModel.status: "Failed"
            })
            db.commit()
        finally:
            db.close()

    def _load_dataframe(self, db: Session, model_type: str, active_ids: List[int], log_fn) -> pd.DataFrame:
        from backend.core.dataset_resolver import DatasetResolver
        schema_type = DatasetResolver(db).get_active_dataset_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_people import Accused
            from backend.models.fir_case import CaseMaster, Inv_OccuranceTime
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeSubHead
            from backend.models.fir_lookup import GravityOffence
            from backend.core.severity import resolve_gravity_severity

            if model_type == "repeat_offender":
                log_fn("Querying offender records...")
                query = db.query(
                    Accused.AgeYear,
                    District.name
                ).select_from(Accused).join(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).filter(
                    CaseMaster.dataset_id.in_(active_ids)
                )
                results = query.all()
                return pd.DataFrame([
                    {
                        "age": float(r[0]) if r[0] is not None else 30.0,
                        "occupation": "Unknown",
                        "caste": "Unknown",
                        "district": r[1],
                        "risk_score": None  # No fabricated target labels!
                    } for r in results
                ])

            elif model_type in ["crime_type", "crime_risk"]:
                log_fn(f"Querying crime events for {model_type}...")
                query = db.query(
                    CrimeSubHead.CrimeHeadName,
                    District.name,
                    CaseMaster.CrimeRegisteredDate,
                    GravityOffence.name
                ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).join(
                    CrimeSubHead, CaseMaster.CrimeMinorHeadID == CrimeSubHead.id
                ).join(
                    GravityOffence, CaseMaster.GravityOffenceID == GravityOffence.id
                ).filter(
                    CaseMaster.dataset_id.in_(active_ids)
                )
                results = query.all()
                return pd.DataFrame([
                    {
                        "crime_category": r[0],
                        "district": r[1],
                        "crime_date": r[2].isoformat() if hasattr(r[2], "isoformat") else str(r[2]),
                        "crime_time": "12:00:00",
                        "severity": resolve_gravity_severity(r[3])
                    } for r in results
                ])

            elif model_type == "hotspot":
                log_fn("Querying monthly incident aggregations for hotspot...")
                query = db.query(
                    CaseMaster.id,
                    District.name,
                    CaseMaster.CrimeRegisteredDate
                ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(District, Unit.DistrictID == District.id).filter(
                    CaseMaster.dataset_id.in_(active_ids)
                )
                results = query.all()
                return pd.DataFrame([
                    {
                        "id": r[0],
                        "district": r[1],
                        "crime_date": r[2].isoformat() if hasattr(r[2], "isoformat") else str(r[2])
                    } for r in results
                ])
        else:
            if model_type == "repeat_offender":
                log_fn("Querying offender records...")
                query = db.query(
                    Criminal.age,
                    Criminal.occupation,
                    Criminal.caste,
                    Location.district,
                    Criminal.risk_score
                ).join(
                    CrimeParticipation, Criminal.id == CrimeParticipation.criminal_id
                ).join(
                    CrimeEvent, CrimeParticipation.crime_event_id == CrimeEvent.id
                ).join(
                    Location, CrimeEvent.location_id == Location.id
                ).filter(
                    Criminal.dataset_id.in_(active_ids)
                )
                results = query.all()
                return pd.DataFrame([
                    {
                        "age": r[0],
                        "occupation": r[1],
                        "caste": r[2],
                        "district": r[3],
                        "risk_score": r[4]
                    } for r in results
                ])

            elif model_type in ["crime_type", "crime_risk"]:
                log_fn(f"Querying crime events for {model_type}...")
                query = db.query(
                    CrimeEvent.crime_type.label("crime_category"),
                    Location.district,
                    CrimeEvent.crime_date,
                    CrimeEvent.crime_time,
                    CrimeEvent.severity
                ).join(
                    Location, CrimeEvent.location_id == Location.id
                ).filter(
                    CrimeEvent.dataset_id.in_(active_ids)
                )
                results = query.all()
                return pd.DataFrame([
                    {
                        "crime_category": r[0],
                        "district": r[1],
                        "crime_date": r[2].isoformat() if hasattr(r[2], "isoformat") else str(r[2]),
                        "crime_time": r[3],
                        "severity": r[4]
                    } for r in results
                ])

            elif model_type == "hotspot":
                log_fn("Querying monthly incident aggregations for hotspot...")
                query = db.query(
                    CrimeEvent.id,
                    Location.district,
                    CrimeEvent.crime_date
                ).join(
                    Location, CrimeEvent.location_id == Location.id
                ).filter(
                    CrimeEvent.dataset_id.in_(active_ids)
                )
                results = query.all()
                return pd.DataFrame([
                    {
                        "id": r[0],
                        "district": r[1],
                        "crime_date": r[2].isoformat() if hasattr(r[2], "isoformat") else str(r[2])
                    } for r in results
                ])

        raise ValueError(f"Unknown model type: {model_type}")

    def _extract_feature_names(self, preprocessor: ColumnTransformer, num_features: List[str], cat_features: List[str]) -> List[str]:
        try:
            cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
            encoded_cat_names = cat_encoder.get_feature_names_out(cat_features)
            feature_names = list(num_features) + list(encoded_cat_names)
            return [f.replace("[", "").replace("]", "").replace("<", "") for f in feature_names]
        except Exception:
            return list(num_features) + list(cat_features)

    def _preprocess_and_split(self, model_type: str, df: pd.DataFrame, log_fn) -> Dict[str, Any]:
        if model_type == "repeat_offender":
            X = df[["age", "occupation", "caste", "district"]]
            # Binary target: risk score > 0.5
            y = (df["risk_score"] > 0.5).astype(int)

            num_features = ["age"]
            cat_features = ["occupation", "caste", "district"]

            preprocessor = self._build_preprocessor(num_features, cat_features)
            
            log_fn("Splitting training / testing datasets (80/20)...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            log_fn("Fitting transformation pipeline...")
            X_train_proc = preprocessor.fit_transform(X_train)
            X_test_proc = preprocessor.transform(X_test)

            feature_names = self._extract_feature_names(preprocessor, num_features, cat_features)

            return {
                "preprocessor": preprocessor,
                "X_train_proc": X_train_proc,
                "X_test_proc": X_test_proc,
                "y_train": y_train,
                "y_test": y_test,
                "feature_names": feature_names
            }

        elif model_type == "crime_type":
            # Preprocess temporal features
            df["crime_date"] = pd.to_datetime(df["crime_date"])
            df["month"] = df["crime_date"].dt.month
            df["day_of_week"] = df["crime_date"].dt.dayofweek
            
            def parse_hour(time_str):
                if not time_str:
                    return 12
                try:
                    return int(time_str.split(":")[0])
                except Exception:
                    return 12
            df["hour"] = df["crime_time"].apply(parse_hour)

            # Historical crime count by district
            district_counts = df["district"].value_counts().to_dict()
            df["historical_crime_count"] = df["district"].map(district_counts)

            X = df[["district", "month", "hour", "day_of_week", "historical_crime_count"]]
            
            # Label encode multi-class target
            le = LabelEncoder()
            y = le.fit_transform(df["crime_category"])

            num_features = ["month", "hour", "day_of_week", "historical_crime_count"]
            cat_features = ["district"]

            preprocessor = self._build_preprocessor(num_features, cat_features)

            log_fn("Splitting datasets (80/20)...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            X_train_proc = preprocessor.fit_transform(X_train)
            X_test_proc = preprocessor.transform(X_test)

            feature_names = self._extract_feature_names(preprocessor, num_features, cat_features)

            return {
                "preprocessor": preprocessor,
                "label_encoder": le,
                "X_train_proc": X_train_proc,
                "X_test_proc": X_test_proc,
                "y_train": y_train,
                "y_test": y_test,
                "feature_names": feature_names
            }

        elif model_type == "crime_risk":
            # Grouping by district, crime_category to define target score
            df["crime_date"] = pd.to_datetime(df["crime_date"])
            df["year"] = df["crime_date"].dt.year

            df_grouped = df.groupby(["district", "crime_category", "year"]).agg(
                crime_count=("severity", "count"),
                avg_severity=("severity", "mean")
            ).reset_index()

            # Score calculations: max count scaling + severity
            max_count = df_grouped["crime_count"].max() if len(df_grouped) > 0 else 1
            df_grouped["risk_score"] = (df_grouped["crime_count"] / max_count) * 80 + df_grouped["avg_severity"] * 2
            df_grouped["risk_score"] = df_grouped["risk_score"].clip(0, 100)

            X = df_grouped[["district", "crime_category", "crime_count"]]
            X = X.rename(columns={"crime_count": "historical_crime_count"})
            y = df_grouped["risk_score"]

            num_features = ["historical_crime_count"]
            cat_features = ["district", "crime_category"]

            preprocessor = self._build_preprocessor(num_features, cat_features)

            log_fn("Splitting training / testing sets (80/20)...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            X_train_proc = preprocessor.fit_transform(X_train)
            X_test_proc = preprocessor.transform(X_test)

            feature_names = self._extract_feature_names(preprocessor, num_features, cat_features)

            return {
                "preprocessor": preprocessor,
                "X_train_proc": X_train_proc,
                "X_test_proc": X_test_proc,
                "y_train": y_train,
                "y_test": y_test,
                "feature_names": feature_names
            }

        elif model_type == "hotspot":
            df["year_month"] = pd.to_datetime(df["crime_date"]).dt.to_period("M").astype(str)
            
            # Monthly counts by district
            agg_df = df.groupby(["district", "year_month"]).size().reset_index(name="crime_count")
            agg_df = agg_df.sort_values(by=["district", "year_month"]).reset_index(drop=True)

            agg_df["prev_crime_count"] = agg_df.groupby("district")["crime_count"].shift(1)
            agg_df["prev_crime_count"] = agg_df["prev_crime_count"].fillna(agg_df["crime_count"])

            agg_df["historical_crime_growth"] = (agg_df["crime_count"] + 1) / (agg_df["prev_crime_count"] + 1)
            agg_df["trend_metrics"] = agg_df["prev_crime_count"]

            # Top 30% monthly count maps to hotspot class
            threshold = agg_df["crime_count"].quantile(0.70) if len(agg_df) > 0 else 0
            agg_df["is_hotspot"] = (agg_df["crime_count"] >= threshold).astype(int)

            X = agg_df[["district", "trend_metrics", "historical_crime_growth"]]
            y = agg_df["is_hotspot"]

            num_features = ["trend_metrics", "historical_crime_growth"]
            cat_features = ["district"]

            preprocessor = self._build_preprocessor(num_features, cat_features)

            log_fn("Splitting training / testing sets (80/20)...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            X_train_proc = preprocessor.fit_transform(X_train)
            X_test_proc = preprocessor.transform(X_test)

            feature_names = self._extract_feature_names(preprocessor, num_features, cat_features)

            return {
                "preprocessor": preprocessor,
                "X_train_proc": X_train_proc,
                "X_test_proc": X_test_proc,
                "y_train": y_train,
                "y_test": y_test,
                "feature_names": feature_names
            }

        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def _build_preprocessor(self, num_cols: List[str], cat_cols: List[str]) -> ColumnTransformer:
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        
        cat_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        
        return ColumnTransformer(
            transformers=[
                ("num", num_transformer, num_cols),
                ("cat", cat_transformer, cat_cols)
            ]
        )

    def _train_model_object(self, model_type: str, X_train_proc: np.ndarray, y_train: pd.Series, log_fn) -> Any:
        if model_type == "crime_risk":
            log_fn("Initializing XGBRegressor for Crime Risk...")
            model = XGBRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == "crime_type":
            log_fn("Initializing XGBClassifier for Crime Type Classification...")
            model = XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                eval_metric="mlogloss"
            )
        else:
            log_fn(f"Initializing XGBClassifier for binary targets ({model_type})...")
            model = XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                eval_metric="logloss"
            )

        model.fit(X_train_proc, y_train)
        return model

    def _evaluate_metrics(self, model_type: str, model: Any, X_test_proc: np.ndarray, y_test: pd.Series, log_fn) -> Dict[str, float]:
        metrics = {}
        if model_type == "crime_risk":
            # Regression scoring
            y_pred = model.predict(X_test_proc)
            r2 = float(r2_score(y_test, y_pred))
            log_fn(f"Crime Risk R^2 evaluation score: {r2:.4f}")
            # Map accuracy metric to R^2 score for registry dashboard
            metrics["accuracy"] = max(0.0, min(r2, 1.0))
            metrics["precision"] = None
            metrics["recall"] = None
            metrics["f1_score"] = None
            metrics["roc_auc"] = None
        else:
            # Classification
            y_pred = model.predict(X_test_proc)
            acc = float(accuracy_score(y_test, y_pred))
            log_fn(f"Model Test Accuracy: {acc:.4f}")
            metrics["accuracy"] = acc

            # Precision, Recall, F1
            avg_mode = "macro" if model_type == "crime_type" else "binary"
            prec = float(precision_score(y_test, y_pred, average=avg_mode, zero_division=0))
            rec = float(recall_score(y_test, y_pred, average=avg_mode, zero_division=0))
            f1 = float(f1_score(y_test, y_pred, average=avg_mode, zero_division=0))
            
            log_fn(f"Precision: {prec:.4f}, Recall: {rec:.4f}, F1 Score: {f1:.4f}")
            metrics["precision"] = prec
            metrics["recall"] = rec
            metrics["f1_score"] = f1

            # ROC AUC
            if model_type != "crime_type":
                try:
                    y_pred_proba = model.predict_proba(X_test_proc)[:, 1]
                    auc = float(roc_auc_score(y_test, y_pred_proba))
                    log_fn(f"ROC AUC Score: {auc:.4f}")
                    metrics["roc_auc"] = auc
                except Exception:
                    metrics["roc_auc"] = None
            else:
                metrics["roc_auc"] = None
                
        return metrics

    def get_model_history(self, model_type: Optional[str] = None) -> List[MLModel]:
        query = self.db.query(MLModel)
        if model_type:
            query = query.filter(MLModel.model_type == model_type)
        return query.order_by(MLModel.created_at.desc()).all()

    def mark_production(self, model_id: int) -> MLModel:
        model = self.db.query(MLModel).filter(MLModel.id == model_id).first()
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")
        if model.status != "Completed":
            raise ValueError("Cannot mark non-completed model as production.")
        
        # Deactivate current production models of same type
        self.db.query(MLModel).filter(
            MLModel.model_type == model.model_type
        ).update({MLModel.is_production: False})
        
        model.is_production = True
        self.db.commit()
        self.db.refresh(model)
        return model

    def rollback_model(self, model_id: int) -> MLModel:
        return self.mark_production(model_id)

    def delete_model(self, model_id: int) -> None:
        model = self.db.query(MLModel).filter(MLModel.id == model_id).first()
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")
        
        # Delete file if exists
        if model.model_path and os.path.exists(model.model_path):
            try:
                os.remove(model.model_path)
            except Exception as e:
                logger.error(f"Error removing model file: {e}")
                
        self.db.delete(model)
        self.db.commit()

    def compare_models(self, model_id_1: int, model_id_2: int) -> dict:
        m1 = self.db.query(MLModel).filter(MLModel.id == model_id_1).first()
        m2 = self.db.query(MLModel).filter(MLModel.id == model_id_2).first()
        if not m1 or not m2:
            raise ValueError("One or both models not found.")
            
        metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
        diff = {}
        for m in metrics:
            val1 = getattr(m1, m, None)
            val2 = getattr(m2, m, None)
            if val1 is not None and val2 is not None:
                diff[m] = float(val2 - val1)
            else:
                diff[m] = None
                
        return {
            "model_1": m1,
            "model_2": m2,
            "metrics_difference": diff
        }
