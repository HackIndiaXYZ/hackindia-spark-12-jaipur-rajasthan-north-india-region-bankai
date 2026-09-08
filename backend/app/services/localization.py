from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.models.network import WaterNetwork, PipelineSegment
from app.models.anomaly import AnomalyResult
from app.models.incident import CandidateSegmentScore
from app.core.logging import logger


class LeakLocalizer:
    """
    Topology-aware Leak Localization engine for AquaSentinel.
    Uses NetworkX graph structure and anomalous sensor spatial relationships
    to identify candidate and selected pipeline segments.
    """

    def __init__(self, network: Optional[WaterNetwork] = None):
        self.network = network or WaterNetwork.create_default_network()

    def localize(self, anomaly_results: List[AnomalyResult]) -> Optional[Dict[str, Any]]:
        """
        Analyzes anomaly detection results and returns localized segment analysis.
        Returns None if no leak-level spatial anomaly pattern is identified.
        """
        anomalous_results = [a for a in anomaly_results if a.is_anomalous]
        if not anomalous_results:
            return None

        # Group anomalous sensors by zone
        zone_anomalies: Dict[str, List[AnomalyResult]] = {}
        for a in anomalous_results:
            zone_anomalies.setdefault(a.zone_id, []).append(a)

        # Pick zone with highest combined anomaly score
        target_zone_id = max(zone_anomalies.keys(), key=lambda z: sum(a.anomaly_score for a in zone_anomalies[z]))
        zone_results = zone_anomalies[target_zone_id]

        responsive_sensors = sorted(list(set(a.sensor_id for a in zone_results)))

        # Check for isolated sensor fault vs true network event
        if len(responsive_sensors) == 1:
            single_res = zone_results[0]
            if single_res.data_quality == "FAULTY_SENSOR" or "SENSOR_ISOLATION_ANOMALY" in single_res.anomaly_types:
                logger.info(f"Isolated anomaly on sensor {responsive_sensors[0]} classified as sensor fault, not a pipeline leak.")
                return None

        # Find all candidate segments in the target zone
        zone_segments = self.network.get_segments_by_zone(target_zone_id)
        if not zone_segments:
            return None

        # Sensors with pressure drop vs flow increase
        pressure_drop_sensors = set(
            a.sensor_id for a in zone_results
            if any("Pressure deviation of -" in e for e in a.evidence) or "PRESSURE_ANOMALY" in a.anomaly_types
        )
        flow_increase_sensors = set(
            a.sensor_id for a in zone_results
            if any("Flow rate deviation of +" in e for e in a.evidence) or "FLOW_ANOMALY" in a.anomaly_types
        )

        candidate_scores: Dict[str, Tuple[float, List[str]]] = {}

        for seg in zone_segments:
            score = 0.0
            reasons = []

            # Factor 1: Sensors mounted on segment or at nodes
            source_sensor = [s for s in self.network.sensors.values() if s.location_node == seg.source_node and s.sensor_id in responsive_sensors]
            dest_sensor = [s for s in self.network.sensors.values() if s.location_node == seg.destination_node and s.sensor_id in responsive_sensors]
            direct_sensor = [s for s in self.network.sensors.values() if s.pipeline_segment_id == seg.segment_id and s.sensor_id in responsive_sensors]

            if source_sensor and dest_sensor:
                score += 0.40
                reasons.append(f"Segment connects responsive sensors {source_sensor[0].sensor_id} and {dest_sensor[0].sensor_id}")
            elif source_sensor or dest_sensor:
                matched_s = (source_sensor or dest_sensor)[0].sensor_id
                score += 0.20
                reasons.append(f"Segment is adjacent to responsive sensor {matched_s}")

            # Factor 2: Pressure drop at destination node + Flow increase upstream at source node
            has_dest_pressure_drop = dest_sensor and dest_sensor[0].sensor_id in pressure_drop_sensors
            has_direct_pressure_drop = direct_sensor and direct_sensor[0].sensor_id in pressure_drop_sensors
            has_source_flow_increase = source_sensor and source_sensor[0].sensor_id in flow_increase_sensors

            if (has_dest_pressure_drop or has_direct_pressure_drop) and has_source_flow_increase:
                score += 0.35
                reasons.append(f"Directional head loss pattern: upstream flow supply increase with downstream pressure drop on {seg.segment_id}")
            elif has_dest_pressure_drop or has_direct_pressure_drop:
                score += 0.20
                reasons.append(f"Pressure drop observed at downstream sensor node {seg.destination_node}")

            # Factor 3: Max anomaly score of adjacent sensors
            adj_scores = [a.anomaly_score for a in zone_results if a.sensor_id in [s.sensor_id for s in (source_sensor + dest_sensor + direct_sensor)]]
            if adj_scores:
                max_adj = max(adj_scores)
                score += 0.25 * max_adj

            norm_score = float(max(0.0, min(1.0, score)))
            candidate_scores[seg.segment_id] = (norm_score, reasons)

        # Sort candidate segments by score descending
        sorted_candidates = sorted(candidate_scores.items(), key=lambda item: item[1][0], reverse=True)

        if not sorted_candidates or sorted_candidates[0][1][0] < 0.30:
            return None

        selected_segment_id, (top_confidence, top_reasons) = sorted_candidates[0]

        candidate_list = [
            CandidateSegmentScore(
                segment_id=seg_id,
                confidence=round(score, 3),
                reason="; ".join(reasons) if reasons else "Topological proximity"
            )
            for seg_id, (score, reasons) in sorted_candidates[:3]  # Top 3 candidates
        ]

        evidence_notes = [
            f"Localized to segment {selected_segment_id} in {target_zone_id}",
            f"Responsive sensors involved: {', '.join(responsive_sensors)}",
        ] + top_reasons

        return {
            "selected_segment": selected_segment_id,
            "affected_zone": target_zone_id,
            "candidate_segments": candidate_list,
            "localization_confidence": round(top_confidence, 3),
            "responsive_sensors": responsive_sensors,
            "evidence": evidence_notes
        }
