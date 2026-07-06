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
