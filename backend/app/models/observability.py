from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class BlindSpotLevel(str, Enum):
    HIGH_OBSERVABILITY = "HIGH_OBSERVABILITY"
    MEDIUM_OBSERVABILITY = "MEDIUM_OBSERVABILITY"
    LOW_OBSERVABILITY = "LOW_OBSERVABILITY"
    CRITICAL_BLIND_SPOT = "CRITICAL_BLIND_SPOT"

@dataclass
class SegmentObservability:
    segment_id: str
    zone_id: str
    observability_score: float                # 0.0 to 1.0
    detected: bool
    detection_delay_minutes: float           # -1.0 if not detected
    responsive_sensor_count: int
    responsive_sensor_ratio: float           # count / total_zone_sensors
    blind_spot_level: BlindSpotLevel
    maximum_anomaly_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "zone_id": self.zone_id,
            "observability_score": round(self.observability_score, 3),
            "detected": self.detected,
            "detection_delay_minutes": round(self.detection_delay_minutes, 1),
            "responsive_sensor_count": self.responsive_sensor_count,
            "responsive_sensor_ratio": round(self.responsive_sensor_ratio, 3),
            "blind_spot_level": self.blind_spot_level.value,
            "maximum_anomaly_score": round(self.maximum_anomaly_score, 3)
        }

@dataclass
class NetworkObservabilitySummary:
    overall_observability: float
    total_segments: int
    high_observability_segments: int
    medium_observability_segments: int
    low_observability_segments: int
    blind_spots: int
    weakest_segment: str
    strongest_segment: str
    segment_details: List[SegmentObservability] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_observability": round(self.overall_observability, 3),
            "total_segments": self.total_segments,
            "high_observability_segments": self.high_observability_segments,
            "medium_observability_segments": self.medium_observability_segments,
            "low_observability_segments": self.low_observability_segments,
            "blind_spots": self.blind_spots,
            "weakest_segment": self.weakest_segment,
            "strongest_segment": self.strongest_segment,
            "segment_details": [s.to_dict() for s in self.segment_details]
        }

@dataclass
class VirtualSensorCandidate:
    candidate_node: str
    target_segment_id: str
    target_zone_id: str
    value_score: float                        # 0.0 to 1.0
    baseline_observability: float
    new_observability: float
    observability_improvement_percent: float
    responsive_sensor_count_before: int
    responsive_sensor_count_after: int
    reasoning: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_node": self.candidate_node,
            "target_segment_id": self.target_segment_id,
            "target_zone_id": self.target_zone_id,
            "value_score": round(self.value_score, 3),
            "baseline_observability": round(self.baseline_observability, 3),
            "new_observability": round(self.new_observability, 3),
            "observability_improvement_percent": round(self.observability_improvement_percent, 1),
            "responsive_sensor_count_before": self.responsive_sensor_count_before,
            "responsive_sensor_count_after": self.responsive_sensor_count_after,
            "reasoning": self.reasoning
        }
