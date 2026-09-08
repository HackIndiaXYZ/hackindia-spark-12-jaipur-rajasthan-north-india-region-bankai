from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ScenarioType(str, Enum):
    NORMAL = "normal"
    GRADUAL_LEAK = "gradual_leak"
    SUDDEN_BURST = "sudden_burst"
    SENSOR_FAULT = "sensor_fault"
    MULTIPLE_ANOMALIES = "multiple_anomalies"

class FaultType(str, Enum):
    STUCK = "stuck"
    SPIKE = "spike"
    DROP = "drop"
    HIGH_NOISE = "high_noise"

class SimulationScenarioRequest(BaseModel):
    scenario: ScenarioType = Field(ScenarioType.NORMAL, json_schema_extra={"example": "sudden_burst"})
    zone_id: Optional[str] = Field("Zone_B", json_schema_extra={"example": "Zone_B"})
    segment_id: Optional[str] = Field("B2-B3", json_schema_extra={"example": "B2-B3"})
    sensor_id: Optional[str] = Field("B3", json_schema_extra={"example": "B3"})
    duration_minutes: int = Field(60, json_schema_extra={"example": 60})
    sampling_interval_seconds: int = Field(60, json_schema_extra={"example": 60})
    leak_start_minute: int = Field(15, json_schema_extra={"example": 15})
    leak_severity: float = Field(0.5, json_schema_extra={"example": 0.6})
    fault_type: Optional[FaultType] = Field(FaultType.SPIKE, json_schema_extra={"example": "spike"})
    seed: Optional[int] = Field(42, json_schema_extra={"example": 42})

class SimulationStatusSchema(BaseModel):
    is_running: bool = Field(False, json_schema_extra={"example": True})
    current_scenario: str = Field("normal", json_schema_extra={"example": "sudden_burst"})
    total_readings_generated: int = Field(0, json_schema_extra={"example": 600})
    last_simulation_time: Optional[datetime] = None
