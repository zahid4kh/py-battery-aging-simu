from simulation_runner import SimulationRunner
from utils.utils import years_to_hours, weeks_to_hours, days_to_hours

def main():
    runner = SimulationRunner()

    print("=== Battery Aging Comparison Simulation ===")
    print()

    print("1. Full Comparison (1 year simulation):")
    runner.run_comparison(years_to_hours(1.0))

    print()
    print("2. Quick Test (1 week simulation):")
    runner.run_comparison(weeks_to_hours(1.0))

    print()
    print("3. Single Scenario Example (30 days):")
    runner.run_single_scenario(days_to_hours(30.0), 25.0, (0.3, 0.9))


if __name__ == "__main__":
    main()