from dataclasses import dataclass

@dataclass
class AgingParameters:
    activation_energy_calendar: float = 36360.0
    activation_energy_cyclic: float = 25000.0 # randomly trying
    gas_constant: float = 8.314
    time_exponent: float = 0.789
    efc_exponent: float = 0.98
    pre_exp_factor_calendar: float = 5.0e-3
    cyclic_factor: float = 2.5