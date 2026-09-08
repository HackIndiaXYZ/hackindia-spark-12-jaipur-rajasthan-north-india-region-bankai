from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Zone:
    zone_id: str
    name: str
    description: Optional[str] = None
    target_pressure_bar: float = 4.0
    target_flow_lpm: float = 100.0
