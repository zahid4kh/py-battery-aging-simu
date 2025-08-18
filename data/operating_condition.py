from dataclasses import dataclass


@dataclass
class OperatingCondition:
    time: float
    ambient_temp: float

    power_consumption_kw: float = 0.0
    available_catenary_power_kw: float = 0.0
    has_catenary: bool = False
    battery_operation_mode: str = "battery_discharging"  # "regenerating", "catenary_powered", "battery_discharging"

    is_charging: bool = False
    is_regenerating: bool = False

    def __post_init__(self):
        self.is_regenerating = (self.battery_operation_mode == "regenerating")
        self.is_charging = (self.battery_operation_mode == "catenary_powered")