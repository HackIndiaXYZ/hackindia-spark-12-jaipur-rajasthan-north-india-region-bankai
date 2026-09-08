from dataclasses import dataclass
from typing import Tuple

@dataclass
class PipelineSegment:
    segment_id: str
    source_node: str
    destination_node: str
    zone_id: str
    length_m: float = 100.0
    nominal_flow_range: Tuple[float, float] = (50.0, 150.0)
    nominal_pressure_range: Tuple[float, float] = (3.0, 5.0)

    @property
    def nominal_min_flow(self) -> float:
        return self.nominal_flow_range[0]

    @property
    def nominal_max_flow(self) -> float:
        return self.nominal_flow_range[1]

    @property
    def nominal_min_pressure(self) -> float:
        return self.nominal_pressure_range[0]

    @property
    def nominal_max_pressure(self) -> float:
        return self.nominal_pressure_range[1]
