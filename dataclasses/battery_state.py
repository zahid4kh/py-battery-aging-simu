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
    cycle_start_soc: float = 0.0
    is_in_discharge: bool = False
    completed_cycles: int = 0