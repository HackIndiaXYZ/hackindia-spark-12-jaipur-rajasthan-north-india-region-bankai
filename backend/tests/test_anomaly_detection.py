import pytest
from datetime import datetime, timedelta
import numpy as np

from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.anomaly_detector import AnomalyDetector
from app.models.reading import SensorReading


def test_baseline_and_zscore_calculation():
    detector = AnomalyDetector()
    readings = [
        SensorReading(
            timestamp=datetime(2026, 9, 8, 8, 0, 0),
            sensor_id="B3",
            zone_id="Zone_B",
            pipeline_segment_id="B2-B3",
            pressure=4.0,
            flow_rate=165.0,
            temperature=20.0,
            sensor_health="HEALTHY"
        )
    ]
    results = detector.detect(readings)
    assert len(results) == 1
    res = results[0]
    assert "pressure_zscore" in res.signals
    assert "flow_zscore" in res.signals
    assert res.anomaly_score < 0.55
    assert not res.is_anomalous


def test_rate_of_change_detection():
    detector = AnomalyDetector()
    t1 = datetime(2026, 9, 8, 8, 0, 0)
    t2 = datetime(2026, 9, 8, 8, 1, 0)

    r1 = SensorReading(timestamp=t1, sensor_id="B3", zone_id="Zone_B", pipeline_segment_id="B2-B3", pressure=4.0, flow_rate=165.0, temperature=20.0)
    r2 = SensorReading(timestamp=t2, sensor_id="B3", zone_id="Zone_B", pipeline_segment_id="B2-B3", pressure=1.5, flow_rate=250.0, temperature=20.0)

    results = detector.detect([r1, r2])
    res2 = [r for r in results if r.timestamp == t2][0]

    assert "RATE_OF_CHANGE_ANOMALY" in res2.anomaly_types
    assert res2.signals["pressure_roc"] > 1.0


def test_persistence_detection():
    detector = AnomalyDetector(persistence_window=3)
    start_t = datetime(2026, 9, 8, 8, 0, 0)

    readings = []
    for step in range(5):
        readings.append(SensorReading(
            timestamp=start_t + timedelta(minutes=step),
            sensor_id="B3",
            zone_id="Zone_B",
            pipeline_segment_id="B2-B3",
            pressure=2.0,  # sustained low pressure
            flow_rate=210.0,
            temperature=20.0
        ))

    results = detector.detect(readings)

    # 4th reading (step index 3) should have persistence_count >= 3
    res_last = results[-1]
    assert res_last.persistence_count >= 3
    assert "PERSISTENT_ANOMALY" in res_last.anomaly_types


def test_multivariate_anomaly_score():
    detector = AnomalyDetector()
    r = SensorReading(
        timestamp=datetime(2026, 9, 8, 8, 10, 0),
        sensor_id="B3",
        zone_id="Zone_B",
        pipeline_segment_id="B2-B3",
        pressure=2.2,
        flow_rate=220.0,
        temperature=20.0
    )
    results = detector.detect([r])
    res = results[0]
    assert "MULTIVARIATE_ANOMALY" in res.anomaly_types
    assert res.is_anomalous


def test_neighbor_sensor_comparison():
    detector = AnomalyDetector()
    t = datetime(2026, 9, 8, 8, 10, 0)

    # B2 normal, B3 abnormal, B4 normal
    r_b2 = SensorReading(timestamp=t, sensor_id="B2", zone_id="Zone_B", pipeline_segment_id="B1-B2", pressure=4.4, flow_rate=170.0, temperature=20.0)
    r_b3 = SensorReading(timestamp=t, sensor_id="B3", zone_id="Zone_B", pipeline_segment_id="B2-B3", pressure=1.5, flow_rate=280.0, temperature=20.0)
    r_b4 = SensorReading(timestamp=t, sensor_id="B4", zone_id="Zone_B", pipeline_segment_id="B3-B4", pressure=4.0, flow_rate=135.0, temperature=20.0)

    results = detector.detect([r_b2, r_b3, r_b4])
    b3_res = [r for r in results if r.sensor_id == "B3"][0]

    assert b3_res.neighbor_deviation > 1.5
    assert "SENSOR_ISOLATION_ANOMALY" in b3_res.anomaly_types or "PRESSURE_ANOMALY" in b3_res.anomaly_types


def test_deterministic_anomaly_detector():
    simulator = SensorSimulator()
    config = SimulationConfig(scenario_type="gradual_leak", duration_minutes=20, seed=42)
    readings = simulator.generate_readings(config)

    detector1 = AnomalyDetector()
    detector2 = AnomalyDetector()

    res1 = detector1.detect(readings)
    res2 = detector2.detect(readings)

    assert len(res1) == len(res2)
    for r1, r2 in zip(res1, res2):
        assert r1.sensor_id == r2.sensor_id
        assert pytest.approx(r1.anomaly_score, rel=1e-4) == r2.anomaly_score


def test_normal_scenario_produces_low_anomaly_scores():
    simulator = SensorSimulator()
    config = SimulationConfig(scenario_type="normal", duration_minutes=30, missing_data_prob=0.0, seed=42)
    readings = simulator.generate_readings(config)

    detector = AnomalyDetector()
    results = detector.detect(readings)

    scores = [r.anomaly_score for r in results]
    avg_score = float(np.mean(scores))
    anomalous_cnt = sum(1 for r in results if r.is_anomalous)

    assert avg_score < 0.40
    # Over 90% of normal readings should not be flagged anomalous
    assert (anomalous_cnt / len(results)) < 0.10


def test_gradual_leak_produces_increasing_scores():
    simulator = SensorSimulator()
    config = SimulationConfig(
        scenario_type="gradual_leak",
        affected_zone_id="Zone_B",
        affected_segment_id="B2-B3",
        leak_start_minute=10,
        duration_minutes=30,
        missing_data_prob=0.0,
        seed=42
    )
    readings = simulator.generate_readings(config)

    detector = AnomalyDetector()
    results = detector.detect(readings)

    b3_before = [r.anomaly_score for r in results if r.sensor_id == "B3" and r.timestamp < config.start_time + timedelta(minutes=10)]
    b3_after = [r.anomaly_score for r in results if r.sensor_id == "B3" and r.timestamp >= config.start_time + timedelta(minutes=25)]

    assert np.mean(b3_after) > np.mean(b3_before) + 0.30


def test_sudden_burst_produces_sharp_anomaly_scores():
    simulator = SensorSimulator()
    config = SimulationConfig(
        scenario_type="sudden_burst",
        affected_zone_id="Zone_B",
        affected_segment_id="B2-B3",
        leak_start_minute=15,
        leak_severity=0.8,
        duration_minutes=30,
        missing_data_prob=0.0,
        seed=42
    )
    readings = simulator.generate_readings(config)

    detector = AnomalyDetector()
    results = detector.detect(readings)

    b3_burst = [r for r in results if r.sensor_id == "B3" and r.timestamp == config.start_time + timedelta(minutes=15)][0]
    assert b3_burst.anomaly_score >= 0.70
    assert b3_burst.is_anomalous


def test_sensor_fault_produces_localized_anomaly():
    simulator = SensorSimulator()
    config = SimulationConfig(
        scenario_type="sensor_fault",
        affected_sensor_id="B3",
        fault_type="spike",
        leak_start_minute=10,
        duration_minutes=20,
        missing_data_prob=0.0,
        seed=42
    )
    readings = simulator.generate_readings(config)

    detector = AnomalyDetector()
    results = detector.detect(readings)

    b3_anomalies = [r for r in results if r.sensor_id == "B3" and r.timestamp >= config.start_time + timedelta(minutes=10)]
    b2_anomalies = [r for r in results if r.sensor_id == "B2" and r.timestamp >= config.start_time + timedelta(minutes=10)]

    b3_avg_score = np.mean([r.anomaly_score for r in b3_anomalies])
    b2_avg_score = np.mean([r.anomaly_score for r in b2_anomalies])

    assert b3_avg_score >= 0.75
    assert b2_avg_score < 0.45
