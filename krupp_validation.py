from synthetic_data_generator import SyntheticDataGenerator
from lab_battery_simulation import LabBatterySimulation
from aging_model import AgingModel
import numpy as np


def validate_krupp_cyclic_matrix():
    print("=== KRUPP TABLE 4.3 CYCLIC AGING MATRIX ===")

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
        print(f"\n--- Test {test_no}/13 (Krupp Table 4.3) ---")
        print(f"DoD={dod * 100:.0f}%, ØSoC={soc_avg * 100:.0f}%, C-rate={c_rate}, Expected: {expected_aging}")

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
            'dod': dod,
            'soc_avg': soc_avg,
            'c_rate': c_rate,
            'expected_aging': expected_aging,
            'final_efc': final_state.cycle_count,
            'capacity_loss_percent': capacity_loss,
            'final_soh': final_state.soh
        }
        results.append(result)

        print(f"Result: {capacity_loss:.2f}% loss at {final_state.cycle_count:.1f} EFC")

    # Summary
    print(f"\n=== KRUPP MATRIX SUMMARY ===")
    for result in results:
        print(f"Test {result['test_no']:2d}: DoD={result['dod'] * 100:3.0f}%, "
              f"ØSoC={result['soc_avg'] * 100:2.0f}%, C={result['c_rate']:4.2f} → "
              f"{result['capacity_loss_percent']:5.2f}% loss ({result['expected_aging']})")

    return results

def validate_calendar_aging():

    print("=== KRUPP CALENDAR AGING VALIDATION ===")

    soc_values = [0.5, 0.7, 0.9]
    temperatures = [23, 40]
    duration_days = 60

    results = []
    generator = SyntheticDataGenerator(battery_capacity_ah=3.3)
    aging_model = AgingModel()
    simulator = LabBatterySimulation(aging_model)

    for soc in soc_values:
        for temp in temperatures:
            print(
                f"\nTesting: {soc*100:.0f}% SOC, {temp}°C, {duration_days} days")

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
                'soc': soc,
                'temperature': temp,
                'duration_days': duration_days,
                'capacity_loss_percent': capacity_loss,
                'final_soh': final_state.soh
            }
            results.append(result)

            print(
                f"Result: {capacity_loss:.3f}% loss after {duration_days} days")

    return results


def validate_cyclic_aging():

    print("=== KRUPP CYCLIC AGING VALIDATION ===")

    # doesn't specify exact DOD values -> using reasonable range
    dod_values = [0.2, 0.5, 0.8]
    soc_values = [0.5, 0.7, 0.9]
    temperatures = [23]
    target_efc = 100

    results = []
    generator = SyntheticDataGenerator(battery_capacity_ah=3.3)
    aging_model = AgingModel()
    simulator = LabBatterySimulation(aging_model)

    total_tests = len(dod_values) * len(soc_values) * len(temperatures)
    current_test = 0

    for dod in dod_values:
        for soc_avg in soc_values:
            for temp in temperatures:
                current_test += 1
                print(f"\n--- Test {current_test}/{total_tests} ---")
                print(
                    f"DoD={dod*100:.0f}%, SoC_avg={soc_avg*100:.0f}%, T={temp}°C")

                conditions = generator.generate_cyclic_aging_profile(
                    dod=dod,
                    soc_avg=soc_avg,
                    temperature=temp,
                    target_efc=target_efc
                )

                start_soc = min(1.0, soc_avg + dod/2)

                history = simulator.simulate_lab_test(
                    conditions,
                    battery_capacity_ah=3.3,
                    initial_soc=start_soc
                )

                final_state = history[-1]
                capacity_loss = (3.3 - final_state.capacity) / 3.3 * 100

                result = {
                    'dod': dod,
                    'soc_avg': soc_avg,
                    'temperature': temp,
                    'final_efc': final_state.cycle_count,
                    'capacity_loss_percent': capacity_loss,
                    'final_soh': final_state.soh
                }
                results.append(result)

                print(
                    f"Result: {capacity_loss:.2f}% loss at {final_state.cycle_count:.1f} EFC")

    return results


if __name__ == "__main__":
    calendar_results = validate_calendar_aging()

    response = input("\nRun Table 4.3 cyclic matrix? (y/n): ")
    if response.lower() == 'y':
        cyclic_results = validate_krupp_cyclic_matrix()
        print("\nKrupp validation complete!")