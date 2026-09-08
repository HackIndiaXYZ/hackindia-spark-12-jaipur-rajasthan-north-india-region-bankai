from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np

from app.models.reading import SensorReading
from app.models.anomaly import AnomalyResult
from app.models.incident import IncidentResult, IncidentType, IncidentSeverity
from app.models.network import WaterNetwork
from app.services.anomaly_detector import AnomalyDetector
from app.services.localization import LeakLocalizer
from app.services.loss_estimator import WaterLossEstimator
from app.services.observability import ObservabilityService
from app.core.logging import logger


class IncidentService:
    """
    End-to-End Pipeline Incident Service for AquaSentinel.
    Consumes sensor readings, runs anomaly detection, localizes leak segments,
    estimates water loss, integrates observability context, and constructs IncidentResult objects.
    """

    def __init__(self, network: Optional[WaterNetwork] = None):
        self.network = network or WaterNetwork.create_default_network()
        self.detector = AnomalyDetector(network=self.network, use_isolation_forest=False)
        self.localizer = LeakLocalizer(network=self.network)
        self.loss_estimator = WaterLossEstimator(network=self.network)
        self.observability_service = ObservabilityService(network=self.network)
        self._incident_counter = 1

    def process_telemetry(self, readings: List[SensorReading]) -> Optional[IncidentResult]:
        """
        Executes end-to-end incident analysis pipeline on incoming sensor telemetry.
        Returns IncidentResult if a pipeline leak/burst incident is detected, else None.
        """
        if not readings:
            return None

        # 1. Run Anomaly Detection
        anomaly_results = self.detector.detect(readings)
        anomalous_results = [a for a in anomaly_results if a.is_anomalous]

        if not anomalous_results:
            return None

        # 2. Run Topology-Aware Leak Localization
        loc_info = self.localizer.localize(anomaly_results)
        if not loc_info:
            logger.info("Anomalies detected but no spatial network leak pattern localized (e.g. isolated sensor fault).")
            return None

        affected_seg_id = loc_info["selected_segment"]
        affected_zone_id = loc_info["affected_zone"]

        # 3. Estimate Flow & Volume Loss
        loss_info = self.loss_estimator.estimate_loss(readings, anomaly_results, affected_seg_id)

        # 4. Integrate Milestone 4 Observability Information
        obs_summary = self.observability_service.analyze_network_observability(use_cache=True)
        obs_seg_info = next((s for s in obs_summary.segment_details if s.segment_id == affected_seg_id), None)
        obs_score = obs_seg_info.observability_score if obs_seg_info else 0.50

        # 5. Compute Normalized Incident Confidence Score [0.0 to 1.0]
        avg_anom_score = float(np.mean([a.anomaly_score for a in anomalous_results]))
        loc_confidence = loc_info["localization_confidence"]
        resp_sensors = loc_info["responsive_sensors"]
        total_zone_sensors = len(self.network.get_sensors_by_zone(affected_zone_id))
        resp_ratio = len(resp_sensors) / max(1, total_zone_sensors)

        confidence = (
            0.45 * loc_confidence +
            0.30 * avg_anom_score +
            0.15 * min(1.0, resp_ratio) +
            0.10 * obs_score
        )
        confidence = float(max(0.0, min(1.0, confidence)))

        # 6. Determine Severity Classification
        flow_loss = loss_info["estimated_flow_loss_lpm"]
        vol_loss = loss_info["estimated_volume_loss_liters"]

        if confidence >= 0.70 and (flow_loss >= 40.0 or vol_loss >= 800.0):
            severity = IncidentSeverity.CRITICAL
        elif confidence >= 0.60 and (flow_loss >= 20.0 or vol_loss >= 300.0):
            severity = IncidentSeverity.HIGH
        elif confidence >= 0.50 and flow_loss >= 10.0:
            severity = IncidentSeverity.MEDIUM
        else:
            severity = IncidentSeverity.LOW

        # 7. Determine Incident Type (Burst vs Gradual Leak)
        has_burst_signals = any("RATE_OF_CHANGE_ANOMALY" in a.anomaly_types for a in anomalous_results)
        inc_type = IncidentType.BURST_EVENT if has_burst_signals else IncidentType.LEAK_SUSPECTED

        first_detected_ts = min([a.timestamp for a in anomalous_results])
        start_ts = min([r.timestamp for r in readings])
        delay_min = (first_detected_ts - start_ts).total_seconds() / 60.0

        inc_id = f"INC-{self._incident_counter:03d}"
        self._incident_counter += 1

        evidence_notes = loc_info["evidence"] + [
            f"Estimated flow loss rate: {flow_loss:.1f} LPM ({vol_loss:.0f} Liters accumulated)",
            f"Segment observability score: {obs_score:.2f} ({obs_seg_info.blind_spot_level.value if obs_seg_info else 'N/A'})"
        ]

        return IncidentResult(
            incident_id=inc_id,
            incident_type=inc_type,
            severity=severity,
            affected_segment=affected_seg_id,
            affected_zone=affected_zone_id,
            detected_at=first_detected_ts,
            detection_delay_min=delay_min,
            confidence=confidence,
            responsive_sensors=resp_sensors,
            estimated_flow_loss_lpm=flow_loss,
            estimated_volume_loss_liters=vol_loss,
            candidate_segments=loc_info["candidate_segments"],
            evidence=evidence_notes,
            observability_score=obs_score
        )
