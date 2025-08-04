import random
from typing import List
from data.operating_condition import OperatingCondition
from data.simulation_parameters import SimulationParameters
import numpy as np

class BusOperationGenerator:
    def __init__(self, sim_params: SimulationParameters = None):
        self.sim_params = sim_params if sim_params else SimulationParameters()
        
    def generate_operating_conditions(
            self,
            duration_hours: float,
            time_step_hours: float = 0.1,
            temp_celsius: float = 25.0,
            soc_update_callback = None
    ) -> List[OperatingCondition]:
        conditions = []
        current_time = 0.0

        while current_time <= duration_hours:
            # temp default if there is no param passed in callback
            current_soc = 0.5
            if soc_update_callback:
                current_soc = soc_update_callback()


            is_charging = self._should_charge_overhead(current_soc=current_soc)
            is_regenerating = self._should_regen_brake(current_soc=current_soc)

            condition = OperatingCondition(
                time=current_time,
                ambient_temp=temp_celsius,
                is_charging=is_charging,
                is_regenerating=is_regenerating
            )
            
            conditions.append(condition)
            current_time += time_step_hours

        return conditions
    
    def _should_charge_overhead(self, current_soc: float) -> bool:
        if current_soc < self.sim_params.charging_soc_threshold:
            # higher probability of overhead charging when SOC is low
            probability = self.sim_params.overhead_coverage * 1.5
        else:
            # lower probability when SOC is not risky
            probability = self.sim_params.overhead_coverage * 0.5

        return np.random.random() < probability
    
    def _should_regen_brake(self, current_soc: float) -> bool:
        if current_soc > self.sim_params.regen_soc_limit:
            return False
        
        return np.random.random() < self.sim_params.regen_probability