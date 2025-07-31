from typing import List, Tuple
from aging_model import AgingModel
from parquet_data_loader import RealOperatingCondition
from data.battery_state import BatteryState
from data.bus import Bus


class RealBusSimulation:
    def __init__(self, aging_model: AgingModel = None):
        self.aging_model = aging_model if aging_model else AgingModel()

    def simulate_from_real_data(
            self,
            bus: Bus,
            real_conditions: List[RealOperatingCondition],
            soc_window: Tuple[float, float] = (0.2, 0.8)
    ) -> dict:

        battery_state = BatteryState(
            soc=bus.initial_soc,
            voltage=360.0,
            current=0.0,
            temperature=real_conditions[0].ambient_temp,
            cycle_count=0.0,
            total_ah_throughput=0.0,
            calendar_age=0.0,
            capacity=bus.battery_capacity,
            soh=100.0
        )

        history = [battery_state]
        total_energy_throughput = 0.0
        print(f"Simulating {len(real_conditions)} data points...")

        for i, condition in enumerate(real_conditions[1:], 1):
            prev_condition = real_conditions[i - 1]
            dt_hours = condition.time_hours - prev_condition.time_hours

            battery_state = self._update_battery_from_real_power(
                battery_state,
                condition,
                dt_hours,
                soc_window,
                bus.battery_capacity
            )

            energy_kWh = abs(condition.total_power_kw) * dt_hours
            total_energy_throughput += energy_kWh

            if i % 1000 == 0:
                total_efc = total_energy_throughput / bus.battery_capacity

                recent_start = max(0, i - 1000)
                recent_conditions = real_conditions[recent_start:i]
                recent_history = history[recent_start:i]

                avg_soc = sum(state.soc for state in recent_history) / len(recent_history)
                avg_temp = sum(c.ambient_temp for c in recent_conditions) / len(recent_conditions)
                avg_dod = self._calculate_average_dod(recent_history)

                calendar_loss = self.aging_model.calculate_calendar_aging(
                    condition.time_hours,
                    avg_temp,
                    avg_soc
                )

                cyclic_loss = self.aging_model.calculate_cyclic_aging(
                    total_efc,
                    avg_temp,
                    avg_soc,
                    avg_dod
                )

                total_loss = calendar_loss + cyclic_loss
                total_loss = max(0.0, min(0.8, total_loss))

                new_capacity = bus.battery_capacity * (1.0 - total_loss)
                new_soh = (new_capacity / bus.battery_capacity) * 100.0

                battery_state = BatteryState(
                    soc=battery_state.soc,
                    voltage=battery_state.voltage,
                    current=battery_state.current,
                    temperature=battery_state.temperature,
                    cycle_count=total_efc,
                    total_ah_throughput=total_energy_throughput,
                    calendar_age=condition.time_hours / 24.0,
                    capacity=new_capacity,
                    soh=new_soh,
                    avg_dod=avg_dod
                )

                if i % 5000 == 0:
                    print(f"Progress: {i}/{len(real_conditions)} - SoH: {new_soh:.2f}% - EFC: {total_efc:.1f}")

            history.append(battery_state)

        final_state = history[-1]

        return {
            'final_state': final_state,
            'history': history,
            'total_efc': total_energy_throughput / bus.battery_capacity,
            'total_energy_kWh': total_energy_throughput,
            'duration_days': real_conditions[-1].time_hours / 24.0,
            'capacity_loss_percent': ((bus.battery_capacity - final_state.capacity) / bus.battery_capacity) * 100
        }

    def _update_battery_from_real_power(
            self,
            state: BatteryState,
            condition: RealOperatingCondition,
            dt_hours: float,
            soc_window: Tuple[float, float],
            battery_capacity_kWh: float
    ) -> BatteryState:

        new_soc = state.soc

        if condition.has_overhead_line:
            if state.soc < soc_window[1]:
                net_power = condition.available_charging_kw - condition.total_power_kw
                if net_power > 0:
                    soc_increase = (net_power * dt_hours) / battery_capacity_kWh
                    new_soc = min(soc_window[1], state.soc + soc_increase)
                else:
                    soc_decrease = (abs(net_power) * dt_hours) / battery_capacity_kWh
                    new_soc = max(soc_window[0], state.soc - soc_decrease)
            else:
                new_soc = state.soc
        else:
            soc_decrease = (condition.total_power_kw * dt_hours) / battery_capacity_kWh
            new_soc = max(soc_window[0], state.soc - soc_decrease)

        voltage = 300.0 + (new_soc * 100.0)
        current = (condition.total_power_kw * 1000) / voltage if voltage > 0 else 0  # Convert kW to A

        return BatteryState(
            soc=new_soc,
            voltage=voltage,
            current=current,
            temperature=condition.ambient_temp,
            cycle_count=state.cycle_count,
            total_ah_throughput=state.total_ah_throughput,
            calendar_age=state.calendar_age,
            capacity=state.capacity,
            soh=state.soh
        )

    def _calculate_average_dod(self, history: List[BatteryState]) -> float:
        if len(history) < 2:
            return 0.0
        soc_values = [state.soc for state in history]
        return max(soc_values) - min(soc_values)