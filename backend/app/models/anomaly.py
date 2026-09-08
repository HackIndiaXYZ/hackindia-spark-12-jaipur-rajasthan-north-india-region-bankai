from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class AnomalyResult:
    sensor_id: str
    timestamp: datetime
    zone_id: str
    pipeline_segment_id: Optional[str]
    anomaly_score: float             # 0.0 (normal) to 1.0 (highly anomalous)
    is_anomalous: bool                # True if anomaly_score >= threshold
    anomaly_types: List[str]          # PRESSURE_ANOMALY, FLOW_ANOMALY, RATE_OF_CHANGE_ANOMALY, etc.
    signals: Dict[str, float]         # z-scores, deviations, rate of change
    evidence: List[str]               # Explainable text notes
    persistence_count: int = 1        # Number of consecutive anomalous readings
    neighbor_deviation: float = 0.0   # Disagreement with connected neighbor sensors
    data_quality: str = "GOOD"        # GOOD, MISSING, FAULTY_SENSOR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp.isoformat(),
            "zone_id": self.zone_id,
            "pipeline_segment_id": self.pipeline_segment_id,
            "anomaly_score": round(self.anomaly_score, 3),
            "is_anomalous": self.is_anomalous,
            "anomaly_types": self.anomaly_types,
            "signals": {k: round(v, 3) for k, v in self.signals.items()},
            "evidence": self.evidence,
            "persistence_count": self.persistence_count,
            "neighbor_deviation": round(self.neighbor_deviation, 3),
            "data_quality": self.data_quality
        }
