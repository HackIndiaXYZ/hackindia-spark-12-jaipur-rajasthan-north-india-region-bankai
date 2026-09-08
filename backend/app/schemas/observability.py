from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SegmentObservabilitySchema(BaseModel):
    segment_id: str = Field(..., json_schema_extra={"example": "C2-C3"})
    zone_id: str = Field(..., json_schema_extra={"example": "Zone_C"})
    observability_score: float = Field(..., json_schema_extra={"example": 0.41})
    detected: bool = Field(..., json_schema_extra={"example": True})
    detection_delay_minutes: float = Field(..., json_schema_extra={"example": 37.0})
    responsive_sensor_count: int = Field(..., json_schema_extra={"example": 2})
    responsive_sensor_ratio: float = Field(..., json_schema_extra={"example": 0.50})
    blind_spot_level: str = Field(..., json_schema_extra={"example": "HIGH_OBSERVABILITY"})
    maximum_anomaly_score: float = Field(..., json_schema_extra={"example": 0.84})

class NetworkObservabilitySummarySchema(BaseModel):
    overall_observability: float = Field(..., json_schema_extra={"example": 0.72})
    total_segments: int = Field(..., json_schema_extra={"example": 10})
    high_observability_segments: int = Field(..., json_schema_extra={"example": 6})
    medium_observability_segments: int = Field(..., json_schema_extra={"example": 2})
    low_observability_segments: int = Field(..., json_schema_extra={"example": 2})
    blind_spots: int = Field(..., json_schema_extra={"example": 1})
    weakest_segment: str = Field(..., json_schema_extra={"example": "C2-C3"})
    strongest_segment: str = Field(..., json_schema_extra={"example": "B2-B3"})
    segment_details: List[SegmentObservabilitySchema] = Field(default_factory=list)

class VirtualSensorCandidateSchema(BaseModel):
    candidate_node: str = Field(..., json_schema_extra={"example": "C3"})
    target_segment_id: str = Field(..., json_schema_extra={"example": "C2-C3"})
    target_zone_id: str = Field(..., json_schema_extra={"example": "Zone_C"})
    value_score: float = Field(..., json_schema_extra={"example": 0.81})
    baseline_observability: float = Field(..., json_schema_extra={"example": 0.41})
    new_observability: float = Field(..., json_schema_extra={"example": 0.78})
    observability_improvement_percent: float = Field(..., json_schema_extra={"example": 90.2})
    responsive_sensor_count_before: int = Field(..., json_schema_extra={"example": 2})
    responsive_sensor_count_after: int = Field(..., json_schema_extra={"example": 4})
    reasoning: List[str] = Field(default_factory=list)
