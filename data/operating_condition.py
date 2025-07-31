from dataclasses import dataclass

@dataclass
class OperatingCondition:
    time: float
    speed: float
    acceleration: float
    gradient: float
    passengers: int
    ambient_temp: float
    is_charging: bool
    is_regenerating: bool