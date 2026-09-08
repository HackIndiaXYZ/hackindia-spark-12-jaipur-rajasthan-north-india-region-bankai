import os
import sys
import json
import pandas as pd
from datetime import datetime

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.network import WaterNetwork
from app.services.observability import ObservabilityService


def run_observability_evaluation():
    exp_dir = os.path.dirname(__file__)
    os.makedirs(exp_dir, exist_ok=True)

    service = ObservabilityService()
    summary = service.analyze_network_observability()

    rows = []
    for s in summary.segment_details:
        rows.append({
            "segment_id": s.segment_id,
            "zone_id": s.zone_id,
            "observability_score": s.observability_score,
            "observability_class": s.blind_spot_level.value,
            "detected": s.detected,
            "detection_delay_minutes": s.detection_delay_minutes,
            "responsive_sensor_count": s.responsive_sensor_count,
            "responsive_sensor_ratio": s.responsive_sensor_ratio,
            "maximum_anomaly_score": s.maximum_anomaly_score
        })

    df = pd.DataFrame(rows)
    csv_path = os.path.join(exp_dir, "observability_evaluation.csv")
    df.to_csv(csv_path, index=False)

    candidates = service.evaluate_virtual_sensor_candidates()

    print("=========================================================================")
    print("       AQUASENTINEL NETWORK OBSERVABILITY EVALUATION REPORT             ")
    print("=========================================================================\n")
    print(f"Overall Network Observability: {summary.overall_observability:.3f}")
    print(f"High Observability Segments:   {summary.high_observability_segments}")
    print(f"Medium Observability Segments: {summary.medium_observability_segments}")
    print(f"Low Observability Segments:    {summary.low_observability_segments}")
    print(f"Critical Blind Spots:          {summary.blind_spots}")
    print(f"Weakest Segment:              {summary.weakest_segment}")
    print(f"Strongest Segment:            {summary.strongest_segment}\n")

    print("--- SEGMENT OBSERVABILITY DETAILS ---")
    print(df.to_string(index=False))
    print("\n" + "-" * 73 + "\n")

    print("--- RANKED VIRTUAL SENSOR CANDIDATES ---")
    cand_rows = []
    for c in candidates:
        cand_rows.append({
            "candidate_node": c.candidate_node,
            "target_segment": c.target_segment_id,
            "value_score": c.value_score,
            "baseline_obs": c.baseline_observability,
            "new_obs": c.new_observability,
            "improvement_pct": f"{c.observability_improvement_percent:+.1f}%",
            "resp_sensors_before_after": f"{c.responsive_sensor_count_before} -> {c.responsive_sensor_count_after}"
        })
    df_cand = pd.DataFrame(cand_rows)
    print(df_cand.to_string(index=False))
    print("=========================================================================\n")


if __name__ == "__main__":
    run_observability_evaluation()
