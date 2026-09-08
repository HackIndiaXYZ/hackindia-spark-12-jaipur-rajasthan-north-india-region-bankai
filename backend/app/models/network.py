from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import networkx as nx

from app.models.zone import Zone
from app.models.pipeline import PipelineSegment
from app.models.sensor import Sensor, HealthStatus


@dataclass
class NetworkNode:
    node_id: str
    node_type: str  # "reservoir", "junction", "endpoint"
    elevation_m: float = 0.0
    zone_id: Optional[str] = None


class WaterNetwork:
    """
    Virtual water pipeline network topology model.
    Encapsulates nodes, zones, pipeline segments, sensors, and graph structure.
    """

    def __init__(self, name: str = "AquaSentinel Default Network"):
        self.name = name
        self.zones: Dict[str, Zone] = {}
        self.nodes: Dict[str, NetworkNode] = {}
        self.segments: Dict[str, PipelineSegment] = {}
        self.sensors: Dict[str, Sensor] = {}
        self.graph: nx.DiGraph = nx.DiGraph()

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.zone_id] = zone

    def add_node(self, node: NetworkNode) -> None:
        self.nodes[node.node_id] = node
        self.graph.add_node(
            node.node_id,
            node_type=node.node_type,
            elevation_m=node.elevation_m,
            zone_id=node.zone_id
        )

    def add_segment(self, segment: PipelineSegment) -> None:
        self.segments[segment.segment_id] = segment
        self.graph.add_edge(
            segment.source_node,
            segment.destination_node,
            segment_id=segment.segment_id,
            zone_id=segment.zone_id,
            length_m=segment.length_m,
            nominal_flow=segment.nominal_flow_range,
            nominal_pressure=segment.nominal_pressure_range
        )

    def add_sensor(self, sensor: Sensor) -> None:
        self.sensors[sensor.sensor_id] = sensor

    def get_sensors_by_zone(self, zone_id: str) -> List[Sensor]:
        return [s for s in self.sensors.values() if s.zone_id == zone_id]

    def get_segments_by_zone(self, zone_id: str) -> List[PipelineSegment]:
        return [seg for seg in self.segments.values() if seg.zone_id == zone_id]

    def get_candidate_segments(self, source_sensor_id: str, dest_sensor_id: str) -> List[PipelineSegment]:
        """
        Finds all pipeline segments on graph path between two sensor nodes.
        """
        if source_sensor_id not in self.sensors or dest_sensor_id not in self.sensors:
            return []

        s1 = self.sensors[source_sensor_id]
        s2 = self.sensors[dest_sensor_id]

        try:
            # Simple shortest path on directed or undirected graph representation
            undirected_g = self.graph.to_undirected()
            path_nodes = nx.shortest_path(undirected_g, source=s1.location_node, target=s2.location_node)
            candidate_segments = []
            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i+1]
                for seg in self.segments.values():
                    if (seg.source_node == u and seg.destination_node == v) or \
                       (seg.source_node == v and seg.destination_node == u):
                        candidate_segments.append(seg)
            return candidate_segments
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    @classmethod
    def create_default_network(cls) -> "WaterNetwork":
        """
        Creates canonical hackathon network layout:
        Reservoir
        |
        +---- A1 ---- A2 ---- A3
        |
        +---- B1 ---- B2 ---- B3 ---- B4
        |
        +---- C1 ---- C2 ---- C3
        """
        net = cls(name="AquaSentinel Synthetic Network")

        # 1. Add Zones
        zone_a = Zone("Zone_A", "Zone A - Residential District", "Northern residential zone", 4.2, 80.0)
        zone_b = Zone("Zone_B", "Zone B - Industrial Hub", "Central industrial pipeline zone", 4.5, 150.0)
        zone_c = Zone("Zone_C", "Zone C - Commercial Center", "Southern commercial district", 3.8, 100.0)

        for z in [zone_a, zone_b, zone_c]:
            net.add_zone(z)

        # 2. Add Reservoir
        net.add_node(NetworkNode("Reservoir", "reservoir", elevation_m=50.0))

        # 3. Add Nodes
        nodes_def = [
            # Zone A
            ("A1", "junction", 35.0, "Zone_A"),
            ("A2", "junction", 30.0, "Zone_A"),
            ("A3", "endpoint", 25.0, "Zone_A"),
            # Zone B
            ("B1", "junction", 40.0, "Zone_B"),
            ("B2", "junction", 38.0, "Zone_B"),
            ("B3", "junction", 35.0, "Zone_B"),
            ("B4", "endpoint", 32.0, "Zone_B"),
            # Zone C
            ("C1", "junction", 20.0, "Zone_C"),
            ("C2", "junction", 18.0, "Zone_C"),
            ("C3", "endpoint", 15.0, "Zone_C"),
        ]
        for n_id, n_type, elev, z_id in nodes_def:
            net.add_node(NetworkNode(n_id, n_type, elev, z_id))

        # 4. Add Pipeline Segments
        segments_def = [
            # Reservoir connections
            ("R-A1", "Reservoir", "A1", "Zone_A", 150.0, (40.0, 100.0), (4.0, 5.0)),
            ("R-B1", "Reservoir", "B1", "Zone_B", 200.0, (80.0, 200.0), (4.2, 5.2)),
            ("R-C1", "Reservoir", "C1", "Zone_C", 180.0, (50.0, 120.0), (3.5, 4.5)),
            # Zone A segments
            ("A1-A2", "A1", "A2", "Zone_A", 120.0, (35.0, 90.0), (3.8, 4.8)),
            ("A2-A3", "A2", "A3", "Zone_A", 100.0, (30.0, 80.0), (3.5, 4.5)),
            # Zone B segments
            ("B1-B2", "B1", "B2", "Zone_B", 250.0, (75.0, 190.0), (4.0, 5.0)),
            ("B2-B3", "B2", "B3", "Zone_B", 220.0, (70.0, 180.0), (3.8, 4.8)),
            ("B3-B4", "B3", "B4", "Zone_B", 180.0, (60.0, 160.0), (3.5, 4.5)),
            # Zone C segments
            ("C1-C2", "C1", "C2", "Zone_C", 140.0, (45.0, 110.0), (3.4, 4.4)),
            ("C2-C3", "C2", "C3", "Zone_C", 110.0, (40.0, 100.0), (3.2, 4.2)),
        ]

        for s_id, src, dst, z_id, l_m, flow_r, pres_r in segments_def:
            net.add_segment(PipelineSegment(s_id, src, dst, z_id, l_m, flow_r, pres_r))

        # 5. Add Sensors
        sensors_def = [
            ("A1", "Zone_A", "R-A1", "A1"),
            ("A2", "Zone_A", "A1-A2", "A2"),
            ("A3", "Zone_A", "A2-A3", "A3"),
            ("B1", "Zone_B", "R-B1", "B1"),
            ("B2", "Zone_B", "B1-B2", "B2"),
            ("B3", "Zone_B", "B2-B3", "B3"),
            ("B4", "Zone_B", "B3-B4", "B4"),
            ("C1", "Zone_C", "R-C1", "C1"),
            ("C2", "Zone_C", "C1-C2", "C2"),
            ("C3", "Zone_C", "C2-C3", "C3"),
        ]

        for s_id, z_id, p_seg_id, loc in sensors_def:
            net.add_sensor(Sensor(
                sensor_id=s_id,
                zone_id=z_id,
                pipeline_segment_id=p_seg_id,
                location_node=loc,
                sensor_type="multi-sensor",
                installation_metadata={
                    "installation_date": "2024-01-15",
                    "model": "AquaSense-Pro-v2",
                    "firmware_version": "2.1.0"
                },
                health_status=HealthStatus.HEALTHY
            ))

        return net
