from dataclasses import dataclass


@dataclass
class AgingParameters:
    activation_energy_calendar: float = 36360.0
    gas_constant: float = 8.314
    time_exponent: float = 0.789
    pre_exp_factor_calendar: float = 2.15e4
    gamma_calendar: float = 1.19e-4
    sigma_calendar: float = 0.01

    activation_energy_cyclic: float = 36360.0
    efc_exponent: float = 0.98
    c2: float = 9.31e4  # cyclic factor
    c3: float = 3.90e-3
    c4: float = 0.20
    c5: float = 4.00e-3
    c6: float = 34.50e-3
    m: float = 1.23
