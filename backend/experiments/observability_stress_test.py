import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Any

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.network import WaterNetwork, Sensor
from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.anomaly_detector import AnomalyDetector
from app.models.reading import SensorReading


def run_experiment_1(network: WaterNetwork) -> pd.DataFrame:
    """
    Experiment 1: Location Stress Test across all pipeline segments in the network.
    Injects identical gradual-leak scenarios into each segment.
    """
    simulator = SensorSimulator(network=network)
    detector = AnomalyDetector(network=network, use_isolation_forest=False)
    start_dt = datetime(2026, 9, 8, 8, 0, 0)
    
    results = []
    
    for seg_id, seg in network.segments.items():
        config = SimulationConfig(
            start_time=start_dt,
            duration_minutes=60,
            sampling_interval_seconds=60,
            seed=42,
            scenario_type="gradual_leak",
            affected_zone_id=seg.zone_id,
            affected_segment_id=seg_id,
            leak_start_minute=15,
            leak_severity=0.6,
            missing_data_prob=0.0
        )
        
        readings = simulator.generate_readings(config)
        anomalies = detector.detect(readings)
        
        # Calculate stress test metrics
        detected_anomalies = [a for a in anomalies if a.is_anomalous] # anomaly_score >= 0.55
        is_detected = len(detected_anomalies) > 0
        
        max_score = max([a.anomaly_score for a in anomalies]) if anomalies else 0.0
        
        if is_detected:
            first_anomaly_ts = min([a.timestamp for a in detected_anomalies])
            time_to_first_strong_min = (first_anomaly_ts - start_dt).total_seconds() / 60.0
        else:
            time_to_first_strong_min = float('inf')
            
        responsive_sensors = sorted(list(set([a.sensor_id for a in detected_anomalies])))
        responsive_sensor_count = len(responsive_sensors)
        
        results.append({
            "segment_id": seg_id,
            "zone_id": seg.zone_id,
            "detected": bool(is_detected),
            "time_to_first_strong_anomaly_minutes": float(time_to_first_strong_min if is_detected else -1.0),
            "maximum_anomaly_score": float(round(max_score, 3)),
            "responsive_sensor_count": int(responsive_sensor_count),
            "responsive_sensor_ids": ",".join(responsive_sensors)
        })
        
    return pd.DataFrame(results)


def run_experiment_2(network: WaterNetwork, exp1_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Experiment 2: Reproducibility across multiple seeds for top and bottom segments.
    """
    seeds = [42, 100, 999]
    sorted_df = exp1_df.sort_values(by="maximum_anomaly_score", ascending=False)
    
    strongest_segs = sorted_df.head(5)["segment_id"].tolist()
    weakest_segs = sorted_df.tail(5)["segment_id"].tolist()
    test_segs = list(set(strongest_segs + weakest_segs))
    
    reproducibility_results = []
    
    for seg_id in test_segs:
        seg = network.segments[seg_id]
        seed_metrics = []
        
        for seed in seeds:
            config = SimulationConfig(
                start_time=datetime(2026, 9, 8, 8, 0, 0),
                duration_minutes=60,
                seed=seed,
                scenario_type="gradual_leak",
                affected_zone_id=seg.zone_id,
                affected_segment_id=seg_id,
                leak_start_minute=15,
                leak_severity=0.6,
                missing_data_prob=0.0
            )
            sim = SensorSimulator(network=network)
            det = AnomalyDetector(network=network, use_isolation_forest=False)
            readings = sim.generate_readings(config)
            anomalies = det.detect(readings)
            
            detected = [a for a in anomalies if a.is_anomalous]
            max_s = max([a.anomaly_score for a in anomalies]) if anomalies else 0.0
            resp_cnt = len(set([a.sensor_id for a in detected]))
            
            seed_metrics.append({
                "seed": int(seed),
                "max_score": float(round(max_s, 3)),
                "responsive_count": int(resp_cnt)
            })
            
        reproducibility_results.append({
            "segment_id": str(seg_id),
            "seed_metrics": seed_metrics
        })
        
    return {"reproducibility": reproducibility_results}


def run_experiment_3(network: WaterNetwork, weakest_segment_id: str) -> Dict[str, Any]:
    """
    Experiment 3: Virtual Sensor Placement on the weakest region to test observability improvement.
    """
    weak_seg = network.segments[weakest_segment_id]
    virtual_sensor_id = f"V_{weak_seg.destination_node}"
    
    modified_network = WaterNetwork.create_default_network()
    modified_network.add_sensor(Sensor(
        sensor_id=virtual_sensor_id,
        zone_id=weak_seg.zone_id,
        pipeline_segment_id=weakest_segment_id,
        location_node=weak_seg.destination_node,
        sensor_type="multi-sensor",
        installation_metadata={"virtual": True}
    ))
    
    # Baseline run (before virtual sensor)
    sim_base = SensorSimulator(network=network)
    det_base = AnomalyDetector(network=network, use_isolation_forest=False)
    config = SimulationConfig(
        scenario_type="gradual_leak",
        affected_zone_id=weak_seg.zone_id,
        affected_segment_id=weakest_segment_id,
        leak_start_minute=15,
        leak_severity=0.6,
        seed=42,
        missing_data_prob=0.0
    )
    r_base = sim_base.generate_readings(config)
    a_base = det_base.detect(r_base)
    max_score_before = max([a.anomaly_score for a in a_base]) if a_base else 0.0
    resp_cnt_before = len(set([a.sensor_id for a in a_base if a.is_anomalous]))
    
    # Virtual sensor run
    sim_v = SensorSimulator(network=modified_network)
    det_v = AnomalyDetector(network=modified_network, use_isolation_forest=False)
    r_v = sim_v.generate_readings(config)
    a_v = det_v.detect(r_v)
    max_score_after = max([a.anomaly_score for a in a_v]) if a_v else 0.0
    resp_cnt_after = len(set([a.sensor_id for a in a_v if a.is_anomalous]))
    
    score_impr_pct = ((max_score_after - max_score_before) / max(0.01, max_score_before)) * 100.0
    
    return {
        "candidate_location": str(weak_seg.destination_node),
        "segment_id": str(weakest_segment_id),
        "max_score_before": float(round(max_score_before, 3)),
        "max_score_after": float(round(max_score_after, 3)),
        "responsive_count_before": int(resp_cnt_before),
        "responsive_count_after": int(resp_cnt_after),
        "score_improvement_percent": float(round(score_impr_pct, 1)),
        "sensor_placement_gate_passed": bool(score_impr_pct >= 10.0 or resp_cnt_after > resp_cnt_before)
    }


def main():
    exp_dir = os.path.dirname(__file__)
    os.makedirs(exp_dir, exist_ok=True)
    
    net = WaterNetwork.create_default_network()
    
    # 1. Run Experiment 1
    df_exp1 = run_experiment_1(net)
    csv_path = os.path.join(exp_dir, "observability_results.csv")
    df_exp1.to_csv(csv_path, index=False)
    
    # Evaluate Viability Gate
    det_rate = float((df_exp1["detected"].sum() / len(df_exp1)) * 100.0)
    min_score = float(df_exp1["maximum_anomaly_score"].min())
    max_score = float(df_exp1["maximum_anomaly_score"].max())
    score_diff = float(max_score - min_score)
    
    det_times = df_exp1[df_exp1["detected"]]["time_to_first_strong_anomaly_minutes"]
    time_diff_pct = 0.0
    if len(det_times) >= 2:
        time_diff_pct = float(((det_times.max() - det_times.min()) / max(1.0, det_times.min())) * 100.0)
        
    min_resp = int(df_exp1["responsive_sensor_count"].min())
    max_resp = int(df_exp1["responsive_sensor_count"].max())
    resp_diff_pct = float(((max_resp - min_resp) / max(1, min_resp)) * 100.0)
    
    viability_gate_passed = bool(
        (score_diff >= 0.15) or
        (time_diff_pct >= 20.0) or
        (resp_diff_pct >= 20.0)
    )
    
    # 2. Run Experiment 2 if Viability Gate passed
    exp2_data = {}
    exp3_data = {}
    if viability_gate_passed:
        exp2_data = run_experiment_2(net, df_exp1)
        
        # Select weakest segment for Exp 3
        weakest_seg = str(df_exp1.sort_values(by="maximum_anomaly_score", ascending=True).iloc[0]["segment_id"])
        exp3_data = run_experiment_3(net, weakest_seg)
        
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_segments_tested": len(df_exp1),
        "detection_rate_percent": round(det_rate, 1),
        "anomaly_score_range": [round(min_score, 3), round(max_score, 3)],
        "anomaly_score_diff": round(score_diff, 3),
        "responsive_sensor_count_range": [min_resp, max_resp],
        "detection_time_range_minutes": [float(det_times.min()) if len(det_times) > 0 else -1.0, float(det_times.max()) if len(det_times) > 0 else -1.0],
        "viability_gate_passed": viability_gate_passed,
        "reproducibility": exp2_data.get("reproducibility", []),
        "virtual_sensor_placement": exp3_data,
        "final_verdict": "OBSERVABILITY VALIDATED" if (viability_gate_passed and exp3_data.get("sensor_placement_gate_passed", False)) else "OBSERVABILITY NOT VALIDATED",
        "recommendation": "BUILD" if viability_gate_passed else "DO NOT BUILD"
    }
    
    json_path = os.path.join(exp_dir, "observability_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
        
    print("\n=========================================================================")
    print("      AQUASENTINEL SIMULATED OBSERVABILITY SPIKE RESULTS                ")
    print("=========================================================================")
    print(f"Total Segments Tested: {len(df_exp1)}")
    print(f"Detection Rate:        {det_rate:.1f}%")
    print(f"Score Range:           [{min_score:.3f}, {max_score:.3f}] (Diff: {score_diff:.3f})")
    print(f"Responsive Sensors:    [{min_resp}, {max_resp}]")
    print(f"Viability Gate Passed: {viability_gate_passed}")
    print(f"FINAL VERDICT:        {summary['final_verdict']}")
    print(f"RECOMMENDATION:       {summary['recommendation']}")
    print("=========================================================================\n")


if __name__ == "__main__":
    main()
