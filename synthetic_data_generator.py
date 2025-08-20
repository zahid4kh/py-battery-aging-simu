import numpy as np
from typing import List, Tuple
from data.lab_test_condition import LabTestCondition


class SyntheticDataGenerator:
    def __init__(self, battery_capacity_ah: float = 3.3):
        self.battery_capacity = battery_capacity_ah

    def generate_cyclic_aging_profile(
        self,
        dod: float,
        soc_avg: float,
        temperature: float,
        c_rate: float,
        target_efc: float,
        time_step_hours: float = 0.1
    ) -> List[LabTestCondition]:
        conditions = []
        current_time = 0.0
        cycle_number = 0

        soc_min = max(0.0, soc_avg - dod/2)
        soc_max = min(1.0, soc_avg + dod/2)

        print(
            f"Test Conditions: DoD={dod*100:.0f}%, SoC_avg={soc_avg*100:.0f}%, T={temperature}°C, C-rate={c_rate}")
        print(f"SOC Window: {soc_min*100:.1f}% - {soc_max*100:.1f}%")

        discharge_time = dod / c_rate
        charge_time = dod / c_rate
        rest_time = 0.1

        cycles_needed = int(target_efc / dod) + 1

        current_soc = soc_max

        for cycle in range(cycles_needed):

            rest_steps = int(rest_time / time_step_hours)
            for _ in range(rest_steps):
                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=current_soc,
                    is_charging=False,
                    c_rate=0.0,
                    cycle_number=cycle
                ))
                current_time += time_step_hours

            discharge_steps = int(discharge_time / time_step_hours)
            for step in range(discharge_steps):
                progress = step / discharge_steps
                target_soc = soc_max - (progress * dod)  # 75% -> 25%

                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=target_soc,
                    is_charging=False,
                    c_rate=c_rate,
                    cycle_number=cycle
                ))
                current_time += time_step_hours

            current_soc = soc_min

            for _ in range(rest_steps):
                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=current_soc,
                    is_charging=False,
                    c_rate=0.0,
                    cycle_number=cycle
                ))
                current_time += time_step_hours

            charge_steps = int(charge_time / time_step_hours)
            for step in range(charge_steps):
                progress = step / charge_steps
                target_soc = soc_min + (progress * dod)

                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=target_soc,
                    is_charging=True,
                    c_rate=-c_rate,
                    cycle_number=cycle
                ))
                current_time += time_step_hours

            current_soc = soc_max
            cycle_number += 1

            if cycle % 100 == 0:
                current_efc = cycle * dod
                print(
                    f"Cycle {cycle}, EFC: {current_efc:.1f}, Time: {current_time:.1f}h")

        print(
            f"Generated {len(conditions)} data points, {cycles_needed} cycles, {current_time:.1f} hours")
        return conditions

    def generate_calendar_aging_profile(
        self,
        soc: float,
        temperature: float,
        duration_days: float
    ) -> List[LabTestCondition]:

        conditions = []
        time_step_hours = 1.0
        total_hours = duration_days * 24
        current_time = 0.0

        while current_time < total_hours:
            conditions.append(LabTestCondition(
                time=current_time,
                temperature=temperature,
                target_soc=soc,
                is_charging=False,
                c_rate=0.0,
                cycle_number=0
            ))
            current_time += time_step_hours

        print(
            f"Generated calendar aging profile: {duration_days} days at {soc*100}% SOC, {temperature}°C")
        return conditions
