import pytest
from app.models.zone import Zone
from app.models.pipeline import PipelineSegment
from app.models.sensor import Sensor, HealthStatus
from app.models.network import WaterNetwork, NetworkNode
from app.schemas.zone import ZoneSchema
from app.schemas.pipeline import PipelineSegmentSchema
from app.schemas.sensor import SensorSchema
from app.schemas.network import NetworkTopologySchema, NetworkStatusSchema


def test_zone_creation():
    zone = Zone(zone_id="Zone_A", name="Zone A", description="Test Zone", target_pressure_bar=4.0, target_flow_lpm=100.0)
    assert zone.zone_id == "Zone_A"
    assert zone.name == "Zone A"
    assert zone.target_pressure_bar == 4.0
    assert zone.target_flow_lpm == 100.0


def test_pipeline_segment_properties():
    seg = PipelineSegment(
        segment_id="B2-B3",
        source_node="B2",
        destination_node="B3",
        zone_id="Zone_B",
        length_m=200.0,
        nominal_flow_range=(70.0, 180.0),
        nominal_pressure_range=(3.8, 4.8)
    )
    assert seg.segment_id == "B2-B3"
    assert seg.nominal_min_flow == 70.0
    assert seg.nominal_max_flow == 180.0
    assert seg.nominal_min_pressure == 3.8
    assert seg.nominal_max_pressure == 4.8


def test_sensor_creation():
    sensor = Sensor(
        sensor_id="B3",
        zone_id="Zone_B",
        pipeline_segment_id="B2-B3",
        location_node="B3",
        health_status=HealthStatus.HEALTHY
    )
    assert sensor.sensor_id == "B3"
    assert sensor.health_status == HealthStatus.HEALTHY


def test_default_water_network():
    net = WaterNetwork.create_default_network()
    
    # Check zones count (Zone A, Zone B, Zone C)
    assert len(net.zones) == 3
    assert "Zone_A" in net.zones
    assert "Zone_B" in net.zones
    assert "Zone_C" in net.zones

    # Check sensors count
    assert len(net.sensors) == 10

    # Check segments count
    assert len(net.segments) == 10

    # Check graph connectivity
    assert net.graph.has_node("Reservoir")
    assert net.graph.has_node("B3")
    assert net.graph.has_edge("B2", "B3")


def test_candidate_segment_search():
    net = WaterNetwork.create_default_network()
    # Path from B2 to B4 passes through B2-B3 and B3-B4
    candidate_segs = net.get_candidate_segments("B2", "B4")
    candidate_ids = [s.segment_id for s in candidate_segs]
    assert "B2-B3" in candidate_ids
    assert "B3-B4" in candidate_ids


def test_pydantic_schema_validation():
    zone_data = {
        "zone_id": "Zone_B",
        "name": "Zone B Industrial",
        "description": "Industrial district",
        "target_pressure_bar": 4.5,
        "target_flow_lpm": 150.0
    }
    schema = ZoneSchema(**zone_data)
    assert schema.zone_id == "Zone_B"
    assert schema.target_pressure_bar == 4.5
