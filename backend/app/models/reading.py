from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class SensorReading:
    timestamp: datetime
    sensor_id: str
    zone_id: str
    pipeline_segment_id: Optional[str]
    pressure: float           # in Bar
    flow_rate: float          # in Liters per minute (LPM)
    temperature: float        # in Celsius
    sensor_health: str = "HEALTHY"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "sensor_id": self.sensor_id,
            "zone_id": self.zone_id,
            "pipeline_segment_id": self.pipeline_segment_id,
            "pressure": round(self.pressure, 3),
            "flow_rate": round(self.flow_rate, 3),
            "temperature": round(self.temperature, 2),
            "sensor_health": self.sensor_health
        }
