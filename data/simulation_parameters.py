from dataclasses import dataclass
from typing import Dict

@dataclass
class SimulationParameters:
    charging_c_rate: float = 0.5
    regen_c_rate: float = 0.2
    discharge_c_rate: float = 0.3

    overhead_coverage: float = 0.3
    regen_probability: float = 0.1

    charging_soc_threshold: float = 0.4
    regen_soc_limit: float = 0.85