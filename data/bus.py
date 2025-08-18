from dataclasses import dataclass
from enum import Enum


@dataclass
class Bus:
    id: str
    battery_capacity: float = 400.0
    initial_soc: float = 0.7
