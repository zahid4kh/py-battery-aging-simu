from dataclasses import dataclass
from typing import Tuple

@dataclass
class SimulationScenario:
    name: str
    temperature: float
    soc_window: Tuple[float, float]
    target_dod: float
    c_rate: float