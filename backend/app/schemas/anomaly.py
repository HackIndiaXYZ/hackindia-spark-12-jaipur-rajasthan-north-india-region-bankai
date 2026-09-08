from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class AnomalyResultBase(BaseModel):
    sensor_id: str = Field(..., json_schema_extra={"example": "B3"})
    timestamp: datetime = Field(..., json_schema_extra={"example": "2026-09-08T10:15:00Z"})
    zone_id: str = Field(..., json_schema_extra={"example": "Zone_B"})
    pipeline_segment_id: Optional[str] = Field(None, json_schema_extra={"example": "B2-B3"})
    anomaly_score: float = Field(..., json_schema_extra={"example": 0.88})
    is_anomalous: bool = Field(..., json_schema_extra={"example": True})
    anomaly_types: List[str] = Field(default_factory=list, json_schema_extra={"example": ["PRESSURE_ANOMALY", "FLOW_ANOMALY"]})
    signals: Dict[str, float] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    persistence_count: int = Field(1, json_schema_extra={"example": 3})
    neighbor_deviation: float = Field(0.0, json_schema_extra={"example": 0.72})
    data_quality: str = Field("GOOD", json_schema_extra={"example": "GOOD"})

class AnomalyResultSchema(AnomalyResultBase):
    id: Optional[int] = None
    model_config = {"from_attributes": True}
