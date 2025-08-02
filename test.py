import numpy as np
from data.aging_parameters import AgingParameters
from utils.utils import celsius_to_kelvin

params = AgingParameters
def calculate_cyclic_aging(efc: float, temp_celsius: float, avg_soc: float, avg_dod: float) -> float:
    if efc <= 0:
        return 0.0
    temp_kelvin = celsius_to_kelvin(temp_celsius)
    temp_term = np.exp(-params.activation_energy_cyclic / (params.gas_constant * temp_kelvin))

    # stress_term = self._calculate_stress_amplitude(avg_soc, avg_dod) using hardcoded DOD&SOC below instead

    dod_stress = 1.0 + 5.0 * avg_dod  # Linear DoD dependency
    soc_stress = 1.0 + 3.0 * (avg_soc - 0.5) ** 2  # Quadratic SoC dependency

    efc_term = efc ** params.efc_exponent
    soc_chemical_term = 3.90e-3 * avg_soc + 0.20  # chemical stress -> linear relationship Equation 4.11

    return params.cyclic_factor * dod_stress * soc_stress * temp_term * efc_term * soc_chemical_term


def _calculate_stress_amplitude(avg_soc: float, avg_dod: float) -> float:
    soc_min = max(0.0, avg_soc - avg_dod / 2.0)
    soc_max = min(1.0, avg_soc + avg_dod / 2.0)
    return _calculate_polynomial(soc_max) - _calculate_polynomial(soc_min)

def _calculate_polynomial(soc: float) -> float:
    coeffs = [2.74e-13, -8.39e-11, 8.38e-9, -2.39e-7, -5.05e-6, 9.70e-5, 0.02, -6.19e-3]
    result = 0.0
    for i, coeff in enumerate(coeffs):
        result += coeff * (soc ** (7 - i))
    return max(0.0, result)