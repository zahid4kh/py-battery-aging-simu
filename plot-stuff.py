import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def load_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    
    data = {
        'time_hours': df["time_hours"].to_list(),
        'cyclic_loss': df["cyclic_loss"].to_list(),
        'calendar_loss': df["calendar_loss"].to_list(),
        'capacity': df["capacity"].to_list(),
        'efc': df["efc"].to_list(),
        'current_dod': df["current_dod"].to_list(),
        'soc': df["soc"].to_list(),
        'soh': df["soh"].to_list(),
        'current': df["current"].to_list(),
        'calendar_age_days': df["calendar_age_days"].to_list(),
        'total_ah_throughput': df["total_ah_throughput"].to_list(),
        'is_charging': df["isCharging"].to_list(),
        'is_regenerating': df["is_regenerating"].to_list()
    }
    
    return data

def plot_dod_vs_time(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['time_hours'], [d*100 for d in data['current_dod']], 'b-', linewidth=1.5)
    plt.xlabel('Time (hours)')
    plt.ylabel('Depth of Discharge (%)')
    plt.title(f'DOD vs Time - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/dod_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_soh_vs_time(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['time_hours'], data['soh'], 'r-', linewidth=2)
    plt.xlabel('Time (hours)')
    plt.ylabel('State of Health (%)')
    plt.title(f'SOH vs Time - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/soh_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_cyclic_loss_vs_time(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['time_hours'], [c*100 for c in data['cyclic_loss']], 'purple', linewidth=1.5)
    
    # charging markers
    charging_times = [t for i, t in enumerate(data['time_hours']) if data['is_charging'][i]]
    charging_losses = [data['cyclic_loss'][i]*100 for i, t in enumerate(data['time_hours']) if data['is_charging'][i]]
    plt.scatter(charging_times, charging_losses, marker='*', color='red', s=30, alpha=0.7, label='Charging')
    
    # regen markers
    regen_times = [t for i, t in enumerate(data['time_hours']) if data['is_regenerating'][i]]
    regen_losses = [data['cyclic_loss'][i]*100 for i, t in enumerate(data['time_hours']) if data['is_regenerating'][i]]
    plt.scatter(regen_times, regen_losses, marker='^', color='green', s=30, alpha=0.7, label='Regenerating')
    
    plt.xlabel('Time (hours)')
    plt.ylabel('Cyclic Loss (%)')
    plt.title(f'Cyclic Loss vs Time - {bus_id}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/cyclic_loss_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_calendar_loss_vs_time(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['time_hours'], [c*100 for c in data['calendar_loss']], 'orange', linewidth=1.5)
    plt.xlabel('Time (hours)')
    plt.ylabel('Calendar Loss (%)')
    plt.title(f'Calendar Loss vs Time - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/calendar_loss_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_efc_vs_time(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['time_hours'], data['efc'], 'brown', linewidth=1.5)
    plt.xlabel('Time (hours)')
    plt.ylabel('Equivalent Full Cycles')
    plt.title(f'EFC vs Time - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/efc_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_soc_vs_time(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['time_hours'], [s*100 for s in data['soc']], 'blue', linewidth=1)
    
    # charging markers
    charging_times = [t for i, t in enumerate(data['time_hours']) if data['is_charging'][i]]
    charging_socs = [data['soc'][i]*100 for i, t in enumerate(data['time_hours']) if data['is_charging'][i]]
    plt.scatter(charging_times, charging_socs, marker='*', color='red', s=40, alpha=0.8, label='Charging')
    
    # regen markers
    regen_times = [t for i, t in enumerate(data['time_hours']) if data['is_regenerating'][i]]
    regen_socs = [data['soc'][i]*100 for i, t in enumerate(data['time_hours']) if data['is_regenerating'][i]]
    plt.scatter(regen_times, regen_socs, marker='^', color='green', s=40, alpha=0.8, label='Regenerating')
    
    plt.xlabel('Time (hours)')
    plt.ylabel('State of Charge (%)')
    plt.title(f'SOC vs Time - {bus_id}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/soc_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_current_vs_time(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['time_hours'], data['current'], 'black', linewidth=1)
    
    # charging markers (negative current)
    charging_times = [t for i, t in enumerate(data['time_hours']) if data['is_charging'][i]]
    charging_currents = [data['current'][i] for i, t in enumerate(data['time_hours']) if data['is_charging'][i]]
    plt.scatter(charging_times, charging_currents, marker='*', color='red', s=30, alpha=0.7, label='Charging')
    
    # regen markers (negative current)
    regen_times = [t for i, t in enumerate(data['time_hours']) if data['is_regenerating'][i]]
    regen_currents = [data['current'][i] for i, t in enumerate(data['time_hours']) if data['is_regenerating'][i]]
    plt.scatter(regen_times, regen_currents, marker='^', color='green', s=30, alpha=0.7, label='Regenerating')
    
    plt.xlabel('Time (hours)')
    plt.ylabel('Current (A)')
    plt.title(f'Current vs Time - {bus_id}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/current_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_cyclic_loss_vs_efc(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.scatter(data['efc'], [c*100 for c in data['cyclic_loss']], alpha=0.6, s=20)
    plt.xlabel('Equivalent Full Cycles')
    plt.ylabel('Cyclic Loss (%)')
    plt.title(f'Cyclic Loss vs EFC - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/cyclic_loss_vs_efc.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_soh_vs_throughput(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.plot(data['total_ah_throughput'], data['soh'], 'darkred', linewidth=1.5)
    plt.xlabel('Total Ah Throughput (Ah)')
    plt.ylabel('State of Health (%)')
    plt.title(f'SOH vs Total Ah Throughput - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/soh_vs_throughput.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_soc_vs_cyclic_loss(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.scatter([s*100 for s in data['soc']], [c*100 for c in data['cyclic_loss']], alpha=0.6, s=20)
    plt.xlabel('State of Charge (%)')
    plt.ylabel('Cyclic Loss (%)')
    plt.title(f'SOC vs Cyclic Loss - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/soc_vs_cyclic_loss.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_soc_vs_calendar_loss(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.scatter([s*100 for s in data['soc']], [c*100 for c in data['calendar_loss']], alpha=0.6, s=20)
    plt.xlabel('State of Charge (%)')
    plt.ylabel('Calendar Loss (%)')
    plt.title(f'SOC vs Calendar Loss - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/soc_vs_calendar_loss.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_dod_vs_cyclic_loss(data, bus_id):
    plt.figure(figsize=(12, 6))
    plt.scatter([d*100 for d in data['current_dod']], [c*100 for c in data['cyclic_loss']], alpha=0.6, s=20)
    plt.xlabel('Depth of Discharge (%)')
    plt.ylabel('Cyclic Loss (%)')
    plt.title(f'DOD vs Cyclic Loss - {bus_id}')
    plt.grid(True, alpha=0.3)
    
    os.makedirs(f'plots/{bus_id}', exist_ok=True)
    plt.savefig(f'plots/{bus_id}/dod_vs_cyclic_loss.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_all_plots(csv_file_path, bus_id):
    print(f"Generating plots for {bus_id}...")
    
    data = load_data(csv_file_path)
    
    plot_dod_vs_time(data, bus_id)
    plot_soh_vs_time(data, bus_id)
    plot_cyclic_loss_vs_time(data, bus_id)
    plot_calendar_loss_vs_time(data, bus_id)
    plot_efc_vs_time(data, bus_id)
    plot_soc_vs_time(data, bus_id)
    plot_current_vs_time(data, bus_id)
    plot_cyclic_loss_vs_efc(data, bus_id)
    plot_soh_vs_throughput(data, bus_id)
    plot_soc_vs_cyclic_loss(data, bus_id)
    plot_soc_vs_calendar_loss(data, bus_id)
    plot_dod_vs_cyclic_loss(data, bus_id)
    
    print(f"All plots generated for {bus_id} and saved to 'plots/' folder")

if __name__ == "__main__":
    bus_ids = ["SOC40-80_Soft", "SOC50-75_Standard", "SOC30-90_Rough"]
    
    for bus_id in bus_ids:
        csv_path = f"csv-results/{bus_id}/simulation_detailed_{bus_id}.csv"
        if os.path.exists(csv_path):
            generate_all_plots(csv_path, bus_id)
        else:
            print(f"CSV file not found: {csv_path}")