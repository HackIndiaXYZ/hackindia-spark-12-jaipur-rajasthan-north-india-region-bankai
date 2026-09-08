import os
import sys
import pandas as pd
from datetime import datetime

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.incident_service import IncidentService


def run_incident_evaluation():
    exp_dir = os.path.dirname(__file__)
    os.makedirs(exp_dir, exist_ok=True)

    simulator = SensorSimulator()
    service = IncidentService()
    start_dt = datetime(2026, 9, 8, 8, 0, 0)

    scenarios = [
        ("NORMAL OPERATION", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="normal", seed=42), None),
        ("GRADUAL LEAK", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="gradual_leak", affected_zone_id="Zone_B", affected_segment_id="B2-B3", leak_start_minute=15, leak_severity=0.6, seed=42), "B2-B3"),
        ("SUDDEN BURST", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="sudden_burst", affected_zone_id="Zone_B", affected_segment_id="B2-B3", leak_start_minute=15, leak_severity=0.8, seed=42), "B2-B3"),
        ("SENSOR FAULT", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="sensor_fault", affected_sensor_id="B3", fault_type="spike", leak_start_minute=15, seed=42), None),
        ("MULTIPLE ANOMALIES", SimulationConfig(start_time=start_dt, duration_minutes=60, scenario_type="multiple_anomalies", affected_zone_id="Zone_B", affected_segment_id="B2-B3", affected_sensor_id="A2", leak_start_minute=15, seed=42), "B2-B3"),
    ]

    print("=========================================================================")
    print("        AQUASENTINEL INCIDENT PIPELINE EVALUATION REPORT                 ")
    print("=========================================================================\n")

    eval_rows = []

    for name, config, ground_truth_seg in scenarios:
        readings = simulator.generate_readings(config)
        incident = service.process_telemetry(readings)

        if incident:
            is_loc_correct = (incident.affected_segment == ground_truth_seg) if ground_truth_seg else "N/A (No Leak)"
            print(f"--- Scenario: {name} ---")
            print(f"Incident Created:     YES ({incident.incident_id})")
            print(f"Incident Type:        {incident.incident_type.value}")
            print(f"Localized Segment:    {incident.affected_segment} (Ground Truth: {ground_truth_seg or 'None'})")
            print(f"Localization Correct: {is_loc_correct}")
            print(f"Localized Zone:       {incident.affected_zone}")
            print(f"Confidence:           {incident.confidence:.3f}")
            print(f"Severity:             {incident.severity.value}")
            print(f"Estimated Flow Loss:  {incident.estimated_flow_loss_lpm:.2f} LPM")
            print(f"Estimated Vol Loss:   {incident.estimated_volume_loss_liters:.1f} Liters")
            print(f"Responsive Sensors:   {incident.responsive_sensors}")
            print(f"Sample Evidence:      {incident.evidence[0] if incident.evidence else ''}")

            eval_rows.append({
                "scenario": name,
                "incident_created": True,
                "incident_type": incident.incident_type.value,
                "localized_segment": incident.affected_segment,
                "ground_truth_segment": ground_truth_seg or "None",
                "localization_correct": is_loc_correct,
                "confidence": incident.confidence,
                "severity": incident.severity.value,
                "estimated_flow_loss_lpm": incident.estimated_flow_loss_lpm,
                "estimated_volume_loss_liters": incident.estimated_volume_loss_liters
            })
        else:
            is_loc_correct = True if ground_truth_seg is None else False
            print(f"--- Scenario: {name} ---")
            print(f"Incident Created:     NO")
            print(f"Ground Truth Segment: {ground_truth_seg or 'None (Normal/Fault Only)'}")
            print(f"Classification Correct: {is_loc_correct}")

            eval_rows.append({
                "scenario": name,
                "incident_created": False,
                "incident_type": "NONE",
                "localized_segment": "NONE",
                "ground_truth_segment": ground_truth_seg or "None",
                "localization_correct": is_loc_correct,
                "confidence": 0.0,
                "severity": "NONE",
                "estimated_flow_loss_lpm": 0.0,
                "estimated_volume_loss_liters": 0.0
            })

        print("\n" + "-" * 73 + "\n")

    df = pd.DataFrame(eval_rows)
    csv_path = os.path.join(exp_dir, "incident_evaluation.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved evaluation results -> {csv_path}\n")


if __name__ == "__main__":
    run_incident_evaluation()
