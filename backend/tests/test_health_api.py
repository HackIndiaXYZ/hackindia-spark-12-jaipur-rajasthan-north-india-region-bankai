def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AquaSentinel" in data["service"]


def test_network_status(client):
    response = client.get("/api/network")
    assert response.status_code == 200
    data = response.json()
    assert "network_status" in data
    assert data["total_sensors"] == 10
    assert data["healthy_sensors"] == 10


def test_network_topology(client):
    response = client.get("/api/network/topology")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AquaSentinel Synthetic Network"
    assert len(data["zones"]) == 3
    assert len(data["sensors"]) == 10
    assert len(data["segments"]) == 10
