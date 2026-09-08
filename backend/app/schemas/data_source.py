from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DataSourceResponse(BaseModel):
    source_id: str = Field(..., example="rajasthan_rainfall_telemetry")
    dataset_name: str = Field(..., example="Rajasthan Surface Water Telemetry Hourly Rainfall")
    agency: str = Field(..., example="Rajasthan Surface Water Department")
    source_organization: str = Field(..., example="National Water Data Portals / India WRIS")
    geography: str = Field(..., example="Rajasthan, India")
    data_frequency: str = Field(..., example="Hourly")
    start_date: Optional[str] = Field(None, example="2021-10-17 07:00")
    end_date: Optional[str] = Field(None, example="2030-01-01 08:00")
    format: str = Field(..., example="CSV / JSON")
    local_file: str = Field(..., example="rainfall_tel_hr_rajasthan_sw_rj_2021_2025.csv")
    source_type: str = Field(..., example="GOVERNMENT_TELEMETRY")
    description: str = Field(..., example="Hourly regional rainfall telemetry observations from rain stations in Rajasthan.")
    unit: str = Field(..., example="mm")
    zone: Optional[str] = Field(None, description="Regional context; null if not spatially mapped to network zone.")


class DataSourceListResponse(BaseModel):
    sources: List[DataSourceResponse]
    total_count: int


class DataSourceSummaryResponse(BaseModel):
    source_id: str
    latest_timestamp: Optional[str] = None
    latest_value: Optional[float] = None
    unit: str = Field(..., example="mm")
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    observation_count: int = 0
    missing_value_count: int = 0
    coverage_start: Optional[str] = None
    coverage_end: Optional[str] = None
    historical_mean_deviation: Optional[float] = None


class ObservationResponse(BaseModel):
    timestamp: str
    value: float
    unit: str
    station_name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ObservationListResponse(BaseModel):
    source_id: str
    observations: List[ObservationResponse]
    total_returned: int
