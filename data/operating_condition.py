from dataclasses import dataclass

@dataclass
class OperatingCondition:
    time: float
    ambient_temp: float
    is_charging: bool
    is_regenerating: bool