import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.incident_service import IncidentService
from app.db.repositories.incident_repository import IncidentRepository, generate_incident_fingerprint
from app.models.incident import IncidentResult, IncidentStatus, IncidentSeverity, IncidentType


def test_incident_db_creation_and_retrieval(db_session):
    service = IncidentService()
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(scenario_type="gradual_leak", seed=42))

    inc = service.process_and_persist_telemetry(readings, db=db_session)
    assert inc is not None

    fetched = IncidentRepository.get_by_id(db_session, inc.incident_id)
    assert fetched is not None
    assert fetched.incident_id == inc.incident_id
    assert fetched.affected_segment == "B2-B3"
    assert fetched.status == "OPEN"
    assert len(fetched.evidence) > 0
    assert len(fetched.candidate_segments) > 0


def test_incident_status_lifecycle_transitions(db_session):
    service = IncidentService()
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(scenario_type="sudden_burst", seed=42))

    inc = service.process_and_persist_telemetry(readings, db=db_session)
    assert inc is not None
    assert inc.status == IncidentStatus.OPEN

    # OPEN -> ACKNOWLEDGED
    model_ack = IncidentRepository.update_status(db_session, inc.incident_id, "ACKNOWLEDGED")
    assert model_ack.status == "ACKNOWLEDGED"

    # ACKNOWLEDGED -> RESOLVED
    model_res = IncidentRepository.update_status(db_session, inc.incident_id, "RESOLVED")
    assert model_res.status == "RESOLVED"

    # Invalid: RESOLVED -> OPEN should raise ValueError
    with pytest.raises(ValueError, match="Invalid status transition"):
        IncidentRepository.update_status(db_session, inc.incident_id, "OPEN")


def test_idempotent_deduplication(db_session):
    service = IncidentService()
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(scenario_type="gradual_leak", seed=42))

    # First submission creates incident
    inc1 = service.process_and_persist_telemetry(readings, db=db_session)
    # Second submission with identical readings returns existing model
    inc2 = service.process_and_persist_telemetry(readings, db=db_session)

    assert inc1 is not None and inc2 is not None
    assert inc1.incident_id == inc2.incident_id
    assert inc1.fingerprint == inc2.fingerprint


def test_incidents_api_endpoints(client: TestClient, db_session):
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(scenario_type="sudden_burst", seed=42))
    payload = [r.to_dict() for r in readings]

    # 1. POST /api/incidents/analyze
    res_post = client.post("/api/incidents/analyze", json=payload)
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["incident_id"] is not None
    inc_id = data_post["incident_id"]
    assert data_post["status"] == "OPEN"

    # 2. GET /api/incidents/{incident_id}
    res_get = client.get(f"/api/incidents/{inc_id}")
    assert res_get.status_code == 200
    assert res_get.json()["incident_id"] == inc_id

    # 3. GET /api/incidents (list)
    res_list = client.get("/api/incidents?status=OPEN")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 4. PATCH /api/incidents/{incident_id}/status
    res_patch = client.patch(f"/api/incidents/{inc_id}/status", json={"status": "ACKNOWLEDGED"})
    assert res_patch.status_code == 200
    assert res_patch.json()["status"] == "ACKNOWLEDGED"

    # 5. Invalid PATCH -> HTTP 400
    res_invalid_patch = client.patch(f"/api/incidents/{inc_id}/status", json={"status": "OPEN"})
    assert res_invalid_patch.status_code == 400
