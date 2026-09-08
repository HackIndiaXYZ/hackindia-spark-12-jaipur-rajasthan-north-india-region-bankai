from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SensorBase(BaseModel):
    sensor_id: str = Field(..., json_schema_extra={"example": "B3"})
    zone_id: str = Field(..., json_schema_extra={"example": "Zone_B"})
    pipeline_segment_id: Optional[str] = Field(None, json_schema_extra={"example": "B2-B3"})
    location_node: str = Field(..., json_schema_extra={"example": "B3"})
    sensor_type: str = Field("multi-sensor", json_schema_extra={"example": "multi-sensor"})
    installation_metadata: Dict[str, Any] = Field(default_factory=dict)
    health_status: str = Field("HEALTHY", json_schema_extra={"example": "HEALTHY"})

class SensorCreate(SensorBase):
    pass

class SensorSchema(SensorBase):
    model_config = {"from_attributes": True}
