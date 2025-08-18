import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime

def load_all_simulation_data():
    combined_data = []
    available_days = []
    
    if os.path.exists("csv-results"):
        for folder in os.listdir("csv-results"):
            if folder.startswith("March_Day"):
                csv_path = f"csv-results/{folder}/simulation_detailed_{folder}.csv"
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    df['day'] = folder
                    df['day_number'] = int(folder.split('Day')[1])
                    combined_data.append(df)
                    available_days.append(folder)
    
    if not combined_data:
        return None, []
    
    full_df = pd.concat(combined_data, ignore_index=True)
    available_days.sort(key=lambda x: int(x.split('Day')[1]))
    
    return full_df, available_days

def create_daily_summary():
    full_df, available_days = load_all_simulation_data()
    
    if full_df is None:
        print("No simulation data found!")
        return None
    
    daily_summary = []
    
    for day in available_days:
        day_data = full_df[full_df['day'] == day]
        
        if len(day_data) == 0:
            continue
            
        summary = {
            'day': day,
            'day_number': day_data['day_number'].iloc[0],
            'duration_hours': day_data['time_hours'].max(),
            'initial_soh': day_data['soh'].iloc[0],
            'final_soh': day_data['soh'].iloc[-1],
            'capacity_loss_percent': day_data['soh'].iloc[0] - day_data['soh'].iloc[-1],
            'final_efc': day_data['efc'].iloc[-1],
            'total_throughput': day_data['total_ah_throughput'].iloc[-1],
            'final_cyclic_loss': day_data['cyclic_loss'].iloc[-1] * 100,
            'final_calendar_loss': day_data['calendar_loss'].iloc[-1] * 100,
            'avg_temperature': day_data['temperature'].mean(),
            'min_soc': day_data['soc'].min() * 100,
            'max_soc': day_data['soc'].max() * 100,
            'avg_dod': day_data['current_dod'].mean() * 100,
            'charging_events': day_data['isCharging'].sum(),
            'regen_events': day_data['is_regenerating'].sum(),
            'max_current': day_data['current'].max(),
            'min_current': day_data['current'].min()
        }
        daily_summary.append(summary)
    
    return pd.DataFrame(daily_summary)

def plot_aging_mechanisms():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.bar(summary_df['day_number'], summary_df['final_cyclic_loss'], 
            color='purple', alpha=0.8)
    plt.xlabel('Day Number')
    plt.ylabel('Cyclic Loss (%)')
    plt.title('Daily Cyclic Aging')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.bar(summary_df['day_number'], summary_df['final_calendar_loss'], 
            color='orange', alpha=0.8)
    plt.xlabel('Day Number')
    plt.ylabel('Calendar Loss (%)')
    plt.title('Daily Calendar Aging')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs('plots/combined', exist_ok=True)
    plt.savefig('plots/combined/aging_mechanisms.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_soh_degradation():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.plot(summary_df['day_number'], summary_df['final_soh'], 'ro-', linewidth=2, markersize=6)
    plt.xlabel('Day Number')
    plt.ylabel('Final SOH (%)')
    plt.title('Daily SOH Evolution')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('plots/combined/soh_degradation.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_daily_capacity_loss():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.bar(summary_df['day_number'], summary_df['capacity_loss_percent'], 
            color='red', alpha=0.7)
    plt.xlabel('Day Number')
    plt.ylabel('Daily Capacity Loss (%)')
    plt.title('Daily Capacity Loss')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('plots/combined/daily_capacity_loss.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_efc():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.plot(summary_df['day_number'], summary_df['final_efc'], 'go-', linewidth=2, markersize=6)
    plt.xlabel('Day Number')
    plt.ylabel('EFC per Day')
    plt.title('Daily EFC Accumulation')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('plots/combined/efc.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_temperature():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.plot(summary_df['day_number'], summary_df['avg_temperature'], 'bo-', linewidth=2, markersize=6)
    plt.xlabel('Day Number')
    plt.ylabel('Average Temperature (°C)')
    plt.title('Daily Temperature Variation')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('plots/combined/temperature.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_soc():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.fill_between(summary_df['day_number'], 
                     summary_df['min_soc'], summary_df['max_soc'], 
                     alpha=0.5, color='green')
    plt.plot(summary_df['day_number'], summary_df['min_soc'], 'g--', label='Min SOC', linewidth=2)
    plt.plot(summary_df['day_number'], summary_df['max_soc'], 'g-', label='Max SOC', linewidth=2)
    plt.xlabel('Day Number')
    plt.ylabel('SOC (%)')
    plt.title('Daily SOC Window')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig('plots/combined/soc.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_dod():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.plot(summary_df['day_number'], summary_df['avg_dod'], 'ro-', linewidth=2, markersize=6)
    plt.xlabel('Day Number')
    plt.ylabel('Average DOD (%)')
    plt.title('Daily Average DOD')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('plots/combined/dod.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_current():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.fill_between(summary_df['day_number'], 
                     summary_df['min_current'], summary_df['max_current'], 
                     alpha=0.5, color='black')
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    plt.xlabel('Day Number')
    plt.ylabel('Current (A)')
    plt.title('Daily Current Range')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('plots/combined/current.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_total_ah_throughput():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        return
    
    plt.figure(figsize=(12, 6))
    plt.plot(summary_df['day_number'], summary_df['total_throughput'], 'mo-', linewidth=2, markersize=6)
    plt.xlabel('Day Number')
    plt.ylabel('Total Ah Throughput (Ah)')
    plt.title('Daily Ah Throughput')
    plt.grid(True, alpha=0.3)
    
    # x-ticks to match day numbers
    plt.xticks(summary_df['day_number'])
    
    plt.savefig('plots/combined/total_ah_throughput.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_combined_summary_report():
    summary_df = create_daily_summary()
    
    if summary_df is None:
        print("No data available...")
        return
    
    total_days = len(summary_df)
    total_duration = summary_df['duration_hours'].sum()
    total_efc = summary_df['final_efc'].sum()
    total_throughput = summary_df['total_throughput'].sum()
    total_capacity_loss = summary_df['capacity_loss_percent'].sum()
    
    avg_daily_efc = summary_df['final_efc'].mean()
    avg_daily_duration = summary_df['duration_hours'].mean()
    avg_temperature = summary_df['avg_temperature'].mean()
    
    #annual_efc = avg_daily_efc * 365
    annual_capacity_loss = (total_capacity_loss / total_days) * 365
    
    report = f"""
# BATTERY AGING ANALYSIS REPORT

## OPERATIONAL SUMMARY:
- **Days Analyzed:** {total_days}
- **Total Operation Time:** {total_duration:.1f} hours
- **Average Daily Duration:** {avg_daily_duration:.1f} hours
- **Average Temperature:** {avg_temperature:.1f}°C

## BATTERY USAGE:
- **Total EFC:** {total_efc:.2f}
- **Average EFC per Day:** {avg_daily_efc:.2f}
- **Total Ah Throughput:** {total_throughput:.0f} Ah

## AGING RESULTS:
- **Total Capacity Loss:** {total_capacity_loss:.4f}%
- **Daily Loss:** {total_capacity_loss/total_days:.4f}%
- **Annual Degradation:** {annual_capacity_loss:.2f}% per year

## OPERATIONAL PATTERNS:
- **SOC Window:** {summary_df['min_soc'].min():.1f}% - {summary_df['max_soc'].max():.1f}%
- **Average DOD:** {summary_df['avg_dod'].mean():.1f}%
- **Charging Events:** {summary_df['charging_events'].sum()}
- **Regen Events:** {summary_df['regen_events'].sum()}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    os.makedirs('plots/combined', exist_ok=True)
    with open('plots/combined/summary_report.md', 'w') as f:
        f.write(report)
    
    summary_df.to_csv('plots/combined/daily_summary_statistics.csv', index=False)
    
    print(report)

if __name__ == "__main__":
    print("=== COMBINED TROLLEYBUS BATTERY ANALYSIS ===")
    
    full_df, available_days = load_all_simulation_data()
    
    if full_df is None:
        print("No simulation results found! Run main.py first.")
    else:
        print(f"Analyzing {len(available_days)} days of operation...")
        
        print("Generating aging mechanisms plot...")
        plot_aging_mechanisms()
        
        print("Generating SOH degradation plot...")
        plot_soh_degradation()
        
        print("Generating daily capacity loss plot...")
        plot_daily_capacity_loss()
        
        print("Generating EFC plot...")
        plot_efc()
        
        print("Generating temperature plot...")
        plot_temperature()
        
        print("Generating SOC plot...")
        plot_soc()
        
        print("Generating DOD plot...")
        plot_dod()
        
        print("Generating current plot...")
        plot_current()
        
        print("Generating total Ah throughput plot...")
        plot_total_ah_throughput()
        
        print("Generating summary report...")
        generate_combined_summary_report()
        
        print("All analysis complete! Check 'plots/combined/' folder!")