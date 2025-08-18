from dataclasses import dataclass

@dataclass
class BatteryState:
    soc: float
    voltage: float
    current: float
    temperature: float
    cycle_count: float
    total_ah_throughput: float
    calendar_age: float
    capacity: float
    soh: float
    avg_dod: float = 0.0