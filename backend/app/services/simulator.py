from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math
import random
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from app.models.reading import SensorReading
from app.models.network import WaterNetwork, PipelineSegment
from app.models.sensor import Sensor, HealthStatus
from app.core.logging import logger


@dataclass
class SimulationConfig:
    start_time: datetime = field(default_factory=lambda: datetime(2026, 9, 8, 8, 0, 0))
    duration_minutes: int = 60
    sampling_interval_seconds: int = 60
    seed: int = 42
    scenario_type: str = "normal"  # normal, gradual_leak, sudden_burst, sensor_fault, multiple_anomalies
    affected_zone_id: str = "Zone_B"
    affected_segment_id: str = "B2-B3"
    affected_sensor_id: str = "B3"
    leak_start_minute: int = 15
    leak_severity: float = 0.6  # 0.0 to 1.0
    fault_type: str = "spike"   # stuck, spike, drop, high_noise, missing
    noise_level: float = 0.02
    drift_rate: float = 0.0001  # drift per minute
    missing_data_prob: float = 0.01


class SensorSimulator:
    """
    Synthetic IoT sensor simulator for water pipeline networks.
    Generates realistic, deterministic telemetry under normal and anomalous scenarios.
    """

    def __init__(self, network: Optional[WaterNetwork] = None):
        self.network = network or WaterNetwork.create_default_network()

    @staticmethod
    def get_demand_multiplier(dt: datetime) -> float:
        """
        Diurnal time-of-day water demand curve.
        Returns a multiplier relative to nominal demand (1.0 average).
        """
        hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        # Combination of sines representing morning (8am) and evening (7pm) peaks
        morning_peak = math.exp(-((hour - 8.0) ** 2) / 8.0) * 0.4
        evening_peak = math.exp(-((hour - 19.0) ** 2) / 6.0) * 0.3
        night_trough = math.exp(-((hour - 3.0) ** 2) / 10.0) * 0.4
        
        base_demand = 0.9 + morning_peak + evening_peak - night_trough
        return max(0.4, min(1.6, base_demand))

    def _get_downstream_distance(self, source_segment_id: str, target_node: str) -> Optional[int]:
        """
        Calculates graph distance (number of hops) from source segment's destination node to target node.
        """
        source_seg = self.network.segments.get(source_segment_id)
        if not source_seg:
            return None
        
        if source_seg.destination_node == target_node or source_seg.source_node == target_node:
            return 0

        try:
            undirected_g = self.network.graph.to_undirected()
            path_len = len(nx.shortest_path(undirected_g, source=source_seg.destination_node, target=target_node)) - 1
            return path_len
        except Exception:
            return None

    def generate_readings(self, config: SimulationConfig) -> List[SensorReading]:
        """
        Generates deterministic time series readings based on configuration.
        """
        rng = np.random.RandomState(config.seed)
        py_rng = random.Random(config.seed)

        readings: List[SensorReading] = []
        total_steps = int((config.duration_minutes * 60) / config.sampling_interval_seconds)

        # Baseline offsets per sensor for realistic variance
        sensor_baselines: Dict[str, Dict[str, float]] = {}
        for s_id, sensor in self.network.sensors.items():
            segment = self.network.segments.get(sensor.pipeline_segment_id) if sensor.pipeline_segment_id else None
            if segment:
                avg_pressure = (segment.nominal_min_pressure + segment.nominal_max_pressure) / 2.0
                avg_flow = (segment.nominal_min_flow + segment.nominal_max_flow) / 2.0
            else:
                avg_pressure = 4.0
                avg_flow = 100.0

            # Add sensor specific baseline noise (+/- 5%)
            sensor_baselines[s_id] = {
                "pressure_base": avg_pressure * (1.0 + rng.uniform(-0.05, 0.05)),
                "flow_base": avg_flow * (1.0 + rng.uniform(-0.05, 0.05)),
                "drift_offset_p": 0.0,
                "drift_offset_f": 0.0,
                "stuck_p": None,
                "stuck_f": None
            }

        # Check affected segment nodes for topology propagation
        affected_seg = self.network.segments.get(config.affected_segment_id)
        affected_nodes = [affected_seg.source_node, affected_seg.destination_node] if affected_seg else []

        for step in range(total_steps):
            elapsed_minutes = (step * config.sampling_interval_seconds) / 60.0
            current_time = config.start_time + timedelta(seconds=step * config.sampling_interval_seconds)
            demand_mult = self.get_demand_multiplier(current_time)

            for s_id, sensor in self.network.sensors.items():
                # 1. Missing reading check
                if rng.uniform(0, 1) < config.missing_data_prob:
                    continue

                baseline = sensor_baselines[s_id]
                
                # Apply gradual drift over time
                baseline["drift_offset_p"] += config.drift_rate * rng.normal(0.5, 0.2)
                baseline["drift_offset_f"] += config.drift_rate * rng.normal(0.5, 0.2)

                # Base pressure & flow under normal demand
                # High demand -> lower pressure (friction loss)
                nominal_flow = baseline["flow_base"] * demand_mult
                pressure_drop_from_demand = (demand_mult - 1.0) * 0.4
                nominal_pressure = baseline["pressure_base"] - pressure_drop_from_demand

                # Add normal Gaussian measurement noise
                p_noise = rng.normal(0, nominal_pressure * config.noise_level)
                f_noise = rng.normal(0, nominal_flow * config.noise_level)

                curr_pressure = nominal_pressure + baseline["drift_offset_p"] + p_noise
                curr_flow = nominal_flow + baseline["drift_offset_f"] + f_noise
                curr_temp = 18.0 + 3.0 * math.sin((current_time.hour - 6) * math.pi / 12) + rng.normal(0, 0.1)
                sensor_health = sensor.health_status.value if hasattr(sensor.health_status, 'value') else str(sensor.health_status)

                # 2. Scenario Alterations
                is_after_leak_start = elapsed_minutes >= config.leak_start_minute

                # Determine scenario type
                effective_scenario = config.scenario_type

                # --- LEAK SCENARIOS (Gradual Leak / Sudden Burst) ---
                if (effective_scenario in ["gradual_leak", "sudden_burst", "multiple_anomalies"]) and is_after_leak_start:
                    is_in_affected_zone = (sensor.zone_id == config.affected_zone_id)
                    
                    if is_in_affected_zone:
                        # Calculate effective leak magnitude (0.0 to config.leak_severity)
                        if effective_scenario == "sudden_burst":
                            leak_mag = config.leak_severity
                        else:  # gradual leak
                            ramp_progress = min(1.0, (elapsed_minutes - config.leak_start_minute) / max(1.0, (config.duration_minutes - config.leak_start_minute)))
                            leak_mag = config.leak_severity * ramp_progress

                        # Check proximity / topology relationship to affected segment
                        is_direct_segment_sensor = (sensor.pipeline_segment_id == config.affected_segment_id or sensor.location_node in affected_nodes)

                        if is_direct_segment_sensor:
                            # Direct leak location: severe pressure drop & increased upstream/burst flow
                            curr_pressure *= (1.0 - 0.45 * leak_mag)
                            curr_flow *= (1.0 + 0.35 * leak_mag)
                        else:
                            # Neighboring / downstream sensors in same zone experience attenuated drop
                            curr_pressure *= (1.0 - 0.20 * leak_mag)
                            curr_flow *= (1.0 - 0.15 * leak_mag)  # downstream flow decreases due to lost volume

                # --- SENSOR FAULT SCENARIO ---
                is_fault_target = (s_id == config.affected_sensor_id)
                if (effective_scenario in ["sensor_fault", "multiple_anomalies"]) and is_fault_target and is_after_leak_start:
                    sensor_health = "FAULTY"
                    if config.fault_type == "stuck":
                        if baseline["stuck_p"] is None:
                            baseline["stuck_p"] = curr_pressure
                            baseline["stuck_f"] = curr_flow
                        curr_pressure = baseline["stuck_p"]
                        curr_flow = baseline["stuck_f"]
                    elif config.fault_type == "spike":
                        curr_pressure *= rng.uniform(2.0, 3.5)
                        curr_flow *= rng.uniform(2.5, 4.0)
                    elif config.fault_type == "drop":
                        curr_pressure *= 0.15
                        curr_flow *= 0.20
                    elif config.fault_type == "high_noise":
                        curr_pressure += rng.normal(0, 1.5)
                        curr_flow += rng.normal(0, 45.0)

                # Ensure non-negative readings
                curr_pressure = max(0.01, curr_pressure)
                curr_flow = max(0.0, curr_flow)

                reading = SensorReading(
                    timestamp=current_time,
                    sensor_id=s_id,
                    zone_id=sensor.zone_id,
                    pipeline_segment_id=sensor.pipeline_segment_id,
                    pressure=curr_pressure,
                    flow_rate=curr_flow,
                    temperature=curr_temp,
                    sensor_health=sensor_health
                )
                readings.append(reading)

        return readings

    @staticmethod
    def to_pandas_dataframe(readings: List[SensorReading]) -> pd.DataFrame:
        """Converts sensor readings list to pandas DataFrame."""
        return pd.DataFrame([r.to_dict() for r in readings])

    @staticmethod
    def to_csv_string(readings: List[SensorReading]) -> str:
        """Converts sensor readings list to CSV formatted string."""
        df = SensorSimulator.to_pandas_dataframe(readings)
        return df.to_csv(index=False)

    @staticmethod
    def to_json_string(readings: List[SensorReading]) -> str:
        """Converts sensor readings list to JSON formatted string."""
        df = SensorSimulator.to_pandas_dataframe(readings)
        return df.to_json(orient="records", date_format="iso")

    @staticmethod
    def export_to_csv(readings: List[SensorReading], filepath: str) -> None:
        """Saves sensor readings to a CSV file."""
        df = SensorSimulator.to_pandas_dataframe(readings)
        df.to_csv(filepath, index=False)
