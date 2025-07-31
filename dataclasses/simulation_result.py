from dataclasses import dataclass
from typing import List
from bus import Bus
from battery_state import BatteryState
from operating_condition import OperatingCondition

@dataclass
class SimulationResult:
    bus: Bus
    history: List[BatteryState]
    conditions: List[OperatingCondition]