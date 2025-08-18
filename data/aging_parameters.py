from dataclasses import dataclass


@dataclass
class AgingParameters:
    activation_energy_calendar: float = 36360.0
    activation_energy_cyclic: float = 36360.0
    gas_constant: float = 8.314
    time_exponent: float = 0.789
    efc_exponent: float = 0.98
    pre_exp_factor_calendar: float = 2.15e4
    cyclic_factor: float = 2.5
