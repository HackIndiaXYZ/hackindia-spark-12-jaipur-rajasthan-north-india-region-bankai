from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAULTY = "FAULTY"

@dataclass
class Sensor:
    sensor_id: str
    zone_id: str
    pipeline_segment_id: Optional[str]
    location_node: str
    sensor_type: str = "multi-sensor"  # "pressure", "flow", "multi-sensor"
    installation_metadata: Dict[str, Any] = field(default_factory=dict)
    health_status: HealthStatus = HealthStatus.HEALTHY
