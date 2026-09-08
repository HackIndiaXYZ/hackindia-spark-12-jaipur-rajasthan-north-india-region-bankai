import pytest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.services.simulator import SensorSimulator, SimulationConfig
from app.models.reading import SensorReading


def test_deterministic_output_with_same_seed():
    config1 = SimulationConfig(seed=123, duration_minutes=15)
    config2 = SimulationConfig(seed=123, duration_minutes=15)

    simulator = SensorSimulator()
    readings1 = simulator.generate_readings(config1)
    readings2 = simulator.generate_readings(config2)

    assert len(readings1) == len(readings2)
    for r1, r2 in zip(readings1, readings2):
        assert r1.sensor_id == r2.sensor_id
        assert r1.timestamp == r2.timestamp
        assert pytest.approx(r1.pressure, rel=1e-5) == r2.pressure
        assert pytest.approx(r1.flow_rate, rel=1e-5) == r2.flow_rate


def test_normal_simulation():
    config = SimulationConfig(scenario_type="normal", duration_minutes=30, missing_data_prob=0.0)
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    # 30 minutes * 60 seconds / 60 seconds interval = 30 steps * 10 sensors = 300 readings
    assert len(readings) == 300

    # Ensure all pressures and flows are positive and within physical bounds
    for r in readings:
        assert 0.5 <= r.pressure <= 8.0
        assert 10.0 <= r.flow_rate <= 300.0
        assert r.sensor_health == "HEALTHY"


def test_time_of_day_demand_variation():
    # Morning peak (08:00) vs Night trough (03:00)
    dt_morning = datetime(2026, 9, 8, 8, 0, 0)
    dt_night = datetime(2026, 9, 8, 3, 0, 0)

    mult_morning = SensorSimulator.get_demand_multiplier(dt_morning)
    mult_night = SensorSimulator.get_demand_multiplier(dt_night)

    assert mult_morning > mult_night
    assert mult_morning >= 1.2
    assert mult_night <= 0.8


def test_sensor_specific_baselines():
    config = SimulationConfig(scenario_type="normal", duration_minutes=5, missing_data_prob=0.0)
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    # Group readings by sensor_id
    b1_flows = [r.flow_rate for r in readings if r.sensor_id == "B1"]
    a1_flows = [r.flow_rate for r in readings if r.sensor_id == "A1"]

    # Zone B industrial nominal flow (150 LPM) vs Zone A residential nominal flow (80 LPM)
    assert np.mean(b1_flows) > np.mean(a1_flows)


def test_noise_and_drift_effects():
    config_low_noise = SimulationConfig(noise_level=0.001, drift_rate=0.0, duration_minutes=20, missing_data_prob=0.0)
    config_high_noise = SimulationConfig(noise_level=0.1, drift_rate=0.0, duration_minutes=20, missing_data_prob=0.0)

    simulator = SensorSimulator()
    r_low = simulator.generate_readings(config_low_noise)
    r_high = simulator.generate_readings(config_high_noise)

    b3_low = [r.pressure for r in r_low if r.sensor_id == "B3"]
    b3_high = [r.pressure for r in r_high if r.sensor_id == "B3"]

    assert np.std(b3_high) > np.std(b3_low)


def test_gradual_leak_scenario():
    config = SimulationConfig(
        scenario_type="gradual_leak",
        affected_zone_id="Zone_B",
        affected_segment_id="B2-B3",
        leak_start_minute=10,
        duration_minutes=30,
        missing_data_prob=0.0
    )
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    b3_before = [r.pressure for r in readings if r.sensor_id == "B3" and r.timestamp < config.start_time + timedelta(minutes=10)]
    b3_after_late = [r.pressure for r in readings if r.sensor_id == "B3" and r.timestamp >= config.start_time + timedelta(minutes=25)]

    # Pressure at affected location B3 should drop significantly after gradual leak ramps up
    assert np.mean(b3_after_late) < np.mean(b3_before) * 0.8


def test_sudden_burst_scenario():
    config = SimulationConfig(
        scenario_type="sudden_burst",
        affected_zone_id="Zone_B",
        affected_segment_id="B2-B3",
        leak_start_minute=15,
        leak_severity=0.8,
        duration_minutes=30,
        missing_data_prob=0.0
    )
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    b3_before = [r.pressure for r in readings if r.sensor_id == "B3" and r.timestamp < config.start_time + timedelta(minutes=15)]
    b3_immediately_after = [r.pressure for r in readings if r.sensor_id == "B3" and r.timestamp >= config.start_time + timedelta(minutes=16)]

    # Immediate sharp pressure drop
    assert np.mean(b3_immediately_after) < np.mean(b3_before) * 0.65


def test_sensor_fault_scenario():
    config = SimulationConfig(
        scenario_type="sensor_fault",
        affected_sensor_id="B3",
        fault_type="spike",
        leak_start_minute=10,
        duration_minutes=20,
        missing_data_prob=0.0
    )
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    # B3 should show FAULTY health status after fault start
    b3_faulty_readings = [r for r in readings if r.sensor_id == "B3" and r.timestamp >= config.start_time + timedelta(minutes=10)]
    b2_readings = [r for r in readings if r.sensor_id == "B2" and r.timestamp >= config.start_time + timedelta(minutes=10)]

    assert len(b3_faulty_readings) > 0
    for r in b3_faulty_readings:
        assert r.sensor_health == "FAULTY"

    # Other sensors in the network should remain unaffected (HEALTHY)
    for r in b2_readings:
        assert r.sensor_health == "HEALTHY"


def test_missing_readings_handling():
    config = SimulationConfig(duration_minutes=30, missing_data_prob=0.20, seed=42)
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    # Expected max = 300 readings. With 20% missing, total readings should be noticeably fewer than 300.
    assert len(readings) < 290


def test_csv_and_json_export():
    config = SimulationConfig(duration_minutes=5, missing_data_prob=0.0)
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    csv_str = simulator.to_csv_string(readings)
    json_str = simulator.to_json_string(readings)

    assert "timestamp,sensor_id,zone_id,pipeline_segment_id,pressure,flow_rate,temperature,sensor_health" in csv_str
    assert "B3" in json_str
    assert "Zone_B" in json_str


def test_data_quality_and_timestamp_ordering():
    config = SimulationConfig(duration_minutes=10, missing_data_prob=0.0)
    simulator = SensorSimulator()
    readings = simulator.generate_readings(config)

    # Group by sensor and check strict ascending timestamps
    sensors = set(r.sensor_id for r in readings)
    for s in sensors:
        s_readings = [r for r in readings if r.sensor_id == s]
        for i in range(len(s_readings) - 1):
            assert s_readings[i].timestamp < s_readings[i+1].timestamp
