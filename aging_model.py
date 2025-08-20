import numpy as np
from data.aging_parameters import AgingParameters
from utils.utils import celsius_to_kelvin, hours_to_days


class AgingModel:
    def __init__(self, params: AgingParameters = None):
        self.params = params if params else AgingParameters()

    def calculate_calendar_aging(self, time_hours: float, temp_celsius: float, avg_soc: float) -> float:
        temp_kelvin = celsius_to_kelvin(temp_celsius)
        time_days = hours_to_days(time_hours)

        temp_term = np.exp(-self.params.activation_energy_calendar /
                           (self.params.gas_constant * temp_kelvin))

        time_term = time_days ** self.params.time_exponent

        soc_term = (self.params.gamma_calendar * avg_soc +
                    self.params.sigma_calendar)

        return self.params.pre_exp_factor_calendar * temp_term * soc_term * time_term

    def calculate_cyclic_aging(self, efc: float, temp_celsius: float, avg_soc: float, avg_dod: float) -> float:
        if efc <= 0:
            return 0.0

        temp_kelvin = celsius_to_kelvin(temp_celsius)
        temp_term = np.exp(-self.params.activation_energy_cyclic /
                           (self.params.gas_constant * temp_kelvin))

        sei_loss = self._calculate_sei_loss(efc, temp_kelvin, avg_soc, avg_dod)

        return sei_loss  # for now, returning only SEI loss without Active Material loss

    def _calculate_sei_loss(self, efc: float, temp_kelvin: float, avg_soc: float, avg_dod: float) -> float:
        temp_term = np.exp(-self.params.activation_energy_cyclic /
                           (self.params.gas_constant * temp_kelvin))

        stress_amplitude = self._calculate_stress_amplitude(
            avg_soc, avg_dod)

        soc_chemical_term = self.params.c3 * avg_soc + self.params.c4

        efc_term = efc ** self.params.efc_exponent

        return self.params.c2 * stress_amplitude * temp_term * efc_term * soc_chemical_term  # Equation 4.8

    def _calculate_stress_amplitude(self, avg_soc: float, avg_dod: float) -> float:
        soc_min = max(0.0, avg_soc - avg_dod / 2.0)
        soc_max = min(1.0, avg_soc + avg_dod / 2.0)
        return self._calculate_polynomial(soc_max) - self._calculate_polynomial(soc_min)

    # Graphite expansion function; Equation 4.6 && Table 4.2
    def _calculate_polynomial(self, soc: float) -> float:
        coeffs = [2.74e-13, -8.39e-11, 8.38e-9,
                  -2.39e-7, -5.05e-6, 9.70e-5, 0.02, -6.19e-3]
        result = 0.0
        for i, coeff in enumerate(coeffs):
            result += coeff * (soc ** (7 - i))
        return max(0.0, result)
