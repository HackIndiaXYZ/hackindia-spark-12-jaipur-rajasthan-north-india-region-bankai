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

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"

# Allowed lifecycle transitions dictionary
ALLOWED_TRANSITIONS = {
    IncidentStatus.OPEN: {IncidentStatus.ACKNOWLEDGED, IncidentStatus.RESOLVED},
    IncidentStatus.ACKNOWLEDGED: {IncidentStatus.RESOLVED},
    IncidentStatus.RESOLVED: set()
}

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
    status: IncidentStatus = IncidentStatus.OPEN
    fingerprint: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    candidate_segments: List[CandidateSegmentScore] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    observability_score: float = 0.0
    disclaimer: str = "Loss values are model-derived simulation estimates intended for demonstration and system evaluation."

    def validate_and_update_status(self, new_status: IncidentStatus) -> IncidentStatus:
        """Enforces valid incident lifecycle state transitions."""
        if new_status == self.status:
            return self.status

        allowed = ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(f"Invalid lifecycle status transition from '{self.status.value}' to '{new_status.value}'.")

        self.status = new_status
        self.updated_at = datetime.utcnow()
        return self.status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "fingerprint": self.fingerprint,
            "incident_type": self.incident_type.value if hasattr(self.incident_type, 'value') else str(self.incident_type),
            "severity": self.severity.value if hasattr(self.severity, 'value') else str(self.severity),
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "affected_segment": self.affected_segment,
            "affected_zone": self.affected_zone,
            "detected_at": self.detected_at.isoformat() if isinstance(self.detected_at, datetime) else str(self.detected_at),
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else (self.detected_at.isoformat() if isinstance(self.detected_at, datetime) else str(self.detected_at)),
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else (self.detected_at.isoformat() if isinstance(self.detected_at, datetime) else str(self.detected_at)),
            "detection_delay_min": round(self.detection_delay_min, 1),
            "confidence": round(self.confidence, 3),
            "responsive_sensors": self.responsive_sensors,
            "estimated_flow_loss_lpm": round(self.estimated_flow_loss_lpm, 2),
            "estimated_volume_loss_liters": round(self.estimated_volume_loss_liters, 2),
            "candidate_segments": [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.candidate_segments],
            "evidence": self.evidence,
            "observability_score": round(self.observability_score, 3),
            "disclaimer": self.disclaimer
        }
