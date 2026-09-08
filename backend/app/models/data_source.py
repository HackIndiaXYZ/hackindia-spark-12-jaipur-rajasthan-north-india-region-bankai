from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SourceType(str, Enum):
    GOVERNMENT_TELEMETRY = "GOVERNMENT_TELEMETRY"
    REGIONAL_WEATHER = "REGIONAL_WEATHER"


@dataclass
class GovernmentDataSource:
    source_id: str
    dataset_name: str
    agency: str
    source_organization: str
    geography: str
    data_frequency: str
    start_date: str
    end_date: str
    format: str
    local_file: str
    source_type: SourceType
    description: str
    unit: str
    zone: Optional[str] = None  # Always None to avoid fabricating spatial mappings


@dataclass
class GovernmentObservation:
    timestamp: str
    value: float
    unit: str
    station_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernmentObservationSummary:
    source_id: str
    latest_timestamp: Optional[str]
    latest_value: Optional[float]
    unit: str
    min_value: Optional[float]
    max_value: Optional[float]
    mean_value: Optional[float]
    median_value: Optional[float]
    observation_count: int
    missing_value_count: int
    coverage_start: Optional[str]
    coverage_end: Optional[str]
    historical_mean_deviation: Optional[float] = None
