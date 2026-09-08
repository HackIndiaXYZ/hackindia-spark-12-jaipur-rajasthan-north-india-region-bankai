import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.government_data_loader import GovernmentDataLoader
from app.services.government_data_service import GovernmentDataContextService

client = TestClient(app)


def test_timestamp_parsing():
    loader = GovernmentDataLoader()
    assert loader.parse_timestamp("17-10-2021 07:00") == "2021-10-17 07:00"
    assert loader.parse_timestamp("2021-10-17 07:00:00") == "2021-10-17 07:00"
    assert loader.parse_timestamp(None) is None
    assert loader.parse_timestamp("-") is None
    assert loader.parse_timestamp("") is None


def test_numeric_parsing():
    loader = GovernmentDataLoader()
    assert loader.parse_numeric("12.5") == 12.5
    assert loader.parse_numeric(5) == 5.0
    assert loader.parse_numeric(None) is None
    assert loader.parse_numeric("-") is None
    assert loader.parse_numeric("null") is None
    assert loader.parse_numeric("invalid") is None


def test_government_data_service_sources():
    service = GovernmentDataContextService()
    sources = service.list_sources()
    assert len(sources) >= 3
    source_ids = [s.source_id for s in sources]
    assert "rajasthan_rainfall_telemetry" in source_ids
    assert "mahi_canal_discharge" in source_ids
    assert "bisalpur_dam_discharge" in source_ids

    # Source metadata checks
    rainfall_src = service.get_source("rajasthan_rainfall_telemetry")
    assert rainfall_src is not None
    assert rainfall_src.agency == "Rajasthan Surface Water Department"
    assert rainfall_src.zone is None  # Ensures spatial mapping is not fabricated


def test_government_data_service_summaries():
    service = GovernmentDataContextService()
    summary = service.get_summary("rajasthan_rainfall_telemetry")
    assert summary is not None
    assert summary.source_id == "rajasthan_rainfall_telemetry"
    assert summary.observation_count > 0
    assert summary.mean_value is not None
    assert summary.min_value is not None
    assert summary.max_value is not None
    assert summary.coverage_start is not None


def test_government_data_service_recent_context():
    service = GovernmentDataContextService()
    recent = service.get_recent_context("mahi_canal_discharge", limit=10)
    assert isinstance(recent, list)
    assert len(recent) <= 10
    if len(recent) > 0:
        obs = recent[0]
        assert obs.unit == "cusec"
        assert obs.timestamp is not None


def test_api_list_data_sources():
    response = client.get("/api/data-sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "total_count" in data
    assert data["total_count"] >= 3
    sources = data["sources"]
    assert any(s["source_id"] == "rajasthan_rainfall_telemetry" for s in sources)


def test_api_get_data_source_detail():
    response = client.get("/api/data-sources/mahi_canal_discharge")
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == "mahi_canal_discharge"
    assert data["agency"] == "Rajasthan Surface Water Department"
    assert data["unit"] == "cusec"


def test_api_get_data_source_summary():
    response = client.get("/api/data-sources/bisalpur_dam_discharge/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == "bisalpur_dam_discharge"
    assert "mean_value" in data
    assert "observation_count" in data


def test_api_get_recent_observations():
    response = client.get("/api/data-sources/rajasthan_rainfall_telemetry/recent?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == "rajasthan_rainfall_telemetry"
    assert "observations" in data
    assert len(data["observations"]) <= 5


def test_api_data_source_not_found():
    response = client.get("/api/data-sources/non_existent_source")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
