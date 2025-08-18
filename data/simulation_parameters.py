from dataclasses import dataclass


@dataclass
class SimulationParameters:
   
    battery_voltage: float = 360.0

    max_charge_c_rate: float = 1.0
    max_discharge_c_rate: float = 2.0