from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class IncidentType(str, Enum):
    LEAK_SUSPECTED = "LEAK_SUSPECTED"
    SENSOR_FAULT = "SENSOR_FAULT"
    BURST_EVENT = "BURST_EVENT"

class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class CandidateSegmentScore:
    segment_id: str
    confidence: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "confidence": round(self.confidence, 3),
            "reason": self.reason
        }

@dataclass
class IncidentResult:
    incident_id: str
    incident_type: IncidentType
    severity: IncidentSeverity
    affected_segment: str
    affected_zone: str
    detected_at: datetime
    detection_delay_min: float
    confidence: float                          # 0.0 to 1.0
    responsive_sensors: List[str]
    estimated_flow_loss_lpm: float            # Liters per minute
    estimated_volume_loss_liters: float       # Total accumulated volume in liters
    candidate_segments: List[CandidateSegmentScore] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    observability_score: float = 0.0
    disclaimer: str = "Loss values are model-derived simulation estimates intended for demonstration and system evaluation."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "incident_type": self.incident_type.value,
            "severity": self.severity.value,
            "affected_segment": self.affected_segment,
            "affected_zone": self.affected_zone,
            "detected_at": self.detected_at.isoformat(),
            "detection_delay_min": round(self.detection_delay_min, 1),
            "confidence": round(self.confidence, 3),
            "responsive_sensors": self.responsive_sensors,
            "estimated_flow_loss_lpm": round(self.estimated_flow_loss_lpm, 2),
            "estimated_volume_loss_liters": round(self.estimated_volume_loss_liters, 2),
            "candidate_segments": [c.to_dict() for c in self.candidate_segments],
            "evidence": self.evidence,
            "observability_score": round(self.observability_score, 3),
            "disclaimer": self.disclaimer
        }
