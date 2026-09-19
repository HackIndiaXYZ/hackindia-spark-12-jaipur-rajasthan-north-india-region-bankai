from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ESP32TelemetryPayload(BaseModel):
    device_id: str = Field(..., json_schema_extra={"example": "AQUA-ESP32-001"})
    sensor_id: str = Field(..., json_schema_extra={"example": "FSR-P01"})
    zone_id: str = Field(..., json_schema_extra={"example": "Zone_B"})
    raw_value: int = Field(..., ge=0, json_schema_extra={"example": 84})
    pressure_equivalent: float = Field(..., ge=0.0, json_schema_extra={"example": 64.0}, description="Prototype pressure-equivalent scale (not physical PSI)")
    threshold: int = Field(..., ge=0, json_schema_extra={"example": 50})
    status: str = Field(..., json_schema_extra={"example": "ALERT"})
    timestamp_ms: int = Field(..., gt=0, json_schema_extra={"example": 123456})

class HardwareStateResponse(BaseModel):
    connection_state: str = Field(..., json_schema_extra={"example": "LIVE HARDWARE"}, description="LIVE HARDWARE, DISCONNECTED, or SIMULATION")
    last_received_at: Optional[str] = None
    telemetry: Optional[ESP32TelemetryPayload] = None
    derived_flow_lpm: Optional[float] = None
    pipeline_incident: Optional[Dict[str, Any]] = None

