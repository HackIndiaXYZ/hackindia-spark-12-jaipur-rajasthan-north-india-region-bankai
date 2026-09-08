import os
import sys
from datetime import datetime

# Add app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.simulator import SensorSimulator, SimulationConfig
from app.core.logging import logger

def generate_all_demo_scenarios(output_dir: str = "demo_datasets"):
    os.makedirs(output_dir, exist_ok=True)
    simulator = SensorSimulator()
    start_dt = datetime(2026, 9, 8, 8, 0, 0)

    scenarios = [
        ("normal_operation.csv", SimulationConfig(
            start_time=start_dt, duration_minutes=60, scenario_type="normal", seed=42
        )),
        ("gradual_leak_zone_b.csv", SimulationConfig(
            start_time=start_dt, duration_minutes=60, scenario_type="gradual_leak",
            affected_zone_id="Zone_B", affected_segment_id="B2-B3", leak_start_minute=15, leak_severity=0.6, seed=42
        )),
        ("sudden_burst_zone_b.csv", SimulationConfig(
            start_time=start_dt, duration_minutes=60, scenario_type="sudden_burst",
            affected_zone_id="Zone_B", affected_segment_id="B2-B3", leak_start_minute=15, leak_severity=0.8, seed=42
        )),
        ("sensor_fault_b3.csv", SimulationConfig(
            start_time=start_dt, duration_minutes=60, scenario_type="sensor_fault",
            affected_sensor_id="B3", fault_type="spike", leak_start_minute=15, seed=42
        )),
    ]

    for filename, config in scenarios:
        filepath = os.path.join(output_dir, filename)
        readings = simulator.generate_readings(config)
        simulator.export_to_csv(readings, filepath)
        print(f"Generated {len(readings)} readings -> {filepath}")

if __name__ == "__main__":
    generate_all_demo_scenarios()
