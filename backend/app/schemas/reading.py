from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SensorReadingBase(BaseModel):
    timestamp: datetime = Field(..., json_schema_extra={"example": "2026-09-08T10:00:00Z"})
    sensor_id: str = Field(..., json_schema_extra={"example": "B3"})
    zone_id: str = Field(..., json_schema_extra={"example": "Zone_B"})
    pipeline_segment_id: Optional[str] = Field(None, json_schema_extra={"example": "B2-B3"})
    pressure: float = Field(..., json_schema_extra={"example": 4.12})
    flow_rate: float = Field(..., json_schema_extra={"example": 145.8})
    temperature: float = Field(20.0, json_schema_extra={"example": 21.5})
    sensor_health: str = Field("HEALTHY", json_schema_extra={"example": "HEALTHY"})

class SensorReadingCreate(SensorReadingBase):
    pass

class SensorReadingSchema(SensorReadingBase):
    id: Optional[int] = None
    model_config = {"from_attributes": True}
