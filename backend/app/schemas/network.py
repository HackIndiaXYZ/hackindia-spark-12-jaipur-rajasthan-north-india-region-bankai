from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.zone import ZoneSchema
from app.schemas.pipeline import PipelineSegmentSchema
from app.schemas.sensor import SensorSchema


class NetworkNodeSchema(BaseModel):
    node_id: str = Field(..., json_schema_extra={"example": "B3"})
    node_type: str = Field(..., json_schema_extra={"example": "junction"})
    elevation_m: float = Field(0.0, json_schema_extra={"example": 35.0})
    zone_id: Optional[str] = Field(None, json_schema_extra={"example": "Zone_B"})


class NetworkTopologySchema(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "AquaSentinel Synthetic Network"})
    zones: List[ZoneSchema]
    nodes: List[NetworkNodeSchema]
    segments: List[PipelineSegmentSchema]
    sensors: List[SensorSchema]


class NetworkStatusSchema(BaseModel):
    network_status: str = Field("HEALTHY", json_schema_extra={"example": "DEGRADED"})
    total_sensors: int = Field(..., json_schema_extra={"example": 10})
    healthy_sensors: int = Field(..., json_schema_extra={"example": 9})
    degraded_sensors: int = Field(..., json_schema_extra={"example": 1})
    faulty_sensors: int = Field(0, json_schema_extra={"example": 0})
    active_anomalies: int = Field(0, json_schema_extra={"example": 2})
    active_leaks: int = Field(0, json_schema_extra={"example": 1})
    estimated_total_loss_lpm: float = Field(0.0, json_schema_extra={"example": 45.2})
