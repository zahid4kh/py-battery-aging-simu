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

        soc_term = (self.params.gamma_calendar * avg_soc *
                    100 + self.params.sigma_calendar)

        calendar_loss = self.params.pre_exp_factor_calendar * \
            temp_term * soc_term * time_term

        return calendar_loss

    def calculate_cyclic_aging(self, efc: float, temp_celsius: float, avg_soc: float, avg_dod: float) -> float:
        if efc <= 0:
            return 0.0

        sei_loss = self._calculate_sei_loss(
            efc, temp_celsius, avg_soc, avg_dod)
        am_loss = self._calculate_active_material_loss(efc, avg_soc, avg_dod)

        return sei_loss + am_loss

    def _calculate_sei_loss(self, efc: float, temp_celsius: float, avg_soc: float, avg_dod: float) -> float:
        temp_kelvin = celsius_to_kelvin(temp_celsius)
        temp_term = np.exp(-self.params.activation_energy_cyclic /
                           (self.params.gas_constant * temp_kelvin))

        stress_amplitude = self._calculate_stress_amplitude(avg_soc, avg_dod)
        soc_chemical_term = self._calculate_soc_dependency_L(avg_soc)
        efc_term = efc ** self.params.efc_exponent

        sei_loss_percent = self.params.c2 * stress_amplitude * \
                           temp_term * efc_term * soc_chemical_term

        return sei_loss_percent / 100000.0

    def _calculate_soc_dependency_E(self, avg_soc: float) -> float:
        """Exponential SoC dependency (Equation 4.9)"""
        avg_soc_percent = avg_soc * 100
        return self.params.c3 * np.exp(self.params.c4 * avg_soc_percent)

    def _calculate_soc_dependency_S(self, avg_soc: float) -> float:
        """Sigmoidal SoC dependency (Equation 4.10)"""
        avg_soc_percent = avg_soc * 100
        return 1.0 / (1.0 + np.exp(-self.params.c3 * (avg_soc_percent - self.params.c4)))

    def _calculate_soc_dependency_L(self, avg_soc: float) -> float:
        """Linear SoC dependency (Equation 4.11)"""
        avg_soc_percent = avg_soc * 100
        return self.params.c3 * avg_soc_percent + self.params.c4

    def _calculate_active_material_loss(self, efc: float, avg_soc: float, avg_dod: float) -> float:
        if avg_dod <= 0.6:
            return 0.0

        stress_amplitude = self._calculate_stress_amplitude(avg_soc, avg_dod)

        dod_excess = avg_dod - 0.6
        if avg_dod >= 0.8:
            dod_factor = np.exp(dod_excess * 2.0)  # Changed from 8.0 to 2.0
        else:
            dod_factor = dod_excess * 2.0  # Changed from 5.0 to 2.0

        am_loss = self.params.c5 * dod_factor * stress_amplitude * \
                  (efc ** 0.8) * 1.0  # Changed from 5.0 to 1.0

        return max(0.0, am_loss / 1000.0)  # Changed from 100.0 to 1000.0

    def _calculate_stress_amplitude(self, avg_soc: float, avg_dod: float) -> float:
        soc_min = max(0.0, avg_soc - avg_dod / 2.0)
        soc_max = min(1.0, avg_soc + avg_dod / 2.0)

        poly_max = self._calculate_polynomial(soc_max)
        poly_min = self._calculate_polynomial(soc_min)

        result = poly_max - poly_min

        if avg_dod >= 0.99:
            print(
                f"Stress Debug: soc_min={soc_min:.3f}, soc_max={soc_max:.3f}")
            print(
                f"Stress Debug: poly_min={poly_min:.8f}, poly_max={poly_max:.8f}, result={result:.8f}")

        return result

    # Graphite expansion function; Equation 4.6 && Table 4.2
    def _calculate_polynomial(self, soc: float) -> float:
        if soc <= 1.0:
            soc = soc * 100.0

        coeffs = [2.74e-13, -8.39e-11, 8.38e-9,
                  -2.39e-7, -5.05e-6, 9.70e-5, 0.02, -6.19e-3]
        result = 0.0
        for i, coeff in enumerate(coeffs):
            result += coeff * (soc ** (7 - i))

        return max(0.0, result)
