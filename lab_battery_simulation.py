from typing import List
import numpy as np
from aging_model import AgingModel
from data.battery_state import BatteryState
from data.lab_test_condition import LabTestCondition
from data.aging_parameters import AgingParameters


class LabBatterySimulation:
    def __init__(self, aging_model: AgingModel = None):
        self.aging_model = aging_model if aging_model else AgingModel()

    def simulate_lab_test(
        self,
        conditions: List[LabTestCondition],
        battery_capacity_ah: float = 64.0,
        initial_soc: float = None
    ) -> List[BatteryState]:
        start_soc = initial_soc if initial_soc is not None else conditions[0].target_soc

        battery_state = BatteryState(
            soc=start_soc,
            voltage=3.7,
            current=0.0,
            temperature=conditions[0].temperature,
            cycle_count=0.0,
            total_ah_throughput=0.0,
            calendar_age=0.0,
            capacity=battery_capacity_ah,
            soh=100.0
        )

        history = [battery_state]
        soc_history = [start_soc]

        for i, condition in enumerate(conditions[1:], 1):
            prev_condition = conditions[i-1]
            dt = condition.time - prev_condition.time

            battery_state = self._update_lab_battery_state(
                battery_state,
                condition,
                dt,
                battery_capacity_ah
            )
            soc_history.append(battery_state.soc)
            if len(soc_history) > 1000:
                soc_history.pop(0)

            if i % 100 == 0:
                characterization_number = i // 100
                current_dod = condition.dod
                clean_efc = characterization_number * 100 * current_dod
                
                avg_soc = np.mean(soc_history[-100:])

                calendar_loss = self.aging_model.calculate_calendar_aging(
                    condition.time,
                    condition.temperature,
                    avg_soc
                )

                cyclic_loss = self.aging_model.calculate_cyclic_aging(
                    clean_efc,
                    condition.temperature,
                    avg_soc,
                    current_dod
                )

                total_loss = calendar_loss + cyclic_loss
                new_capacity = battery_capacity_ah * (1.0 - total_loss)
                new_soh = (new_capacity / battery_capacity_ah) * 100.0

                battery_state = BatteryState(
                    soc=battery_state.soc,
                    voltage=battery_state.voltage,
                    current=battery_state.current,
                    temperature=battery_state.temperature,
                    cycle_count=clean_efc,  # Use clean EFC
                    total_ah_throughput=battery_state.total_ah_throughput,
                    calendar_age=condition.time / 24.0,
                    capacity=new_capacity,
                    soh=new_soh,
                    avg_dod=current_dod
                )

            history.append(battery_state)
        return history


    def _update_lab_battery_state(
        self,
        state: BatteryState,
        condition: LabTestCondition,
        dt: float,
        capacity_ah: float
    ) -> BatteryState:
        current = condition.c_rate * capacity_ah

        new_soc = condition.target_soc

        throughput = state.total_ah_throughput + abs(current) * dt
        total_efc = throughput / (2.0 * capacity_ah)

        return BatteryState(
            soc=new_soc,
            voltage=64.0,
            current=current,
            temperature=condition.temperature,
            cycle_count=total_efc,
            total_ah_throughput=throughput,
            calendar_age=state.calendar_age,
            capacity=state.capacity,
            soh=state.soh
        )