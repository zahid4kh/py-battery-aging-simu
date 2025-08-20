from synthetic_data_generator import SyntheticDataGenerator
from lab_battery_simulation import LabBatterySimulation
from aging_model import AgingModel
import numpy as np


def validate_single_condition():
    print("=== KRUPP MODEL VALIDATION ===")
    print("Testing single condition: DoD=50%, SoC_avg=50%, T=25°C, 1C")

    generator = SyntheticDataGenerator(battery_capacity_ah=3.3)

    conditions = generator.generate_cyclic_aging_profile(
        dod=0.5,
        soc_avg=0.5,
        temperature=23.0,
        c_rate=1.0,
        target_efc=100.0
    )

    aging_model = AgingModel()
    simulator = LabBatterySimulation(aging_model)

    history = simulator.simulate_lab_test(conditions, battery_capacity_ah=3.3)

    final_state = history[-1]
    capacity_loss = (3.3 - final_state.capacity) / 3.3 * 100

    print(f"\n=== RESULTS ===")
    print(f"Final EFC: {final_state.cycle_count:.1f}")
    print(f"Final SOH: {final_state.soh:.2f}%")
    print(f"Capacity Loss: {capacity_loss:.3f}%")
    print(f"Total Duration: {conditions[-1].time:.1f} hours")

    print(f"\nExpected: ~2-5% loss at 100 EFC")
    print(
        f"Result: {capacity_loss:.3f}% loss at {final_state.cycle_count:.1f} EFC")

    if 1.0 <= capacity_loss <= 8.0:
        print("Reasonable!")
    else:
        print("Outside expected range!")

    return history


def validate_krupp_test_matrix():

    print("\n=== KRUPP FULL TEST MATRIX ===")

    dod_values = [0.2, 0.5, 0.8]
    soc_values = [0.5, 0.7, 0.9]
    temperatures = [23, 40]
    c_rates = [1.0]
    target_efc = 200

    results = []
    generator = SyntheticDataGenerator(battery_capacity_ah=3.3)
    aging_model = AgingModel()
    simulator = LabBatterySimulation(aging_model)

    total_tests = len(dod_values) * len(soc_values) * \
        len(temperatures) * len(c_rates)
    current_test = 0

    for dod in dod_values:
        for soc_avg in soc_values:
            for temp in temperatures:
                for c_rate in c_rates:
                    current_test += 1
                    print(f"\n--- Test {current_test}/{total_tests} ---")
                    print(
                        f"DoD={dod*100:.0f}%, SoC_avg={soc_avg*100:.0f}%, T={temp}°C, C-rate={c_rate}")

                    conditions = generator.generate_cyclic_aging_profile(
                        dod=dod,
                        soc_avg=soc_avg,
                        temperature=temp,
                        c_rate=c_rate,
                        target_efc=target_efc
                    )

                    history = simulator.simulate_lab_test(
                        conditions, battery_capacity_ah=3.3)
                    final_state = history[-1]
                    capacity_loss = (3.3 - final_state.capacity) / 3.3 * 100

                    result = {
                        'dod': dod,
                        'soc_avg': soc_avg,
                        'temperature': temp,
                        'c_rate': c_rate,
                        'final_efc': final_state.cycle_count,
                        'capacity_loss_percent': capacity_loss,
                        'final_soh': final_state.soh
                    }
                    results.append(result)

                    print(
                        f"Result: {capacity_loss:.2f}% loss at {final_state.cycle_count:.1f} EFC")

    print(f"\n=== TEST MATRIX SUMMARY ===")
    for result in results:
        print(f"DoD={result['dod']*100:.0f}%, SoC={result['soc_avg']*100:.0f}%, "
              f"T={result['temperature']:.0f}°C: {result['capacity_loss_percent']:.2f}% loss")

    return results


if __name__ == "__main__":
    single_result = validate_single_condition()

    response = input("\nRun full test matrix? (y/n): ")
    if response.lower() == 'y':
        matrix_results = validate_krupp_test_matrix()
