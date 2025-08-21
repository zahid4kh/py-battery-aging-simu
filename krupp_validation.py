from synthetic_data_generator import SyntheticDataGenerator
from lab_battery_simulation import LabBatterySimulation
from aging_model import AgingModel
import csv
import os

def validate_krupp_cyclic_matrix():
    os.makedirs('csv-cyclic', exist_ok=True)
    # Table 4.3
    krupp_tests = [
        # No. DoD, ØSoC, C-rate, Expected aging mode
        (1, 0.05, 0.50, 0.5, "LLI"),
        (2, 0.10, 0.50, 0.5, "LLI"),
        (3, 0.20, 0.50, 0.5, "LLI"),
        (4, 0.40, 0.50, 0.5, "LLI"),
        (5, 0.50, 0.50, 0.5, "LLI"),
        (6, 0.60, 0.50, 0.5, "LLI"),
        (7, 0.80, 0.50, 0.5, "LLI+LAM"),
        (8, 0.90, 0.50, 0.5, "LLI+LAM"),
        (9, 0.10, 0.70, 0.5, "LLI"),
        (10, 0.10, 0.90, 0.5, "LLI"),
        (11, 0.10, 0.70, 1.25, "LLI"),
        (12, 0.10, 0.70, 2.0, "LLI"),
        (13, 1.00, 0.50, 2.0, "LLI+LAM"),
        # Test 14 excluded due to measuring channel failure
    ]

    results = []
    generator = SyntheticDataGenerator(battery_capacity_ah=3.3)
    aging_model = AgingModel()
    simulator = LabBatterySimulation(aging_model)

    target_efc = 200
    temperature = 23.0

    for test_no, dod, soc_avg, c_rate, expected_aging in krupp_tests:
        conditions = generator.generate_cyclic_aging_profile(
            dod=dod,
            soc_avg=soc_avg,
            c_rate=c_rate,
            temperature=temperature,
            target_efc=target_efc
        )

        start_soc = min(1.0, soc_avg + dod / 2)

        history = simulator.simulate_lab_test(
            conditions,
            battery_capacity_ah=3.3,
            initial_soc=start_soc
        )

        final_state = history[-1]
        capacity_loss = (3.3 - final_state.capacity) / 3.3 * 100

        result = {
            'test_no': test_no,
            'dod_percent': dod * 100,
            'soc_avg_percent': soc_avg * 100,
            'c_rate': c_rate,
            'expected_aging': expected_aging,
            'final_efc': final_state.cycle_count,
            'capacity_loss_percent': capacity_loss,
            'final_soh': final_state.soh
        }
        results.append(result)

        with open(f'csv-cyclic/test_{test_no:02d}.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=result.keys())
            writer.writeheader()
            writer.writerow(result)

    with open('csv-cyclic/summary.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    return results

def validate_calendar_aging():
    os.makedirs('csv-calendar', exist_ok=True)

    soc_values = [0.5, 0.7, 0.9]
    temperatures = [23, 40]
    duration_days = 60

    results = []
    generator = SyntheticDataGenerator(battery_capacity_ah=3.3)
    aging_model = AgingModel()
    simulator = LabBatterySimulation(aging_model)

    test_number = 0
    for soc in soc_values:
        for temp in temperatures:
            test_number += 1

            conditions = generator.generate_calendar_aging_profile(
                soc=soc,
                temperature=temp,
                duration_days=duration_days
            )

            history = simulator.simulate_lab_test(
                conditions,
                battery_capacity_ah=3.3,
                initial_soc=soc
            )

            final_state = history[-1]
            capacity_loss = (3.3 - final_state.capacity) / 3.3 * 100

            result = {
                'test_no': test_number,
                'soc_percent': soc * 100,
                'temperature': temp,
                'duration_days': duration_days,
                'capacity_loss_percent': capacity_loss,
                'final_soh': final_state.soh
            }
            results.append(result)

            with open(f'csv-calendar/test_{test_number:02d}.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=result.keys())
                writer.writeheader()
                writer.writerow(result)

    with open('csv-calendar/summary.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    return results

if __name__ == "__main__":
    calendar_results = validate_calendar_aging()

    response = input("\nRun Table 4.3 cyclic matrix? (y/n): ")
    if response.lower() == 'y':
        cyclic_results = validate_krupp_cyclic_matrix()
        print("\nKrupp validation complete!")