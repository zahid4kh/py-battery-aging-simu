from dataclasses import dataclass
from enum import Enum

class RouteType(Enum):
    CITY = "CITY"
    SUBURBAN = "SUBURBAN"
    EXPRESS = "EXPRESS"

@dataclass
class Bus:
    id: str
    route_type: RouteType
    battery_capacity: float = 300.0
    initial_soc: float = 0.9
    overhead_coverage: float = 0.3