from pydantic import BaseModel, Field
from typing import Optional

class ZoneBase(BaseModel):
    zone_id: str = Field(..., json_schema_extra={"example": "Zone_B"})
    name: str = Field(..., json_schema_extra={"example": "Zone B - Industrial Hub"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Central industrial pipeline zone"})
    target_pressure_bar: float = Field(4.0, json_schema_extra={"example": 4.5})
    target_flow_lpm: float = Field(100.0, json_schema_extra={"example": 150.0})

class ZoneCreate(ZoneBase):
    pass

class ZoneSchema(ZoneBase):
    model_config = {"from_attributes": True}
