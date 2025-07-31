import os
from create_mock_parquet import create_mock_trolleybus_data
from parquet_data_loader import ParquetDataLoader
from bus_simulation import RealBusSimulation
from data.bus import Bus, RouteType


def main():
    os.makedirs('data', exist_ok=True)

    print("=== Creating Mock Parquet Data ===")
    df = create_mock_trolleybus_data()


    print("\n=== Loading Parquet Data ===")
    loader = ParquetDataLoader()
    conditions = loader.load_trolleybus_data('data/mock_trolleybus_day1.parquet')
    summary = loader.get_data_summary(conditions)

    print(f"Data Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n=== Running Real Data Simulation ===")
    bus = Bus(
        id="RealBus_001",
        route_type=RouteType.CITY,
        battery_capacity=300.0,
        initial_soc=0.8
    )

    simulation = RealBusSimulation()
    result = simulation.simulate_from_real_data(bus, conditions, soc_window=(0.2, 0.9))

    print("\n=== Simulation Results ===")
    print(f"Duration: {result['duration_days']:.1f} days")
    print(f"Total Energy Throughput: {result['total_energy_kWh']:.1f} kWh")
    print(f"Total EFC: {result['total_efc']:.2f}")
    print(f"Final SoH: {result['final_state'].soh:.4f}%")
    print(f"Final SoC: {result['final_state'].soc:.1%}")
    print(f"Capacity Loss: {result['capacity_loss_percent']:.4f}%")
    print(f"Remaining Capacity: {result['final_state'].capacity:.1f} kWh")


if __name__ == "__main__":
    main()