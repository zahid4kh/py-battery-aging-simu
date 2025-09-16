import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def create_plots():
    os.makedirs('plots/calendar', exist_ok=True)
    os.makedirs('plots/cyclic', exist_ok=True)

    plot_calendar_aging()
    plot_cyclic_aging()
    test_stress_amplitude()


def plot_calendar_aging():
    try:
        df = pd.read_csv('csv-calendar/summary.csv')

        # SOC vs Capacity Loss
        plt.figure(figsize=(8, 6))
        for temp in df['temperature'].unique():
            temp_data = df[df['temperature'] == temp]
            plt.plot(temp_data['soc_percent'], temp_data['capacity_loss_percent'],
                     'o-', label=f'{temp}°C', markersize=8, linewidth=2)
        plt.xlabel('SOC (%)')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Calendar Aging: SOC vs Capacity Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/calendar/soc_vs_loss.png',
                    dpi=150, bbox_inches='tight')
        plt.close()

        # Temperature vs Capacity Loss
        plt.figure(figsize=(8, 6))
        for soc in df['soc_percent'].unique():
            soc_data = df[df['soc_percent'] == soc]
            plt.plot(soc_data['temperature'], soc_data['capacity_loss_percent'],
                     'o-', label=f'{soc}% SOC', markersize=8, linewidth=2)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Calendar Aging: Temperature vs Capacity Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/calendar/temp_vs_loss.png',
                    dpi=150, bbox_inches='tight')
        plt.close()

    except Exception as e:
        print(f"Error plotting calendar aging: {e}")


def plot_cyclic_aging():
    try:
        df = pd.read_csv('csv-cyclic/summary.csv')

        # DoD vs Capacity Loss (all data points)
        plt.figure(figsize=(8, 6))
        plt.scatter(df['dod_percent'],
                    df['capacity_loss_percent'], alpha=0.7, s=60)
        plt.xlabel('DoD (%)')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: DoD vs Capacity Loss')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic/dod_vs_loss.png',
                    dpi=150, bbox_inches='tight')
        plt.close()

        # SOC vs Capacity Loss (all data points)
        plt.figure(figsize=(8, 6))
        plt.scatter(df['soc_avg_percent'],
                    df['capacity_loss_percent'], alpha=0.7, s=60)
        plt.xlabel('Average SOC (%)')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: SOC vs Capacity Loss')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic/soc_vs_loss.png',
                    dpi=150, bbox_inches='tight')
        plt.close()

        # C-rate vs Capacity Loss (all data points)
        plt.figure(figsize=(8, 6))
        plt.scatter(df['c_rate'], df['capacity_loss_percent'], alpha=0.7, s=60)
        plt.xlabel('C-rate')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: C-rate vs Capacity Loss')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic/crate_vs_loss.png',
                    dpi=150, bbox_inches='tight')
        plt.close()

        # EFC vs Capacity Loss
        plt.figure(figsize=(8, 6))
        plt.scatter(df['final_efc'],
                    df['capacity_loss_percent'], alpha=0.7, s=60)
        plt.xlabel('Final EFC')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: EFC vs Capacity Loss')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic/efc_vs_loss.png',
                    dpi=150, bbox_inches='tight')
        plt.close()

        # Aging Modes
        plt.figure(figsize=(8, 6))
        for aging_mode in df['expected_aging'].unique():
            mode_data = df[df['expected_aging'] == aging_mode]
            plt.scatter(mode_data['dod_percent'], mode_data['capacity_loss_percent'],
                        label=aging_mode, alpha=0.7, s=60)
        plt.xlabel('DoD (%)')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: DoD vs Capacity Loss by Aging Mode')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic/aging_modes.png',
                    dpi=150, bbox_inches='tight')
        plt.close()

    except Exception as e:
        print(f"Error plotting cyclic aging: {e}")


def test_stress_amplitude():
    from aging_model import AgingModel
    
    model = AgingModel()
    
    soc_values = np.linspace(0.05, 0.95, 91)
    dod_fixed = 0.05
    stress_soc = []
    
    print("SoC [%] | Stress Amplitude | Notes")
    print("-" * 45)
    
    for soc in soc_values:
        if soc - dod_fixed/2 >= 0 and soc + dod_fixed/2 <= 1.0:
            stress = model._calculate_stress_amplitude(soc, dod_fixed)
            stress_soc.append(stress)
            
            if len(stress_soc) % 10 == 1:
                print(f"{soc*100:5.1f}%  | {stress:.8f}")
        else:
            stress_soc.append(np.nan)
    
    # actual minimum
    valid_stress = [s for s in stress_soc if not np.isnan(s)]
    valid_soc = [soc for soc, s in zip(soc_values, stress_soc) if not np.isnan(s)]
    
    min_idx = np.argmin(valid_stress)
    min_stress_soc = valid_soc[min_idx]
    min_stress_val = valid_stress[min_idx]
    
    print(f"\nActual minimum: {min_stress_soc*100:.1f}% SoC, σ = {min_stress_val:.8f}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(np.array(valid_soc) * 100, valid_stress, 'b-', linewidth=2)
    plt.axvline(min_stress_soc * 100, color='r', linestyle='--', 
                label=f'Minimum at {min_stress_soc*100:.1f}%')
    plt.xlabel('ØSoC [%]')
    plt.ylabel('Stress Amplitude σ')
    plt.title('Stress vs ØSoC at 5% DoD (No Boundary Effects)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('plots/stress_amplitude.png',
                    dpi=150, bbox_inches='tight')
    plt.close()

def calculate_stress_amplitude(avg_soc: float, avg_dod: float) -> float:
    soc_min = max(0.0, avg_soc - avg_dod / 2.0)
    soc_max = min(1.0, avg_soc + avg_dod / 2.0)
    return (calculate_polynomial(soc_max) - calculate_polynomial(soc_min)) * 0.21


def calculate_polynomial(soc: float) -> float:
    if soc <= 1.0:
            soc_percent = soc * 100.0
    else:
        soc_percent = soc

    coeffs = [2.74e-13, -8.39e-11, 8.38e-9,
                -2.39e-7, -5.05e-6, 9.70e-5, 0.02, -6.19e-3]
    result = 0.0
    for i, coeff in enumerate(coeffs):
        result += coeff * (soc_percent ** (7 - i))

    return max(0.0, result)


if __name__ == "__main__":
    create_plots()