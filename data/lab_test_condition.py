from dataclasses import dataclass

@dataclass
class LabTestCondition:
    time: float
    temperature: float
    target_soc: float
    is_charging: float
    c_rate: float
    cycle_number: float
    dod: float = 0.0