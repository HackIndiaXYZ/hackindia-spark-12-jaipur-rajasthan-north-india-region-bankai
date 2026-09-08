from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np

from app.models.reading import SensorReading
from app.models.anomaly import AnomalyResult
from app.models.network import WaterNetwork
from app.services.simulator import SensorSimulator
from app.core.logging import logger


class WaterLossEstimator:
    """
    Model-derived Water Loss Estimator for AquaSentinel pipeline monitoring.
    Calculates estimated instantaneous flow loss (LPM) and accumulated volume loss (Liters).
    """

    DISCLAIMER = "Loss values are model-derived simulation estimates intended for demonstration and system evaluation."

    def __init__(self, network: Optional[WaterNetwork] = None):
        self.network = network or WaterNetwork.create_default_network()

    def estimate_loss(
        self,
        readings: List[SensorReading],
        anomaly_results: List[AnomalyResult],
        affected_segment_id: str
    ) -> Dict[str, Any]:
        """
        Estimates flow loss (LPM) and volume loss (Liters) based on observed telemetry deviations.
        Guaranteed to handle zero-duration, negative differences, or missing values safely.
        """
        if not readings or not anomaly_results:
            return {
                "estimated_flow_loss_lpm": 0.0,
                "estimated_volume_loss_liters": 0.0,
                "duration_minutes": 0.0,
                "disclaimer": self.DISCLAIMER
            }

        segment = self.network.segments.get(affected_segment_id)
        nominal_avg_flow = (segment.nominal_min_flow + segment.nominal_max_flow) / 2.0 if segment else 100.0

        # Filter anomalous readings for the affected segment or adjacent sensors
        anomalous_ts = [a.timestamp for a in anomaly_results if a.is_anomalous]
        
        if not anomalous_ts:
            return {
                "estimated_flow_loss_lpm": 0.0,
                "estimated_volume_loss_liters": 0.0,
                "duration_minutes": 0.0,
                "disclaimer": self.DISCLAIMER
            }

        # Determine anomaly duration in minutes
        min_ts = min(anomalous_ts)
        max_ts = max(anomalous_ts)
        duration_sec = (max_ts - min_ts).total_seconds()
        duration_minutes = max(1.0, duration_sec / 60.0) if duration_sec > 0 else 1.0

        # Compute flow rate deviations during anomalous period
        flow_deviations: List[float] = []

        for r in readings:
            if r.timestamp in anomalous_ts and (r.pipeline_segment_id == affected_segment_id or r.sensor_id in affected_segment_id):
                demand_mult = SensorSimulator.get_demand_multiplier(r.timestamp)
                expected_flow = nominal_avg_flow * demand_mult
                
                # Flow loss estimate: excess flow supplied upstream or pressure drop loss equivalence
                flow_diff = r.flow_rate - expected_flow
                if flow_diff > 0:
                    flow_deviations.append(flow_diff)
                else:
                    # Alternative loss heuristic based on pressure drop head loss
                    expected_p = 4.0
                    p_drop = max(0.0, expected_p - r.pressure)
                    estimated_lpm_from_p = p_drop * 25.0  # Heuristic 25 LPM per Bar drop
                    flow_deviations.append(estimated_lpm_from_p)

        avg_flow_loss_lpm = float(np.mean(flow_deviations)) if flow_deviations else 0.0
        avg_flow_loss_lpm = max(0.0, avg_flow_loss_lpm)

        accumulated_volume_liters = max(0.0, avg_flow_loss_lpm * duration_minutes)

        return {
            "estimated_flow_loss_lpm": round(avg_flow_loss_lpm, 2),
            "estimated_volume_loss_liters": round(accumulated_volume_liters, 2),
            "duration_minutes": round(duration_minutes, 1),
            "disclaimer": self.DISCLAIMER
        }
