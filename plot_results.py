import pandas as pd
import matplotlib.pyplot as plt
import os

def create_plots():
    os.makedirs('plots', exist_ok=True)
    plot_calendar_aging()
    plot_cyclic_aging()
    plot_krupp_style_calendar()

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
        plt.savefig('plots/calendar_soc_vs_loss.png', dpi=150, bbox_inches='tight')
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
        plt.savefig('plots/calendar_temp_vs_loss.png', dpi=150, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Error plotting calendar aging: {e}")

def plot_cyclic_aging():
    try:
        df = pd.read_csv('csv-cyclic/summary.csv')
        
        # DoD vs Capacity Loss (at 50% SOC, 0.5C)
        baseline_data = df[(df['soc_avg_percent'] == 50) & (df['c_rate'] == 0.5)]
        plt.figure(figsize=(8, 6))
        plt.plot(baseline_data['dod_percent'], baseline_data['capacity_loss_percent'], 
                'o-', color='blue', markersize=8, linewidth=2)
        plt.xlabel('DoD (%)')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: DoD vs Capacity Loss (50% SOC, 0.5C)')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic_dod_vs_loss.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # SOC vs Capacity Loss (10% DoD, 0.5C)
        soc_data = df[(df['dod_percent'] == 10) & (df['c_rate'] == 0.5)]
        plt.figure(figsize=(8, 6))
        plt.plot(soc_data['soc_avg_percent'], soc_data['capacity_loss_percent'], 
                'o-', color='green', markersize=8, linewidth=2)
        plt.xlabel('Average SOC (%)')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: SOC vs Capacity Loss (10% DoD, 0.5C)')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic_soc_vs_loss.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # C-rate vs Capacity Loss (10% DoD, 70% SOC)
        crate_data = df[(df['dod_percent'] == 10) & (df['soc_avg_percent'] == 70)]
        plt.figure(figsize=(8, 6))
        plt.plot(crate_data['c_rate'], crate_data['capacity_loss_percent'], 
                'o-', color='red', markersize=8, linewidth=2)
        plt.xlabel('C-rate')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: C-rate vs Capacity Loss (10% DoD, 70% SOC)')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic_crate_vs_loss.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # EFC vs Capacity Loss
        plt.figure(figsize=(8, 6))
        plt.scatter(df['final_efc'], df['capacity_loss_percent'], alpha=0.7, s=60)
        plt.xlabel('Final EFC')
        plt.ylabel('Capacity Loss (%)')
        plt.title('Cyclic Aging: EFC vs Capacity Loss')
        plt.grid(True, alpha=0.3)
        plt.savefig('plots/cyclic_efc_vs_loss.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # DoD vs Capacity Loss by Aging Mode
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
        plt.savefig('plots/cyclic_aging_modes.png', dpi=150, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Error plotting cyclic aging: {e}")

def plot_krupp_style_calendar():
    """3.5 style calendar aging plot"""
    try:
        df = pd.read_csv('csv-calendar/summary.csv')
        
        plt.figure(figsize=(10, 8))
        
        for temp in sorted(df['temperature'].unique()):
            for soc in sorted(df['soc_percent'].unique()):
                data = df[(df['temperature'] == temp) & (df['soc_percent'] == soc)]
                
                if len(data) > 0:
                    linestyle = '-' if temp == 23 else '--'
                    
                    if soc == 50:
                        color = 'black'
                    elif soc == 70:
                        color = 'blue'
                    else: 
                        color = 'green'
                    
                    plt.plot(data['duration_days'], data['capacity_loss_percent'], 
                            linestyle=linestyle, color=color, marker='s', markersize=6,
                            label=f'{soc}% SOC, {temp}°C', linewidth=2)
        
        plt.xlabel('Time [days]')
        plt.ylabel('Capacity Loss [%]')
        plt.title('Calendar Aging: Capacity Loss vs Time (Krupp Style)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.xlim(0, max(df['duration_days']) * 1.1)
        plt.ylim(0, max(df['capacity_loss_percent']) * 1.1)
        plt.tight_layout()
        plt.savefig('plots/krupp_style_calendar.png', dpi=150, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Error creating Krupp-style calendar plot: {e}")

if __name__ == "__main__":
    create_plots()
    print("Plots created in 'plots' folder")