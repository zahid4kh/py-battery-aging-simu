from simulation_runner import SimulationRunner

def main():
    runner = SimulationRunner()

    print("Starting 30-day trolleybus battery aging simulation...")
    print()

    result = runner.run_simulation(
        duration_days=30.0,
        temperature=25.0,
        soc_window=(0.3, 0.9),
        bus_id="TrolleyBus_30Day"
    )


if __name__ == "__main__":
    main()