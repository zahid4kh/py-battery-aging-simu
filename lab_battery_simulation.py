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
        battery_capacity_ah: float = 3.3,
        initial_soc: float = None
    ) -> List[BatteryState]:
        battery_state = BatteryState(
            soc=initial_soc,
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
        soc_history = [initial_soc]

        print(f"Starting lab simulation with {len(conditions)} conditions...")

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
                current_dod = self._calculate_dod_from_soc_history(soc_history)
                avg_soc = np.mean(soc_history[-100:])

                total_efc = battery_state.total_ah_throughput / \
                    (2.0 * battery_capacity_ah)

                calendar_loss = self.aging_model.calculate_calendar_aging(
                    condition.time,
                    condition.temperature,
                    avg_soc
                )

                cyclic_loss = self.aging_model.calculate_cyclic_aging(
                    total_efc,
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
                    cycle_count=total_efc,
                    total_ah_throughput=battery_state.total_ah_throughput,
                    calendar_age=condition.time / 24.0,
                    capacity=new_capacity,
                    soh=new_soh,
                    avg_dod=current_dod
                )

            history.append(battery_state)

            if i % 1000 == 0:
                print(
                    f"Step {i}/{len(conditions)}, EFC: {battery_state.cycle_count:.1f}, SOH: {battery_state.soh:.2f}%")

        print(
            f"Simulation complete! Final SOH: {history[-1].soh:.2f}%, EFC: {history[-1].cycle_count:.1f}")
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

        return BatteryState(
            soc=new_soc,
            voltage=3.7,
            current=current,
            temperature=condition.temperature,
            cycle_count=state.cycle_count,
            total_ah_throughput=throughput,
            calendar_age=state.calendar_age,
            capacity=state.capacity,
            soh=state.soh
        )

    def _calculate_dod_from_soc_history(self, soc_history: List[float]) -> float:
        if len(soc_history) < 10:
            return 0.0

        cycles = []
        in_discharge = False
        cycle_start_soc = None

        for i in range(1, len(soc_history)):
            current_soc = soc_history[i]
            prev_soc = soc_history[i-1]

            if not in_discharge and current_soc < prev_soc:
                in_discharge = True
                cycle_start_soc = prev_soc  # where dicharge started

            elif in_discharge and current_soc >= prev_soc:
                if cycle_start_soc is not None:
                    cycle_dod = cycle_start_soc - prev_soc
                    if cycle_dod > 0.01:
                        cycles.append(cycle_dod)
                in_discharge = False
                cycle_start_soc = None

        if in_discharge and cycle_start_soc is not None:
            final_dod = cycle_start_soc - soc_history[-1]
            if final_dod > 0.01:
                cycles.append(final_dod)

        return np.mean(cycles) if cycles else 0.0
