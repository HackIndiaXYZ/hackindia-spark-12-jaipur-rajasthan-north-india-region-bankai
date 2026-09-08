import math
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest

from app.models.reading import SensorReading
from app.models.anomaly import AnomalyResult
from app.models.network import WaterNetwork
from app.services.simulator import SensorSimulator
from app.core.logging import logger


class AnomalyDetector:
    """
    Statistical and Machine Learning Anomaly Detection Engine for AquaSentinel water networks.
    Combines rolling Z-score statistics, rate-of-change metrics, topology neighbor disagreement,
    and optional Isolation Forest model outputs to produce explainable normalized anomaly scores.
    """

    def __init__(
        self,
        network: Optional[WaterNetwork] = None,
        anomaly_threshold: float = 0.55,
        persistence_window: int = 3,
        use_isolation_forest: bool = True
    ):
        self.network = network or WaterNetwork.create_default_network()
        self.anomaly_threshold = anomaly_threshold
        self.persistence_window = persistence_window
        self.use_isolation_forest = use_isolation_forest
        self.isolation_forest_model: Optional[IsolationForest] = None
        self._is_iforest_trained = False

        # State tracking per sensor for rolling stats and persistence
        self._previous_readings: Dict[str, SensorReading] = {}
        self._persistence_counts: Dict[str, int] = {}

    def _train_isolation_forest_baseline(self, readings: List[SensorReading]) -> None:
        """
        Trains IsolationForest on normal baseline telemetry features.
        """
        features = []
        for r in readings:
            if r.sensor_health == "HEALTHY":
                features.append([r.pressure, r.flow_rate, r.temperature])

        if len(features) >= 20:
            X = np.array(features)
            self.isolation_forest_model = IsolationForest(
                n_estimators=50,
                contamination=0.05,
                random_state=42
            )
            self.isolation_forest_model.fit(X)
            self._is_iforest_trained = True

    def detect(self, readings: List[SensorReading]) -> List[AnomalyResult]:
        """
        Processes a time series of sensor readings and returns AnomalyResults.
        """
        if not readings:
            return []

        # Train Isolation Forest on initial readings if not trained
        if self.use_isolation_forest and not self._is_iforest_trained:
            self._train_isolation_forest_baseline(readings)

        # Sort readings chronologically
        sorted_readings = sorted(readings, key=lambda r: r.timestamp)
        results: List[AnomalyResult] = []

        # Group readings by timestamp to perform neighbor comparisons across the network
        time_groups: Dict[datetime, Dict[str, SensorReading]] = {}
        for r in sorted_readings:
            time_groups.setdefault(r.timestamp, {})[r.sensor_id] = r

        for ts, sensor_map in time_groups.items():
            # First pass: compute individual sensor Z-scores at this timestamp
            sensor_zscores: Dict[str, Dict[str, float]] = {}

            for s_id, reading in sensor_map.items():
                sensor_model = self.network.sensors.get(s_id)
                segment = self.network.segments.get(sensor_model.pipeline_segment_id) if sensor_model and sensor_model.pipeline_segment_id else None
                
                # Nominal baseline ranges
                if segment:
                    expected_p_base = (segment.nominal_min_pressure + segment.nominal_max_pressure) / 2.0
                    expected_f_base = (segment.nominal_min_flow + segment.nominal_max_flow) / 2.0
                else:
                    expected_p_base = 4.0
                    expected_f_base = 100.0

                # Adjust expected baseline by diurnal time-of-day demand multiplier
                demand_mult = SensorSimulator.get_demand_multiplier(ts)
                expected_flow = expected_f_base * demand_mult
                expected_pressure = expected_p_base - (demand_mult - 1.0) * 0.4

                # Standard deviations (nominal 5% noise)
                p_std = max(0.1, expected_pressure * 0.05)
                f_std = max(2.0, expected_flow * 0.05)

                p_zscore = abs(reading.pressure - expected_pressure) / p_std
                f_zscore = abs(reading.flow_rate - expected_flow) / f_std
                
                sensor_zscores[s_id] = {
                    "p_zscore": p_zscore,
                    "f_zscore": f_zscore,
                    "max_z": max(p_zscore, f_zscore),
                    "expected_p": expected_pressure,
                    "expected_f": expected_flow
                }

            # Second pass: compute neighbor deviations and generate AnomalyResults
            for s_id, reading in sensor_map.items():
                z_info = sensor_zscores[s_id]
                p_z = z_info["p_zscore"]
                f_z = z_info["f_zscore"]
                
                # Rate of Change calculation
                p_roc = 0.0
                f_roc = 0.0
                prev_r = self._previous_readings.get(s_id)
                if prev_r:
                    time_delta_sec = (reading.timestamp - prev_r.timestamp).total_seconds()
                    if time_delta_sec > 0:
                        p_roc = abs(reading.pressure - prev_r.pressure) / (time_delta_sec / 60.0)
                        f_roc = abs(reading.flow_rate - prev_r.flow_rate) / (time_delta_sec / 60.0)

                self._previous_readings[s_id] = reading

                # Neighbor disagreement calculation using NetworkX graph
                neighbor_z_diff = 0.0
                neighbor_count = 0
                sensor_obj = self.network.sensors.get(s_id)
                if sensor_obj:
                    # Find graph neighbors of sensor's node location
                    loc_node = sensor_obj.location_node
                    if self.network.graph.has_node(loc_node):
                        neighbors_nodes = list(self.network.graph.neighbors(loc_node))
                        neighbor_sensors = [s for s in self.network.sensors.values() if s.location_node in neighbors_nodes and s.sensor_id != s_id]
                        
                        if neighbor_sensors:
                            neighbor_z_vals = [sensor_zscores[ns.sensor_id]["max_z"] for ns in neighbor_sensors if ns.sensor_id in sensor_zscores]
                            if neighbor_z_vals:
                                avg_neighbor_z = float(np.mean(neighbor_z_vals))
                                neighbor_z_diff = abs(z_info["max_z"] - avg_neighbor_z)

                # Persistence count tracking
                is_currently_elevated = (z_info["max_z"] >= 2.0 or reading.sensor_health == "FAULTY")
                if is_currently_elevated:
                    self._persistence_counts[s_id] = self._persistence_counts.get(s_id, 0) + 1
                else:
                    self._persistence_counts[s_id] = 0

                persistence_cnt = self._persistence_counts[s_id]

                # Isolation Forest score
                iforest_score = 0.0
                if self.use_isolation_forest and self.isolation_forest_model:
                    try:
                        raw_score = self.isolation_forest_model.score_samples([[reading.pressure, reading.flow_rate, reading.temperature]])[0]
                        # Score samples returns negative anomaly score (more negative = more anomalous)
                        iforest_score = max(0.0, min(1.0, -raw_score * 2.0))
                    except Exception:
                        iforest_score = 0.0

                # --- EXPLAINABLE ANOMALY SCORE FUSION ---
                # Normalized statistical score from z-score
                stat_score = min(1.0, z_info["max_z"] / 4.0)
                persistence_factor = min(1.0, persistence_cnt / float(self.persistence_window))
                roc_score = min(1.0, (p_roc / 0.5 + f_roc / 20.0) / 2.0)
                
                # Multivariate signal boost if both pressure and flow z-scores are elevated (>= 2.0)
                multivariate_boost = 0.20 if (p_z >= 2.0 and f_z >= 2.0) else 0.0

                # Combined score
                composite_score = (
                    0.45 * stat_score +
                    0.20 * iforest_score +
                    0.15 * persistence_factor +
                    0.10 * min(1.0, neighbor_z_diff / 3.0) +
                    multivariate_boost
                )

                # Override for faulty sensor health
                if reading.sensor_health == "FAULTY":
                    composite_score = max(composite_score, 0.85)

                anomaly_score = max(0.0, min(1.0, composite_score))
                is_anomalous = anomaly_score >= self.anomaly_threshold

                # Build Evidence and Anomaly Types
                anomaly_types = []
                evidence = []

                if p_z >= 2.0:
                    anomaly_types.append("PRESSURE_ANOMALY")
                    diff_pct = ((reading.pressure - z_info["expected_p"]) / z_info["expected_p"]) * 100.0
                    evidence.append(f"Pressure deviation of {diff_pct:+.1f}% from expected baseline (Z={p_z:.1f})")

                if f_z >= 2.0:
                    anomaly_types.append("FLOW_ANOMALY")
                    diff_pct = ((reading.flow_rate - z_info["expected_f"]) / z_info["expected_f"]) * 100.0
                    evidence.append(f"Flow rate deviation of {diff_pct:+.1f}% from expected baseline (Z={f_z:.1f})")

                if p_roc > 0.3 or f_roc > 15.0:
                    anomaly_types.append("RATE_OF_CHANGE_ANOMALY")
                    evidence.append(f"Rapid telemetry rate of change detected (p_roc={p_roc:.2f} bar/min, f_roc={f_roc:.1f} lpm/min)")

                if p_z >= 2.0 and f_z >= 2.0:
                    anomaly_types.append("MULTIVARIATE_ANOMALY")
                    evidence.append("Multivariate anomaly: simultaneous pressure and flow deviations observed")

                if persistence_cnt >= self.persistence_window:
                    anomaly_types.append("PERSISTENT_ANOMALY")
                    evidence.append(f"Persistent anomaly sustained for {persistence_cnt} consecutive time steps")

                if neighbor_z_diff >= 2.0:
                    anomaly_types.append("SENSOR_ISOLATION_ANOMALY")
                    evidence.append(f"Sensor readings disagree significantly with graph neighbor sensors (diff={neighbor_z_diff:.1f})")

                data_quality = "GOOD"
                if reading.sensor_health == "FAULTY":
                    data_quality = "FAULTY_SENSOR"
                    evidence.append("Sensor self-reported FAULTY health status")

                result = AnomalyResult(
                    sensor_id=s_id,
                    timestamp=ts,
                    zone_id=reading.zone_id,
                    pipeline_segment_id=reading.pipeline_segment_id,
                    anomaly_score=anomaly_score,
                    is_anomalous=is_anomalous,
                    anomaly_types=anomaly_types,
                    signals={
                        "pressure_zscore": p_z,
                        "flow_zscore": f_z,
                        "pressure_roc": p_roc,
                        "flow_roc": f_roc,
                        "stat_score": stat_score,
                        "iforest_score": iforest_score
                    },
                    evidence=evidence,
                    persistence_count=persistence_cnt,
                    neighbor_deviation=neighbor_z_diff,
                    data_quality=data_quality
                )
                results.append(result)

        return results
