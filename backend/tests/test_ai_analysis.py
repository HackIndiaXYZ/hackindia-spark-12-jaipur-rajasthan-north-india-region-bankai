import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_service import AIAnalysisService
from app.schemas.ai_analysis import AIAnalysisResponse, AIAnalysisResult
from app.services.incident_service import IncidentService
from app.services.simulator import SensorSimulator, SimulationConfig
from app.models.incident import IncidentStatus

client = TestClient(app)


def test_ai_service_fallback_mode():
    service = AIAnalysisService()
    # Force fallback mode by nullifying client
    service._client = None

    incident_data = {
        "incident_id": "INC-TEST-001",
        "incident_type": "LEAK_SUSPECTED",
        "severity": "HIGH",
        "affected_segment": "B2-B3",
        "affected_zone": "Zone_B",
        "confidence": 0.85,
        "observability_score": 0.90,
        "estimated_flow_loss_lpm": 25.0,
        "estimated_volume_loss_liters": 500.0,
        "responsive_sensors": ["B1", "B2", "B3"],
        "evidence": ["Pressure drop detected on B2."]
    }

    res = service.analyze_incident(incident_data, force_refresh=True)
    assert isinstance(res, AIAnalysisResponse)
    assert res.provider == "deterministic_fallback"
    assert "B2-B3" in res.analysis.summary
    assert len(res.analysis.why_detected) > 0
    assert len(res.analysis.recommended_actions) > 0


def test_ai_service_sensor_fault_grounding():
    service = AIAnalysisService()
    service._client = None

    sensor_fault_data = {
        "incident_id": "INC-FAULT-002",
        "incident_type": "SENSOR_FAULT",
        "severity": "HIGH",
        "affected_segment": "B2-B3",
        "affected_zone": "Zone_B",
        "confidence": 0.92,
        "responsive_sensors": ["B3"],
        "evidence": ["Sensor B3 spike fault (+2.8 bar). Neighboring sensors B2 & B4 remain normal."]
    }

    res = service.analyze_incident(sensor_fault_data, force_refresh=True)
    assert res.provider == "deterministic_fallback"
    assert "sensor fault" in res.analysis.summary.lower()
    assert any("recalibrate" in a.lower() or "inspect" in a.lower() for a in res.analysis.recommended_actions)


def test_ai_service_caching():
    service = AIAnalysisService()
    service._client = None

    incident_data = {
        "incident_id": "INC-CACHE-TEST",
        "incident_type": "LEAK_SUSPECTED",
        "affected_segment": "B2-B3"
    }

    res1 = service.analyze_incident(incident_data)
    res2 = service.analyze_incident(incident_data)
    assert res1 is res2  # Same object returned from cache


def test_ai_service_grounding_no_contradiction():
    service = AIAnalysisService()
    service._client = None

    incident_data = {
        "incident_id": "INC-GROUND-001",
        "incident_type": "BURST_EVENT",
        "severity": "CRITICAL",
        "affected_segment": "A1-A2",
        "affected_zone": "Zone_A",
        "confidence": 0.95,
        "estimated_flow_loss_lpm": 120.0,
        "estimated_volume_loss_liters": 2400.0,
        "responsive_sensors": ["A1", "A2"],
        "evidence": ["Sudden pressure drop on A1."]
    }

    res = service.analyze_incident(incident_data, force_refresh=True)
    assert res.provider == "deterministic_fallback"
    assert "A1-A2" in res.analysis.summary or "A1-A2" in str(res.analysis.why_detected)
    assert "Zone_A" in res.analysis.summary or "Zone_A" in str(res.analysis.recommended_actions)
    assert not any("B2-B3" in act for act in res.analysis.recommended_actions)  # Must not introduce wrong segment


def test_api_ai_analysis_endpoint(client: TestClient):
    simulator = SensorSimulator()
    readings = simulator.generate_readings(SimulationConfig(scenario_type="gradual_leak", seed=201))
    payload = [r.to_dict() for r in readings]

    # 1. Analyze and persist incident via API
    res_post = client.post("/api/incidents/analyze", json=payload)
    assert res_post.status_code == 200
    inc_data = res_post.json()
    inc_id = inc_data["incident_id"]

    # 2. Call POST /api/incidents/{incident_id}/ai-analysis
    response = client.post(f"/api/incidents/{inc_id}/ai-analysis")
    assert response.status_code == 200
    data = response.json()

    assert data["incident_id"] == inc_id
    assert "analysis" in data
    assert "provider" in data
    assert "summary" in data["analysis"]
    assert isinstance(data["analysis"]["why_detected"], list)
    assert isinstance(data["analysis"]["recommended_actions"], list)


def test_api_ai_analysis_not_found(client: TestClient):
    response = client.post("/api/incidents/INC-NON-EXISTENT/ai-analysis")
    assert response.status_code == 404

