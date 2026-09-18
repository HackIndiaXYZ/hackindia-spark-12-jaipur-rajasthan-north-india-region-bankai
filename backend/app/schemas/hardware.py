from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ESP32TelemetryPayload(BaseModel):
    device_id: str = Field(..., example="AQUA-ESP32-001")
    sensor_id: str = Field(..., example="FSR-P01")
    zone_id: str = Field(..., example="Zone_B")
    raw_value: int = Field(..., example=84)
    pressure_equivalent: float = Field(..., example=64.0, description="Prototype pressure-equivalent scale (not physical PSI)")
    threshold: int = Field(..., example=50)
    status: str = Field(..., example="ALERT")
    timestamp_ms: int = Field(..., example=123456)

class HardwareStateResponse(BaseModel):
    connection_state: str = Field(..., example="LIVE HARDWARE", description="LIVE HARDWARE, DISCONNECTED, or NO_DATA")
    last_received_at: Optional[str] = None
    telemetry: Optional[ESP32TelemetryPayload] = None
    derived_flow_lpm: Optional[float] = None
    pipeline_incident: Optional[Dict[str, Any]] = None
