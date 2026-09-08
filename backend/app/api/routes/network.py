from fastapi import APIRouter
from app.models.network import WaterNetwork
from app.schemas.network import NetworkTopologySchema, NetworkStatusSchema, NetworkNodeSchema
from app.schemas.zone import ZoneSchema
from app.schemas.pipeline import PipelineSegmentSchema
from app.schemas.sensor import SensorSchema

router = APIRouter(prefix="/network", tags=["Network Topology"])

# Cache default network instance for local runtime
_default_network = WaterNetwork.create_default_network()


@router.get("", response_model=NetworkStatusSchema)
def get_network_status():
    total_sensors = len(_default_network.sensors)
    healthy_sensors = sum(1 for s in _default_network.sensors.values() if s.health_status == "HEALTHY")
    degraded_sensors = sum(1 for s in _default_network.sensors.values() if s.health_status == "DEGRADED")
    faulty_sensors = sum(1 for s in _default_network.sensors.values() if s.health_status == "FAULTY")

    status_str = "HEALTHY" if faulty_sensors == 0 and degraded_sensors == 0 else "DEGRADED"

    return NetworkStatusSchema(
        network_status=status_str,
        total_sensors=total_sensors,
        healthy_sensors=healthy_sensors,
        degraded_sensors=degraded_sensors,
        faulty_sensors=faulty_sensors,
        active_anomalies=0,
        active_leaks=0,
        estimated_total_loss_lpm=0.0
    )


@router.get("/topology", response_model=NetworkTopologySchema)
def get_network_topology():
    net = _default_network
    zones = [ZoneSchema(
        zone_id=z.zone_id,
        name=z.name,
        description=z.description,
        target_pressure_bar=z.target_pressure_bar,
        target_flow_lpm=z.target_flow_lpm
    ) for z in net.zones.values()]

    nodes = [NetworkNodeSchema(
        node_id=n.node_id,
        node_type=n.node_type,
        elevation_m=n.elevation_m,
        zone_id=n.zone_id
    ) for n in net.nodes.values()]

    segments = [PipelineSegmentSchema(
        segment_id=s.segment_id,
        source_node=s.source_node,
        destination_node=s.destination_node,
        zone_id=s.zone_id,
        length_m=s.length_m,
        nominal_min_flow=s.nominal_min_flow,
        nominal_max_flow=s.nominal_max_flow,
        nominal_min_pressure=s.nominal_min_pressure,
        nominal_max_pressure=s.nominal_max_pressure
    ) for s in net.segments.values()]

    sensors = [SensorSchema(
        sensor_id=s.sensor_id,
        zone_id=s.zone_id,
        pipeline_segment_id=s.pipeline_segment_id,
        location_node=s.location_node,
        sensor_type=s.sensor_type,
        installation_metadata=s.installation_metadata,
        health_status=s.health_status.value if hasattr(s.health_status, 'value') else str(s.health_status)
    ) for s in net.sensors.values()]

    return NetworkTopologySchema(
        name=net.name,
        zones=zones,
        nodes=nodes,
        segments=segments,
        sensors=sensors
    )
