from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional

class CandidateSegmentScoreSchema(BaseModel):
    segment_id: str = Field(..., json_schema_extra={"example": "B2-B3"})
    confidence: float = Field(..., json_schema_extra={"example": 0.87})
    reason: str = Field(..., json_schema_extra={"example": "Adjacent to responsive sensors B2 and B3"})

class IncidentStatusUpdateSchema(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ACKNOWLEDGED"})

class IncidentResultBase(BaseModel):
    incident_id: str = Field(..., json_schema_extra={"example": "INC-001"})
    fingerprint: Optional[str] = Field(None, json_schema_extra={"example": "a1b2c3d4e5f6"})
    incident_type: str = Field(..., json_schema_extra={"example": "LEAK_SUSPECTED"})
    severity: str = Field(..., json_schema_extra={"example": "HIGH"})
    status: str = Field("OPEN", json_schema_extra={"example": "OPEN"})
    affected_segment: str = Field(..., json_schema_extra={"example": "B2-B3"})
    affected_zone: str = Field(..., json_schema_extra={"example": "Zone_B"})
    detected_at: datetime = Field(..., json_schema_extra={"example": "2026-09-08T08:15:00Z"})
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    detection_delay_min: float = Field(..., json_schema_extra={"example": 15.0})
    confidence: float = Field(..., json_schema_extra={"example": 0.88})
    responsive_sensors: List[str] = Field(default_factory=list, json_schema_extra={"example": ["B2", "B3"]})
    estimated_flow_loss_lpm: float = Field(..., json_schema_extra={"example": 45.2})
    estimated_volume_loss_liters: float = Field(..., json_schema_extra={"example": 1356.0})
    candidate_segments: List[CandidateSegmentScoreSchema] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    observability_score: float = Field(0.0, json_schema_extra={"example": 0.89})
    disclaimer: str = Field("Loss values are model-derived simulation estimates intended for demonstration and system evaluation.")

class IncidentResultSchema(IncidentResultBase):
    id: Optional[int] = None
    model_config = {"from_attributes": True}
