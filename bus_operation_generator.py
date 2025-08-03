import random
from typing import List
from data.operating_condition import OperatingCondition

class BusOperationGenerator:
    def generate_operating_conditions(
            self,
            duration_hours: float,
            time_step_hours: float = 0.1,
            temp_celsius: float = 25.0,
            overhead_coverage: float = 0.3
    ) -> List[OperatingCondition]:
        conditions = []
        current_time = 0.0

        while current_time < duration_hours:
            is_charging = random.random() < overhead_coverage
            is_regenerating = not is_charging and random.random() < 0.2

            conditions.append(OperatingCondition(
                time=current_time,
                ambient_temp=temp_celsius,
                is_charging=is_charging,
                is_regenerating=is_regenerating
            ))
            print("Is charging?", is_charging)
            print("Is regenerating?", is_regenerating)

            current_time += time_step_hours

        return conditions