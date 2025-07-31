from typing import Tuple, List
from aging_model import AgingModel
from data.battery_state import BatteryState
from data.bus import Bus
from data.operating_condition import OperatingCondition
from data.simulation_result import SimulationResult
from utils.utils import hours_to_days


class BusSimulation:
    def __init__(self, aging_model: AgingModel = None):
        self.aging_model = aging_model if aging_model else AgingModel()

    def simulate_battery(
            self,
            bus: Bus,
            conditions: List[OperatingCondition],
            soc_window: Tuple[float, float] = (0.2, 0.8)
    ) -> SimulationResult:
        battery_state = BatteryState(
            soc=bus.initial_soc,
            voltage=360.0,
            current=0.0,
            temperature=conditions[0].ambient_temp,
            cycle_count=0.0,
            total_ah_throughput=0.0,
            calendar_age=0.0,
            capacity=bus.battery_capacity,
            soh=100.0
        )

        history = [battery_state]
        total_efc = 0.0
        avg_soc = bus.initial_soc
        avg_dod = 0.0

        for i in range(1, len(conditions)):
            condition = conditions[i]
            prev_condition = conditions[i - 1]
            dt = condition.time - prev_condition.time

            battery_state = self._update_battery_state(
                battery_state,
                condition,
                dt,
                soc_window,
                bus.battery_capacity
            )

            if i % 100 == 0:
                recent_history = history[-100:] if len(history) >= 100 else history
                avg_soc = sum(state.soc for state in recent_history) / len(recent_history)
                avg_dod = self._calculate_average_dod(recent_history)
                total_efc += avg_dod / 2.0

                calendar_loss = self.aging_model.calculate_calendar_aging(
                    condition.time,
                    condition.ambient_temp,
                    avg_soc
                )

                cyclic_loss = self.aging_model.calculate_cyclic_aging(
                    total_efc,
                    condition.ambient_temp,
                    avg_soc,
                    avg_dod
                )

                total_loss = calendar_loss + cyclic_loss
                new_capacity = bus.battery_capacity * (1.0 - total_loss)
                new_soh = (new_capacity / bus.battery_capacity) * 100.0

                battery_state = BatteryState(
                    soc=battery_state.soc,
                    voltage=battery_state.voltage,
                    current=battery_state.current,
                    temperature=battery_state.temperature,
                    cycle_count=total_efc,
                    total_ah_throughput=battery_state.total_ah_throughput,
                    calendar_age=hours_to_days(condition.time),
                    capacity=new_capacity,
                    soh=new_soh,
                    avg_dod=avg_dod
                )

            history.append(battery_state)

        return SimulationResult(bus, history, conditions)

    def _update_battery_state(
            self,
            state: BatteryState,
            condition: OperatingCondition,
            dt: float,
            soc_window: Tuple[float, float],
            nominal_capacity: float
    ) -> BatteryState:
        new_soc = state.soc
        current = 0.0

        if condition.is_charging and state.soc < soc_window[1]:
            current = -100.0
            new_soc = min(soc_window[1], state.soc + (abs(current) * dt / nominal_capacity))
        elif condition.is_regenerating and state.soc < soc_window[1]:
            current = -50.0
            new_soc = min(soc_window[1], state.soc + (abs(current) * dt / nominal_capacity))
        elif not condition.is_charging:
            current = 80.0 + condition.passengers * 1.5
            new_soc = max(soc_window[0], state.soc - (current * dt / nominal_capacity))

        voltage = 300.0 + (new_soc * 100.0)
        throughput = state.total_ah_throughput + abs(current) * dt

        return BatteryState(
            soc=new_soc,
            voltage=voltage,
            current=current,
            temperature=condition.ambient_temp,
            cycle_count=state.cycle_count,
            total_ah_throughput=throughput,
            calendar_age=state.calendar_age,
            capacity=state.capacity,
            soh=state.soh
        )

    def _calculate_average_dod(self, history: List[BatteryState]) -> float:
        if len(history) < 2:
            return 0.0
        soc_values = [state.soc for state in history]
        max_soc = max(soc_values)
        min_soc = min(soc_values)
        return max_soc - min_soc