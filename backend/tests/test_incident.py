import pytest
from datetime import datetime, timedelta

from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.incident_service import IncidentService
from app.services.localization import LeakLocalizer
from app.services.loss_estimator import WaterLossEstimator
from app.models.reading import SensorReading
from app.models.incident import IncidentType, IncidentSeverity


def test_normal_telemetry_produces_no_incident():
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(scenario_type="normal", duration_minutes=30, seed=42))

    service = IncidentService()
    incident = service.process_telemetry(readings)

    assert incident is None


def test_gradual_leak_produces_leak_suspected_incident():
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(
        scenario_type="gradual_leak",
        affected_zone_id="Zone_B",
        affected_segment_id="B2-B3",
        leak_start_minute=15,
        leak_severity=0.6,
        seed=42
    ))

    service = IncidentService()
    incident = service.process_telemetry(readings)

    assert incident is not None
    assert incident.affected_segment == "B2-B3"
    assert incident.affected_zone == "Zone_B"
    assert incident.incident_type in [IncidentType.LEAK_SUSPECTED, IncidentType.BURST_EVENT]
    assert 0.0 <= incident.confidence <= 1.0
    assert incident.estimated_flow_loss_lpm >= 0.0
    assert incident.estimated_volume_loss_liters >= 0.0


def test_sudden_burst_produces_burst_incident():
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(
        scenario_type="sudden_burst",
        affected_zone_id="Zone_B",
        affected_segment_id="B2-B3",
        leak_start_minute=15,
        leak_severity=0.8,
        seed=42
    ))

    service = IncidentService()
    incident = service.process_telemetry(readings)

    assert incident is not None
    assert incident.affected_segment in ["B2-B3", "B1-B2"]
    assert any(c.segment_id == "B2-B3" for c in incident.candidate_segments)
    assert incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]


def test_sensor_fault_alone_produces_no_leak_incident():
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(
        scenario_type="sensor_fault",
        affected_sensor_id="B3",
        fault_type="spike",
        leak_start_minute=10,
        seed=42
    ))

    service = IncidentService()
    incident = service.process_telemetry(readings)

    # Isolated sensor fault must NOT create a pipeline leak incident
    assert incident is None


test_multiple_anomalies_localizes_plausible_segment = lambda: _test_multiple_anomalies()

def _test_multiple_anomalies():
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(
        scenario_type="multiple_anomalies",
        affected_zone_id="Zone_B",
        affected_segment_id="B2-B3",
        affected_sensor_id="A2",
        leak_start_minute=15,
        seed=42
    ))

    service = IncidentService()
    incident = service.process_telemetry(readings)

    assert incident is not None
    assert incident.affected_segment == "B2-B3"


def test_confidence_and_severity_bounds():
    service = IncidentService()
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(scenario_type="sudden_burst", seed=42))

    incident = service.process_telemetry(readings)

    assert incident is not None
    assert 0.0 <= incident.confidence <= 1.0
    assert incident.severity.value in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_loss_estimator_safety_with_zero_duration_or_empty_data():
    estimator = WaterLossEstimator()
    res = estimator.estimate_loss([], [], "B2-B3")

    assert res["estimated_flow_loss_lpm"] == 0.0
    assert res["estimated_volume_loss_liters"] == 0.0
    assert "disclaimer" in res


def test_deterministic_incident_pipeline():
    simulator = SensorSimulator()
    readings1 = simulator.generate_readings(SimulationConfig(scenario_type="gradual_leak", seed=123))
    readings2 = simulator.generate_readings(SimulationConfig(scenario_type="gradual_leak", seed=123))

    service1 = IncidentService()
    service2 = IncidentService()

    inc1 = service1.process_telemetry(readings1)
    inc2 = service2.process_telemetry(readings2)

    assert inc1 is not None and inc2 is not None
    assert inc1.affected_segment == inc2.affected_segment
    assert pytest.approx(inc1.confidence, rel=1e-5) == inc2.confidence
    assert pytest.approx(inc1.estimated_flow_loss_lpm, rel=1e-5) == inc2.estimated_flow_loss_lpm
