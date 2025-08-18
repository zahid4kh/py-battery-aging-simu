from typing import Tuple
from data_loader import DataLoader
from bus_simulation import BusSimulation
from data.bus import RouteType, Bus
from data.simulation_result import SimulationResult
from data.simulation_parameters import SimulationParameters


class SimulationRunner:
    def __init__(self):
        self.bus_simulation = None
        self.data_loader = None

    def run_simulation(
            self,
            parquet_file_path: str,
            soc_window: Tuple[float, float],
            sim_params: SimulationParameters = None,
            bus_id: str = "Data_Bus"
    ) -> SimulationResult:
        if sim_params is None:
            sim_params = SimulationParameters()

        self.data_loader = DataLoader(parquet_file_path)
        conditions = self.data_loader.convert_to_operating_conditions()

        self.bus_simulation = BusSimulation(sim_params=sim_params)

        bus = Bus(
            id=bus_id,
            route_type=RouteType.CITY,
            battery_capacity=400.0,
            initial_soc=0.7,  
        )

        battery_capacity_kwh = (bus.battery_capacity * sim_params.battery_voltage) / 1000

        duration_hours = conditions[-1].time
        print(f"=== Real Data Trolleybus Battery Aging Simulation ===")
        print(f"Bus ID: {bus_id}")
        print(f"Duration: {duration_hours:.2f} hours ({duration_hours / 24:.2f} days)")
        print(f"Data Points: {len(conditions)}")
        print(
            f"Temperature Range: {min(c.ambient_temp for c in conditions):.1f}°C - {max(c.ambient_temp for c in conditions):.1f}°C")
        print(f"SoC Window: {soc_window[0] * 100}% - {soc_window[1] * 100}%")
        print(f"Battery Capacity: {bus.battery_capacity} Ah ({battery_capacity_kwh:.1f} kWh)")
        print()

        result = self.bus_simulation.simulate_battery(
            bus,
            conditions,
            soc_window,
            save_interval_hours=0.5
        )

        final_state = result.history[-1]
        capacity_loss = ((bus.battery_capacity - final_state.capacity) / bus.battery_capacity) * 100.0

        print("=== SIMULATION RESULTS ===")
        print(f"Final SoH: {final_state.soh:.2f}%")
        print(f"Final Capacity: {final_state.capacity:.2f} Ah")
        print(f"Capacity Loss: {capacity_loss:.4f}%")
        print(f"Total EFC: {final_state.cycle_count:.2f}")
        print(f"Calendar Age: {final_state.calendar_age:.2f} days")
        print(f"Total Ah Throughput: {final_state.total_ah_throughput:.1f} Ah")

        return result