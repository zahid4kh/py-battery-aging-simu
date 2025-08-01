from typing import Tuple, List

import pandas as pd

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
            soc_window: Tuple[float, float] = (0.2, 0.8),
            save_interval_hours: float = 1.0 # saving every hour
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
        detailed_data = []

        soc_history_for_dod = []
        last_save_time = 0.0

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

            soc_history_for_dod.append(battery_state.soc)
            if len(soc_history_for_dod) > 1000:
                soc_history_for_dod.pop(0)

            if i % 100 == 0:
                current_dod = self._calculate_dod_from_soc_history(soc_history_for_dod)

                recent_history = history[-100:] if len(history) >= 100 else history
                avg_soc = sum(state.soc for state in recent_history) / len(recent_history)

                total_efc = battery_state.total_ah_throughput / (2.0 * bus.battery_capacity)

                calendar_loss = self.aging_model.calculate_calendar_aging(
                    condition.time,
                    condition.ambient_temp,
                    avg_soc
                )

                cyclic_loss = self.aging_model.calculate_cyclic_aging(
                    total_efc,
                    condition.ambient_temp,
                    avg_soc,
                    current_dod
                )

                total_loss_fraction = calendar_loss + cyclic_loss
                new_capacity = bus.battery_capacity * (1.0 - total_loss_fraction)
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
                    avg_dod=current_dod
                )

            if condition.time - last_save_time >= save_interval_hours:
                current_dod = self._calculate_dod_from_soc_history(soc_history_for_dod)

                detailed_data.append({
                    'time_hours': condition.time,
                    'time_days': hours_to_days(condition.time),
                    'soc': battery_state.soc,
                    'soh': battery_state.soh,
                    'capacity': battery_state.capacity,
                    'current': battery_state.current,
                    'temperature': battery_state.temperature,
                    'total_ah_throughput': battery_state.total_ah_throughput,
                    'efc': battery_state.cycle_count,
                    'current_dod': current_dod,  # Current DoD at this time
                    'calendar_age_days': battery_state.calendar_age,
                    'calendar_loss': self.aging_model.calculate_calendar_aging(
                        condition.time, condition.ambient_temp, battery_state.soc),
                    'cyclic_loss': self.aging_model.calculate_cyclic_aging(
                        battery_state.cycle_count, condition.ambient_temp,
                        battery_state.soc, current_dod) if battery_state.cycle_count > 0 else 0.0
                })
                last_save_time = condition.time

            history.append(battery_state)

        self._save_detailed_data(detailed_data, bus.id)

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

    def _calculate_dod_from_soc_history(self, soc_history: List[float]) -> float:
        if len(soc_history) < 10:  # at least 10 data points
            return 0.0

        max_soc = max(soc_history)
        min_soc = min(soc_history)
        dod = max_soc - min_soc

        return max(0.0, dod)

    def _save_detailed_data(self, data: List[dict], bus_id: str):
        """Save detailed simulation data to CSV"""
        if data:
            df = pd.DataFrame(data)
            filename = f"simulation_detailed_{bus_id}.csv"
            df.to_csv(filename, index=False)
            print(f"Detailed data saved to {filename} with {len(data)} records")