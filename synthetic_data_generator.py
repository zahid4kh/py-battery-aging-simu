import numpy as np
from typing import List
from data.lab_test_condition import LabTestCondition


class SyntheticDataGenerator:
    def __init__(self, battery_capacity_ah: float = 3.3):
        self.battery_capacity = battery_capacity_ah

    def generate_cyclic_aging_profile(
            self,
            dod: float,
            soc_avg: float,
            c_rate: float,
            temperature: float,
            target_efc: float,
            time_step_hours: float = 0.1
    ) -> List[LabTestCondition]:

        conditions = []
        current_time = 0.0
        cycle_number = 0

        soc_min = max(0.0, soc_avg - dod / 2)
        soc_max = min(1.0, soc_avg + dod / 2)

        print(f"Krupp Cyclic: DoD={dod * 100:.0f}%, ØSoC={soc_avg * 100:.0f}%, C-rate={c_rate}, T={temperature}°C")
        print(f"SOC Window: {soc_min * 100:.1f}% - {soc_max * 100:.1f}%")

        # 4.4.4: preconditioning (5 cycles at 1C)
        print("Adding preconditioning: 5 cycles at 1C")
        current_time = self._add_preconditioning(conditions, current_time, temperature, time_step_hours)

        # 4.4.4: Simple cycling times based on C-rate
        discharge_time = dod / c_rate
        charge_time = dod / c_rate
        cycles_needed = int(target_efc / dod) + 1

        current_soc = soc_max

        for cycle in range(cycles_needed):

            # PHASE 1: DISCHARGE at specified C-rate
            discharge_steps = int(discharge_time / time_step_hours)
            for step in range(discharge_steps):
                progress = step / discharge_steps
                target_soc = soc_max - (progress * dod)

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

            # PHASE 2: CHARGE at specified C-rate
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

            # 4.4.4: Characterization every 100 cycles
            if cycle > 0 and cycle % 100 == 0:
                print(f"Adding characterization at cycle {cycle}")
                current_time = self._add_cyclic_characterization(
                    conditions, current_time, temperature, time_step_hours, cycle, current_soc
                )

            if cycle % 50 == 0:
                current_efc = cycle * dod
                print(f"Cycle {cycle}, EFC: {current_efc:.1f}, Time: {current_time:.1f}h")

        print(f"Generated {len(conditions)} conditions, {cycles_needed} cycles")
        return conditions

    def _add_preconditioning(self, conditions, current_time, temperature, time_step_hours):
        """5 preconditioning cycles at 1C (4.4.4)"""

        for precond_cycle in range(5):
            discharge_time = 1.0
            discharge_steps = int(discharge_time / time_step_hours)
            for step in range(discharge_steps):
                progress = step / discharge_steps
                target_soc = 1.0 - progress  # 100% → 0%

                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=target_soc,
                    is_charging=False,
                    c_rate=1.0,
                    cycle_number=-1
                ))
                current_time += time_step_hours

            charge_steps = int(discharge_time / time_step_hours)
            for step in range(charge_steps):
                progress = step / charge_steps
                target_soc = progress  # 0% → 100%

                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=target_soc,
                    is_charging=True,
                    c_rate=-1.0,
                    cycle_number=-1
                ))
                current_time += time_step_hours

        return current_time

    def _add_cyclic_characterization(self, conditions, current_time, temperature, time_step_hours, cycle_num, current_soc):
        """Subchapter 4.4.4 characterization"""
        # Capacity measurement (CC charge 1C + CV + CC discharge 1C)
        # Repeated twice with 30-min rests

        start_soc = current_soc

        for char_cycle in range(2):
            # CC charge to 100%
            if start_soc < 1.0:
                charge_range = 1.0 - start_soc
                charge_time = charge_range / 1.0
                charge_steps = int(charge_time / time_step_hours)

                for step in range(charge_steps):
                    progress = step / charge_steps
                    target_soc = start_soc + (progress * charge_range)

                    conditions.append(LabTestCondition(
                        time=current_time,
                        temperature=temperature,
                        target_soc=target_soc,
                        is_charging=True,
                        c_rate=-1.0,
                        cycle_number=cycle_num
                    ))
                    current_time += time_step_hours

            # CV phase until 1/20C
            cv_time = 0.5
            cv_steps = int(cv_time / time_step_hours)
            for _ in range(cv_steps):
                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=1.0,
                    is_charging=True,
                    c_rate=-0.05,
                    cycle_number=cycle_num
                ))
                current_time += time_step_hours

            # 30-minute rest
            rest_time = 0.5
            rest_steps = int(rest_time / time_step_hours)
            for _ in range(rest_steps):
                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=1.0,
                    is_charging=False,
                    c_rate=0.0,
                    cycle_number=cycle_num
                ))
                current_time += time_step_hours

            # CC discharge at 1C
            discharge_1c_time = 1.0
            discharge_steps = int(discharge_1c_time / time_step_hours)
            for step in range(discharge_steps):
                progress = step / discharge_steps
                target_soc = 1.0 - (progress * 1.0)

                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=target_soc,
                    is_charging=False,
                    c_rate=1.0,
                    cycle_number=cycle_num
                ))
                current_time += time_step_hours

            # 30-minute rest
            for _ in range(rest_steps):
                conditions.append(LabTestCondition(
                    time=current_time,
                    temperature=temperature,
                    target_soc=0.0,
                    is_charging=False,
                    c_rate=0.0,
                    cycle_number=cycle_num
                ))
                current_time += time_step_hours

        return current_time

    def generate_calendar_aging_profile(
            self,
            soc: float,
            temperature: float,
            duration_days: float
    ) -> List[LabTestCondition]:
        """ Calendar aging with 3.2.4 characterization"""

        conditions = []
        current_time = 0.0
        time_step_hours = 1.0

        current_time = self._add_calendar_characterization(
            conditions, current_time, temperature, 0.1
        )

        characterization_interval_hours = duration_days * 24 / 4
        next_characterization = characterization_interval_hours

        total_hours = duration_days * 24

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

            if current_time >= next_characterization and current_time < total_hours - 24:
                print(f"Adding calendar characterization at {current_time / 24:.1f} days")
                current_time = self._add_calendar_characterization(
                    conditions, current_time, temperature, 0.1
                )
                next_characterization += characterization_interval_hours

        print(f"Generated calendar aging: {duration_days} days at {soc * 100}% SOC, {temperature}°C")
        return conditions

    def _add_calendar_characterization(self, conditions, current_time, temperature, time_step_hours):
        """Subchapter 3.2.4 calendar aging characterization"""

        # Capacity measurement + HPPC test + C/10 discharge
        # CC charge at 1C to 4.2V
        charge_time = 1.0
        charge_steps = int(charge_time / time_step_hours)
        for step in range(charge_steps):
            progress = step / charge_steps
            target_soc = 0.5 + (progress * 0.5)

            conditions.append(LabTestCondition(
                time=current_time,
                temperature=temperature,
                target_soc=target_soc,
                is_charging=True,
                c_rate=-1.0,
                cycle_number=0
            ))
            current_time += time_step_hours

        # CV phase
        cv_time = 0.5
        cv_steps = int(cv_time / time_step_hours)
        for _ in range(cv_steps):
            conditions.append(LabTestCondition(
                time=current_time,
                temperature=temperature,
                target_soc=1.0,
                is_charging=True,
                c_rate=-0.05,
                cycle_number=0
            ))
            current_time += time_step_hours

        # 30-minute rest
        rest_time = 0.5
        rest_steps = int(rest_time / time_step_hours)
        for _ in range(rest_steps):
            conditions.append(LabTestCondition(
                time=current_time,
                temperature=temperature,
                target_soc=1.0,
                is_charging=False,
                c_rate=0.0,
                cycle_number=0
            ))
            current_time += time_step_hours

        # CC discharge at 1C
        discharge_time = 1.0
        discharge_steps = int(discharge_time / time_step_hours)
        for step in range(discharge_steps):
            progress = step / discharge_steps
            target_soc = 1.0 - (progress * 1.0)

            conditions.append(LabTestCondition(
                time=current_time,
                temperature=temperature,
                target_soc=target_soc,
                is_charging=False,
                c_rate=1.0,
                cycle_number=0
            ))
            current_time += time_step_hours

        # 30-minute rest
        for _ in range(rest_steps):
            conditions.append(LabTestCondition(
                time=current_time,
                temperature=temperature,
                target_soc=0.0,
                is_charging=False,
                c_rate=0.0,
                cycle_number=0
            ))
            current_time += time_step_hours

        return current_time