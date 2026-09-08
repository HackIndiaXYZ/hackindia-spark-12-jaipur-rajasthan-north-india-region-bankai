import copy
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from app.models.network import WaterNetwork, Sensor, HealthStatus
from app.models.observability import (
    SegmentObservability,
    NetworkObservabilitySummary,
    VirtualSensorCandidate,
    BlindSpotLevel
)
from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.anomaly_detector import AnomalyDetector
from app.core.logging import logger


class ObservabilityService:
    """
    Simulated Network Observability & Sensor Planning Intelligence Service.
    Analyzes model-based detection response, identifies blind spots, and evaluates virtual sensor placement.
    """

    def __init__(
        self,
        network: Optional[WaterNetwork] = None,
        weight_detected: float = 0.30,
        weight_coverage: float = 0.30,
        weight_latency: float = 0.20,
        weight_signal: float = 0.20,
        max_latency_minutes: float = 60.0
    ):
        self.network = network or WaterNetwork.create_default_network()
        self.w_detected = weight_detected
        self.w_coverage = weight_coverage
        self.w_latency = weight_latency
        self.w_signal = weight_signal
        self.max_latency_minutes = max_latency_minutes

        # Local cache for expensive stress test analysis
        self._cache: Dict[str, NetworkObservabilitySummary] = {}

    def _generate_cache_key(self, net: WaterNetwork, scenario_duration: int) -> str:
        s_ids = sorted(list(net.sensors.keys()))
        seg_ids = sorted(list(net.segments.keys()))
        raw_key = f"{net.name}:{len(s_ids)}:{','.join(s_ids)}:{len(seg_ids)}:{scenario_duration}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def calculate_segment_score(
        self,
        detected: bool,
        detection_delay_minutes: float,
        responsive_sensor_count: int,
        total_zone_sensors: int,
        maximum_anomaly_score: float
    ) -> float:
        """
        Calculates explainable composite observability score between 0.0 and 1.0.
        """
        if not detected:
            return 0.0

        s_detected = 1.0 if detected else 0.0
        
        # Responsive sensor ratio relative to zone sensors
        responsive_ratio = responsive_sensor_count / max(1.0, float(total_zone_sensors))
        s_coverage = min(1.0, responsive_ratio)

        # Latency component (faster detection = higher score)
        delay = max(0.0, detection_delay_minutes)
        s_latency = max(0.0, 1.0 - (delay / self.max_latency_minutes))

        # Signal strength component
        s_signal = min(1.0, max(0.0, maximum_anomaly_score))

        composite_score = (
            self.w_detected * s_detected +
            self.w_coverage * s_coverage +
            self.w_latency * s_latency +
            self.w_signal * s_signal
        )
        return float(max(0.0, min(1.0, composite_score)))

    def classify_blind_spot(self, score: float, detected: bool) -> BlindSpotLevel:
        if not detected or score < 0.35:
            return BlindSpotLevel.CRITICAL_BLIND_SPOT
        elif score < 0.55:
            return BlindSpotLevel.LOW_OBSERVABILITY
        elif score < 0.75:
            return BlindSpotLevel.MEDIUM_OBSERVABILITY
        else:
            return BlindSpotLevel.HIGH_OBSERVABILITY

    def analyze_network_observability(
        self,
        duration_minutes: int = 60,
        leak_start_minute: int = 15,
        leak_severity: float = 0.6,
        seed: int = 42,
        use_cache: bool = True
    ) -> NetworkObservabilitySummary:
        """
        Performs location stress testing across all network pipeline segments and computes observability summary.
        """
        cache_key = self._generate_cache_key(self.network, duration_minutes)
        if use_cache and cache_key in self._cache:
            logger.info("Returning cached network observability summary.")
            return self._cache[cache_key]

        start_dt = datetime(2026, 9, 8, 8, 0, 0)
        simulator = SensorSimulator(network=self.network)
        detector = AnomalyDetector(network=self.network, use_isolation_forest=False)

        segment_results: List[SegmentObservability] = []

        for seg_id, seg in self.network.segments.items():
            config = SimulationConfig(
                start_time=start_dt,
                duration_minutes=duration_minutes,
                sampling_interval_seconds=60,
                seed=seed,
                scenario_type="gradual_leak",
                affected_zone_id=seg.zone_id,
                affected_segment_id=seg_id,
                leak_start_minute=leak_start_minute,
                leak_severity=leak_severity,
                missing_data_prob=0.0
            )

            readings = simulator.generate_readings(config)
            anomalies = detector.detect(readings)

            detected_anomalies = [a for a in anomalies if a.is_anomalous]
            is_detected = len(detected_anomalies) > 0

            max_score = max([a.anomaly_score for a in anomalies]) if anomalies else 0.0

            if is_detected:
                first_ts = min([a.timestamp for a in detected_anomalies])
                delay_min = (first_ts - start_dt).total_seconds() / 60.0
            else:
                delay_min = -1.0

            responsive_sensors = set([a.sensor_id for a in detected_anomalies])
            resp_cnt = len(responsive_sensors)

            total_zone_sensors = len(self.network.get_sensors_by_zone(seg.zone_id))
            resp_ratio = resp_cnt / max(1, total_zone_sensors)

            obs_score = self.calculate_segment_score(
                detected=is_detected,
                detection_delay_minutes=delay_min,
                responsive_sensor_count=resp_cnt,
                total_zone_sensors=total_zone_sensors,
                maximum_anomaly_score=max_score
            )

            blind_spot = self.classify_blind_spot(obs_score, is_detected)

            segment_results.append(SegmentObservability(
                segment_id=seg_id,
                zone_id=seg.zone_id,
                observability_score=obs_score,
                detected=is_detected,
                detection_delay_minutes=delay_min,
                responsive_sensor_count=resp_cnt,
                responsive_sensor_ratio=resp_ratio,
                blind_spot_level=blind_spot,
                maximum_anomaly_score=max_score
            ))

        # Overall summary aggregation
        overall_score = float(np.mean([s.observability_score for s in segment_results])) if segment_results else 0.0

        high_cnt = sum(1 for s in segment_results if s.blind_spot_level == BlindSpotLevel.HIGH_OBSERVABILITY)
        med_cnt = sum(1 for s in segment_results if s.blind_spot_level == BlindSpotLevel.MEDIUM_OBSERVABILITY)
        low_cnt = sum(1 for s in segment_results if s.blind_spot_level == BlindSpotLevel.LOW_OBSERVABILITY)
        blind_cnt = sum(1 for s in segment_results if s.blind_spot_level == BlindSpotLevel.CRITICAL_BLIND_SPOT)

        sorted_by_score = sorted(segment_results, key=lambda s: s.observability_score)
        weakest_seg = sorted_by_score[0].segment_id if sorted_by_score else "N/A"
        strongest_seg = sorted_by_score[-1].segment_id if sorted_by_score else "N/A"

        summary = NetworkObservabilitySummary(
            overall_observability=overall_score,
            total_segments=len(segment_results),
            high_observability_segments=high_cnt,
            medium_observability_segments=med_cnt,
            low_observability_segments=low_cnt,
            blind_spots=blind_cnt,
            weakest_segment=weakest_seg,
            strongest_segment=strongest_seg,
            segment_details=segment_results
        )

        if use_cache:
            self._cache[cache_key] = summary

        return summary

    def generate_candidate_locations(self) -> List[Tuple[str, str, str]]:
        """
        Generates candidate virtual sensor nodes across pipeline network junction/endpoint nodes.
        Returns list of tuples: (node_id, segment_id, zone_id)
        """
        candidates = []
        for seg_id, seg in self.network.segments.items():
            # Candidate at destination node
            if "Reservoir" not in seg.destination_node:
                candidates.append((seg.destination_node, seg_id, seg.zone_id))
            # Candidate at source node if non-reservoir
            if "Reservoir" not in seg.source_node:
                candidates.append((seg.source_node, seg_id, seg.zone_id))

        return list(set(candidates))

    def evaluate_virtual_sensor_candidates(self) -> List[VirtualSensorCandidate]:
        """
        Evaluates virtual sensor candidates by testing simulated observability improvements.
        Ranks candidates deterministically.
        """
        baseline_summary = self.analyze_network_observability(use_cache=True)
        baseline_map = {s.segment_id: s for s in baseline_summary.segment_details}

        candidates_def = self.generate_candidate_locations()
        ranked_candidates: List[VirtualSensorCandidate] = []

        for candidate_node, seg_id, zone_id in candidates_def:
            base_seg_info = baseline_map.get(seg_id)
            if not base_seg_info:
                continue

            # Clone network and add virtual sensor
            mod_net = WaterNetwork.create_default_network()
            virtual_sensor_id = f"V_{candidate_node}"
            mod_net.add_sensor(Sensor(
                sensor_id=virtual_sensor_id,
                zone_id=zone_id,
                pipeline_segment_id=seg_id,
                location_node=candidate_node,
                sensor_type="multi-sensor",
                installation_metadata={"virtual": True}
            ))

            # Run observability analysis on modified network
            mod_service = ObservabilityService(network=mod_net)
            mod_summary = mod_service.analyze_network_observability(use_cache=False)
            mod_map = {s.segment_id: s for s in mod_summary.segment_details}

            mod_seg_info = mod_map[seg_id]

            obs_before = base_seg_info.observability_score
            obs_after = mod_seg_info.observability_score
            impr_pct = ((obs_after - obs_before) / max(0.01, obs_before)) * 100.0

            resp_before = base_seg_info.responsive_sensor_count
            resp_after = mod_seg_info.responsive_sensor_count

            # Value score calculation (explainable deterministic formula)
            # Higher score if segment was previously weak/blind spot and receives large boost
            blind_boost = 0.30 if base_seg_info.blind_spot_level in [BlindSpotLevel.LOW_OBSERVABILITY, BlindSpotLevel.CRITICAL_BLIND_SPOT] else 0.10
            value_score = float(max(0.0, min(1.0, 0.50 * obs_after + 0.20 * (impr_pct / 100.0) + blind_boost)))

            # Reasoning notes
            reasoning = []
            if base_seg_info.blind_spot_level in [BlindSpotLevel.LOW_OBSERVABILITY, BlindSpotLevel.CRITICAL_BLIND_SPOT]:
                reasoning.append(f"Monitors weak region {seg_id} previously classified as {base_seg_info.blind_spot_level.value}")
            if resp_after > resp_before:
                reasoning.append(f"Increases simulated responsive-sensor count from {resp_before} to {resp_after}")
            if mod_seg_info.detection_delay_minutes < base_seg_info.detection_delay_minutes and mod_seg_info.detection_delay_minutes > 0:
                reasoning.append(f"Reduces simulated detection delay by {base_seg_info.detection_delay_minutes - mod_seg_info.detection_delay_minutes:.1f} minutes")
            if not reasoning:
                reasoning.append("Provides sensor redundancy for neighboring pipeline nodes")

            ranked_candidates.append(VirtualSensorCandidate(
                candidate_node=candidate_node,
                target_segment_id=seg_id,
                target_zone_id=zone_id,
                value_score=value_score,
                baseline_observability=obs_before,
                new_observability=obs_after,
                observability_improvement_percent=impr_pct,
                responsive_sensor_count_before=resp_before,
                responsive_sensor_count_after=resp_after,
                reasoning=reasoning
            ))

        # Sort candidates by value_score descending
        ranked_candidates.sort(key=lambda c: c.value_score, reverse=True)
        return ranked_candidates
