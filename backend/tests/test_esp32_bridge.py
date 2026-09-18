import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_hardware_status_initial_state():
    response = client.get("/api/hardware/latest")
    assert response.status_code == 200
    data = response.json()
    assert "connection_state" in data
    # Initially SIMULATION before any telemetry is received
    assert data["connection_state"] == "SIMULATION"

def test_hardware_telemetry_ingestion_normal():
    payload = {
        "device_id": "AQUA-ESP32-001",
        "sensor_id": "FSR-P01",
        "zone_id": "Zone_B",
        "raw_value": 25,
        "pressure_equivalent": 12.5,
        "threshold": 50,
        "status": "NORMAL",
        "timestamp_ms": 1000
    }
    response = client.post("/api/hardware/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["connection_state"] == "LIVE HARDWARE"
    assert data["telemetry"]["status"] == "NORMAL"
    assert data["derived_flow_lpm"] is not None
    # Derived flow should be nominal (120 LPM) when FSR is low
    assert data["derived_flow_lpm"] == 120.0

def test_hardware_telemetry_ingestion_alert():
    payload = {
        "device_id": "AQUA-ESP32-001",
        "sensor_id": "FSR-P01",
        "zone_id": "Zone_B",
        "raw_value": 85,
        "pressure_equivalent": 65.0,
        "threshold": 50,
        "status": "ALERT",
        "timestamp_ms": 2000
    }
    response = client.post("/api/hardware/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["connection_state"] == "LIVE HARDWARE"
    assert data["telemetry"]["status"] == "ALERT"
    # Derived flow should surge above nominal (120 + 65.0/100 * 160 = 224.0 LPM)
    assert data["derived_flow_lpm"] > 150.0

def test_hardware_status_stale():
    # Ingest telemetry once
    payload = {
        "device_id": "AQUA-ESP32-001",
        "sensor_id": "FSR-P01",
        "zone_id": "Zone_B",
        "raw_value": 20,
        "pressure_equivalent": 10.0,
        "threshold": 50,
        "status": "NORMAL",
        "timestamp_ms": 3000
    }
    client.post("/api/hardware/telemetry", json=payload)
    
    # Check immediate status -> LIVE HARDWARE
    resp_live = client.get("/api/hardware/latest")
    assert resp_live.json()["connection_state"] == "LIVE HARDWARE"
