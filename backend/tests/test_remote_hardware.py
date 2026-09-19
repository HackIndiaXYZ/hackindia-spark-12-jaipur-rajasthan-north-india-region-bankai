import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_health_check_version_1_1_0():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.1.0"

def test_hardware_telemetry_remote_ingestion():
    payload = {
        "device_id": "AQUA-ESP32-001",
        "sensor_id": "FSR-P01",
        "zone_id": "Zone_B",
        "raw_value": 120,
        "pressure_equivalent": 45.0,
        "threshold": 50,
        "status": "ALERT",
        "timestamp_ms": int(time.time() * 1000)
    }

    res = client.post("/api/hardware/telemetry", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["connection_state"] == "LIVE HARDWARE"
    assert data["telemetry"]["sensor_id"] == "FSR-P01"
    assert data["pipeline_incident"] is not None

def test_hardware_telemetry_malformed_rejection():
    # Negative raw_value triggers validation error
    malformed_payload = {
        "device_id": "AQUA-ESP32-001",
        "sensor_id": "FSR-P01",
        "zone_id": "Zone_B",
        "raw_value": -5,
        "pressure_equivalent": 45.0,
        "threshold": 50,
        "status": "ALERT",
        "timestamp_ms": 123456
    }
    res = client.post("/api/hardware/telemetry", json=malformed_payload)
    assert res.status_code == 422

def test_hardware_latest_stale_detection(monkeypatch):
    payload = {
        "device_id": "AQUA-ESP32-001",
        "sensor_id": "FSR-P01",
        "zone_id": "Zone_B",
        "raw_value": 20,
        "pressure_equivalent": 10.0,
        "threshold": 50,
        "status": "NORMAL",
        "timestamp_ms": int(time.time() * 1000)
    }

    client.post("/api/hardware/telemetry", json=payload)

    # Immediately after POST: LIVE HARDWARE
    latest_res = client.get("/api/hardware/latest")
    assert latest_res.status_code == 200
    assert latest_res.json()["connection_state"] == "LIVE HARDWARE"

    # Simulate elapsed time beyond stale threshold
    monkeypatch.setattr(settings, "ESP32_STALE_THRESHOLD_SEC", 0.1)
    time.sleep(0.15)

    stale_res = client.get("/api/hardware/latest")
    assert stale_res.status_code == 200
    assert stale_res.json()["connection_state"] == "DISCONNECTED"
    assert stale_res.json()["pipeline_incident"] is None

def test_hardware_ingest_token_authentication(monkeypatch):
    monkeypatch.setattr(settings, "HARDWARE_INGEST_TOKEN", "SECRET_TOKEN_123")

    payload = {
        "device_id": "AQUA-ESP32-001",
        "sensor_id": "FSR-P01",
        "zone_id": "Zone_B",
        "raw_value": 30,
        "pressure_equivalent": 15.0,
        "threshold": 50,
        "status": "NORMAL",
        "timestamp_ms": int(time.time() * 1000)
    }

    # Unauthenticated request should fail with 401
    res_unauth = client.post("/api/hardware/telemetry", json=payload)
    assert res_unauth.status_code == 401

    # Authenticated request with header should succeed
    res_auth = client.post(
        "/api/hardware/telemetry",
        json=payload,
        headers={"X-Hardware-Token": "SECRET_TOKEN_123"}
    )
    assert res_auth.status_code == 200
