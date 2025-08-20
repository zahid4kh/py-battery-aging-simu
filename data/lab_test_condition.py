from dataclasses import dataclass


@dataclass
class LabTestCondition:
    time: float
    temperature: float
    target_soc: float
    is_charging: bool
    c_rate: float
    cycle_number: int
