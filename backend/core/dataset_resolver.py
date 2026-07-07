from sqlalchemy.orm import Session
from typing import Optional
from backend.core.exceptions import NoActiveDatasetException

class DatasetResolver:
    def __init__(self, db: Session):
        self.db = db

    def get_active_dataset_id(self) -> int:
        """
        Resolves the currently active dataset ID or raises NoActiveDatasetException.
        """
        from backend.services.dataset_service import DatasetService
        return DatasetService(self.db).get_active_dataset_id_or_raise()

    def get_active_dataset_id_optional(self) -> Optional[int]:
        """
        Resolves the active dataset ID, returning None if none is active.
        """
        from backend.services.dataset_service import DatasetService
        return DatasetService(self.db).get_active_dataset_id()

    def get_active_dataset_ids(self) -> list[int]:
        """
        Resolves all currently active dataset IDs or raises NoActiveDatasetException.
        """
        from backend.services.dataset_service import DatasetService
        ids = DatasetService(self.db).get_active_dataset_ids()
        if not ids:
            raise NoActiveDatasetException()
        return ids

    def get_active_dataset_ids_optional(self) -> list[int]:
        """
        Resolves all currently active dataset IDs, returning an empty list if none are active.
        """
        from backend.services.dataset_service import DatasetService
        return DatasetService(self.db).get_active_dataset_ids()

    def get_active_dataset_schema_type(self) -> str:
        """
        Resolves the schema type of the currently active dataset.
        Returns "legacy_crime_intel" or "fir_normalized".
        """
        from backend.services.dataset_service import DatasetService
        active_ds = DatasetService(self.db).get_active_dataset()
        if not active_ds:
            raise NoActiveDatasetException()
        return active_ds.schema_type or "legacy_crime_intel"

    def get_dataset_schema_type(self, dataset_id: int) -> str:
        """
        Resolves the schema type for a specific dataset ID.
        """
        from backend.models.dataset import Dataset
        ds = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")
        return ds.schema_type or "legacy_crime_intel"
