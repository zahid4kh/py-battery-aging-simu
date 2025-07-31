import random
from typing import Tuple
from bus_operation_generator import BusOperationGenerator
from bus_simulation import BusSimulation
from data.bus import RouteType, Bus
from data.simulation_scenario import SimulationScenario
from utils.utils import years_to_hours, hours_to_days


class SimulationRunner:
    def __init__(self):
        self.bus_simulation = BusSimulation()
        self.operation_generator = BusOperationGenerator()

    def run_comparison(self, duration_hours: float = None):
        if duration_hours is None:
            duration_hours = years_to_hours(1.0)

        scenarios = [
            SimulationScenario("Cold_Narrow", 10.0, (0.2, 0.8), 0.1, 0.5),
            SimulationScenario("Normal_Narrow", 25.0, (0.2, 0.8), 0.1, 0.5),
            SimulationScenario("Hot_Narrow", 40.0, (0.2, 0.8), 0.1, 0.5),
            SimulationScenario("Normal_Medium", 25.0, (0.3, 0.9), 0.5, 1.0),
            SimulationScenario("Normal_Wide", 25.0, (0.5, 1.0), 0.5, 1.0),
            SimulationScenario("High_DoD", 25.0, (0.2, 0.8), 0.8, 2.0),
            SimulationScenario("High_CRate", 25.0, (0.2, 0.8), 0.5, 2.0)
        ]

        print("Scenario,FinalSoH,CalendarAge,CycleCount,CapacityLoss")

        for scenario in scenarios:
            bus = Bus(
                id="TestBus",
                route_type=RouteType.CITY,
                battery_capacity=300.0,
                initial_soc=(scenario.soc_window[0] + scenario.soc_window[1]) / 2.0,
                stops_per_route=random.randint(15, 34),
                passengers_avg=random.randint(25, 54)
            )

            conditions = self.operation_generator.generate_operating_conditions(
                duration_hours=duration_hours,
                temp_celsius=scenario.temperature
            )

            result = self.bus_simulation.simulate_battery(bus, conditions, scenario.soc_window)
            final_state = result.history[-1]
            capacity_loss = ((bus.battery_capacity - final_state.capacity) / bus.battery_capacity) * 100.0

            print(
                f"{scenario.name},{final_state.soh},{final_state.calendar_age},{final_state.cycle_count},{capacity_loss}")

    def run_single_scenario(
            self,
            duration_hours: float,
            temperature: float = 25.0,
            soc_window: Tuple[float, float] = (0.2, 0.8)
    ):
        bus = Bus(
            id="SingleTestBus",
            route_type=RouteType.CITY,
            battery_capacity=300.0,
            initial_soc=0.8,
            stops_per_route=random.randint(20, 29),
            passengers_avg=random.randint(30, 49)
        )

        conditions = self.operation_generator.generate_operating_conditions(
            duration_hours=duration_hours,
            temp_celsius=temperature
        )

        result = self.bus_simulation.simulate_battery(bus, conditions, soc_window)
        final_state = result.history[-1]

        print("Single Scenario Results:")
        print(f"Duration: {hours_to_days(duration_hours)} days")
        print(f"Temperature: {temperature}°C")
        print(f"SoC Window: {soc_window[0] * 100}% - {soc_window[1] * 100}%")
        print(f"Final SoH: {final_state.soh}%")
        print(f"Calendar Age: {final_state.calendar_age} days")
        print(f"Cycle Count: {final_state.cycle_count}")
        print(f"Capacity Loss: {((bus.battery_capacity - final_state.capacity) / bus.battery_capacity) * 100.0}%")