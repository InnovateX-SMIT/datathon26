from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List

class DatasetSummaryResponse(BaseModel):
    total_crimes: int
    criminals: int
    victims: int
    date_range: Dict[str, Optional[str]]
    districts: List[str]
    upload_time: Optional[datetime] = None
    file_size: int

class DatasetBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    original_filename: str
    source_type: str
    row_count: Optional[int] = 0
    column_count: Optional[int] = 0
    file_size: Optional[int] = 0
    status: str = "Processing"
    upload_status: Optional[str] = "Completed"
    storage_path: Optional[str] = None
    is_active: bool = False
    import_summary: Optional[str] = None

class DatasetCreate(DatasetBase):
    pass

class DatasetResponse(DatasetBase):
    id: int
    upload_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DatasetSwitchRequest(BaseModel):
    dataset_id: int

class DatasetPreviewResponse(BaseModel):
    first_20_rows: List[Dict[str, Any]]
    total_rows: int
    total_columns: int
    columns: List[str]
    data_types: Dict[str, str]

class DatasetStatisticsResponse(BaseModel):
    total_rows: int
    total_columns: int
    missing_values: Dict[str, int]
    duplicate_rows: int
    numeric_columns: List[str]
    categorical_columns: List[str]

class DatasetConfigRequest(BaseModel):
    max_active_datasets: str

class DatasetConfigResponse(BaseModel):
    max_active_datasets: str

    model_config = ConfigDict(from_attributes=True)



