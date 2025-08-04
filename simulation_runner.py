from typing import Tuple
from bus_operation_generator import BusOperationGenerator
from bus_simulation import BusSimulation
from data.bus import RouteType, Bus
from data.simulation_result import SimulationResult
from data.simulation_parameters import SimulationParameters
from utils.utils import days_to_hours


class SimulationRunner:
    def __init__(self):
        self.bus_simulation = None
        self.operation_generator = None

    def run_simulation(
            self,
            duration_days: float = 30.0,  # default 30 days
            temperature: float = 25.0,
            soc_window: Tuple[float, float] = (0.3, 0.9),
            sim_params: SimulationParameters = None,
            bus_id: str = "TrolleyBus_001"
    ) -> SimulationResult:
        duration_hours = days_to_hours(duration_days)

        if sim_params is None:
            sim_params = SimulationParameters()

        self.bus_simulation = BusSimulation(sim_params=sim_params)
        self.operation_generator = BusOperationGenerator(sim_params=sim_params)

        bus = Bus(
            id=bus_id,
            route_type=RouteType.CITY,
            battery_capacity=400.0,  # 400 Ah trolleybus battery
            initial_soc=0.5,  # Start at 50% charge
        )

        print(f"=== Trolleybus Battery Aging Simulation ===")
        print(f"Bus ID: {bus_id}")
        print(f"Duration: {duration_days} days ({duration_hours} hours)")
        print(f"Temperature: {temperature}°C")
        print(f"SoC Window: {soc_window[0] * 100}% - {soc_window[1] * 100}%")
        print(f"Battery Capacity: {bus.battery_capacity} Ah")
        print(f"C-rates: Charge={sim_params.charging_c_rate:.1f}C, Regen={sim_params.regen_c_rate:.1f}C, Discharge={sim_params.discharge_c_rate:.1f}C")
        print(f"Overhead Coverage: {sim_params.overhead_coverage*100:.1f}%")
        print(f"Charging SOC Threshold: {sim_params.charging_soc_threshold*100:.1f}%")
        print()

        # operating conditions
        conditions = self.operation_generator.generate_operating_conditions(
            duration_hours=duration_hours,
            temp_celsius=temperature,
            time_step_hours=0.1,  # 6-minute intervals for detailed simulation
            soc_update_callback=self.bus_simulation.get_current_soc
        )

        result = self.bus_simulation.simulate_battery(
            bus,
            conditions,
            soc_window,
            save_interval_hours=1.0  # Save every hour
        )

        final_state = result.history[-1]
        capacity_loss = ((bus.battery_capacity - final_state.capacity) / bus.battery_capacity) * 100.0

        print("=== SIMULATION RESULTS ===")
        print(f"Final SoH: {final_state.soh:.2f}%")
        print(f"Final Capacity: {final_state.capacity:.2f} Ah")
        print(f"Capacity Loss: {capacity_loss:.2f}%")
        print(f"Total EFC: {final_state.cycle_count:.2f}")
        print(f"Calendar Age: {final_state.calendar_age:.1f} days")
        print(f"Total Ah Throughput: {final_state.total_ah_throughput:.1f} Ah")

        return result
