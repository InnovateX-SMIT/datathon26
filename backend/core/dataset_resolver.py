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
