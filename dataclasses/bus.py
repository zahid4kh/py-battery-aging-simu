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
    avg_speed: float = 30.0
    route_length: float = 50.0
    overhead_coverage: float = 0.3
    stops_per_route: int = 25
    passengers_avg: int = 40