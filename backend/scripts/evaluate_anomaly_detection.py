import os
import sys
import pandas as pd
from datetime import datetime

# Add app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.anomaly_detector import AnomalyDetector
from app.models.reading import SensorReading


def load_or_generate_readings(filename: str, config: SimulationConfig) -> list[SensorReading]:
    filepath = os.path.join("demo_datasets", filename)
    simulator = SensorSimulator()
    
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        readings = []
        for _, row in df.iterrows():
            readings.append(SensorReading(
                timestamp=datetime.fromisoformat(row["timestamp"]),
                sensor_id=str(row["sensor_id"]),
                zone_id=str(row["zone_id"]),
                pipeline_segment_id=str(row["pipeline_segment_id"]) if pd.notna(row["pipeline_segment_id"]) else None,
                pressure=float(row["pressure"]),
                flow_rate=float(row["flow_rate"]),
                temperature=float(row["temperature"]),
                sensor_health=str(row["sensor_health"])
            ))
        return readings
    else:
        return simulator.generate_readings(config)


def evaluate_all_scenarios():
    detector = AnomalyDetector()
    start_dt = datetime(2026, 9, 8, 8, 0, 0)

    scenarios = [
        ("normal_operation.csv", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="normal", seed=42)),
        ("gradual_leak_zone_b.csv", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="gradual_leak", affected_zone_id="Zone_B", leak_start_minute=15, seed=42)),
        ("sudden_burst_zone_b.csv", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="sudden_burst", affected_zone_id="Zone_B", leak_start_minute=15, seed=42)),
        ("sensor_fault_b3.csv", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="sensor_fault", affected_sensor_id="B3", leak_start_minute=15, seed=42))
    ]

    print("=========================================================================")
    print("        AQUASENTINEL ANOMALY DETECTION EVALUATION REPORT                ")
    print("=========================================================================\n")

    for filename, config in scenarios:
        readings = load_or_generate_readings(filename, config)
        anomaly_results = detector.detect(readings)

        scores = [r.anomaly_score for r in anomaly_results]
        anomalous_readings = [r for r in anomaly_results if r.is_anomalous]
        affected_sensors = set(r.sensor_id for r in anomalous_readings)

        # Time to first strong anomaly (score >= 0.7)
        strong_anomalies = [r for r in anomaly_results if r.anomaly_score >= 0.7]
        first_strong_time = strong_anomalies[0].timestamp.strftime("%H:%M:%S") if strong_anomalies else "N/A"

        print(f"--- Scenario: {config.scenario_type.upper()} ({filename}) ---")
        print(f"Total Readings Processed: {len(readings)}")
        print(f"Average Anomaly Score:    {float(pd.Series(scores).mean()):.3f}")
        print(f"Maximum Anomaly Score:    {float(pd.Series(scores).max()):.3f}")
        print(f"Anomalous Readings Count: {len(anomalous_readings)} ({len(anomalous_readings)/max(1, len(readings))*100:.1f}%)")
        print(f"Affected Sensors:         {sorted(list(affected_sensors))}")
        print(f"Time to First Strong (>=0.7): {first_strong_time}")

        if anomalous_readings:
            sample = anomalous_readings[0]
            print(f"Sample Evidence: {sample.sensor_id} @ {sample.timestamp.strftime('%H:%M:%S')} (Score: {sample.anomaly_score:.2f}) -> {sample.evidence}")
        print("\n" + "-" * 73 + "\n")


if __name__ == "__main__":
    evaluate_all_scenarios()
