import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_mock_trolleybus_data():
    start_time = datetime(2024, 3, 1, 6, 0, 0)  # Start at 6 AM
    intervals = 8640

    data = []
    current_time = start_time

    route_segments = [
        {"has_catenary": True, "segment_length": 100},  # 100 intervals with overhead
        {"has_catenary": False, "segment_length": 50},  # 50 intervals battery only
        {"has_catenary": True, "segment_length": 80},  # 80 intervals with overhead
        {"has_catenary": False, "segment_length": 70},  # 70 intervals battery only
    ]

    segment_idx = 0
    segment_counter = 0

    for i in range(intervals):
        # Current segment
        current_segment = route_segments[segment_idx]

        hour = current_time.hour
        is_peak = (7 <= hour <= 9) or (17 <= hour <= 19)  # Morning/evening peaks
        is_night = hour < 6 or hour > 22

        if is_night:
            velocity = 0
            traction_power = 0
            heating_power = 2 if hour < 6 else 0
            passengers = 0
        else:
            velocity = np.random.normal(25, 10) if not is_peak else np.random.normal(15, 8)
            velocity = max(0, min(50, velocity))

            base_traction = velocity * 2 + np.random.normal(0, 5)
            passenger_load = np.random.randint(10, 80) if is_peak else np.random.randint(5, 40)
            traction_power = max(0, base_traction + passenger_load * 0.5)

            temp = 5 + np.sin(hour / 24 * 2 * np.pi) * 8
            heating_power = max(0, (10 - temp) * 0.8) if temp < 10 else 0
            aircond_power = max(0, (temp - 20) * 1.2) if temp > 20 else 0
            passengers = passenger_load

        lv_aux_power = 2 + np.random.normal(0, 0.5)
        hv_aux_power = 1 + np.random.normal(0, 0.3)

        total_power = traction_power + heating_power + aircond_power + lv_aux_power + hv_aux_power

        has_catenary = current_segment["has_catenary"]
        catenary_voltage = 750 if has_catenary else 0
        available_catenary_power = 300 if has_catenary else 0
        max_catenary_current = available_catenary_power / catenary_voltage if catenary_voltage > 0 else 0

        data.append({
            'satellites_count': np.random.randint(8, 16),
            'route_id': 1,
            'dest_id': 1,
            'longitude': 5.917687 + np.random.normal(0, 0.001),
            'latitude': 51.976417 + np.random.normal(0, 0.001),
            'velocity_kmh': velocity,
            'max_catenary_current_a': max_catenary_current,
            'catenary_voltage_v': catenary_voltage,
            'traction_power_kw': traction_power,
            'heating_power_kw': heating_power,
            'aircond_power_kw': aircond_power if 'aircond_power' in locals() else 0,
            'lv_aux_power_kw': lv_aux_power,
            'hv_aux_power_kw': hv_aux_power,
            'ambient_air_temp_degc': temp if 'temp' in locals() else 5,
            'duration': 10000000000,  # 10 seconds in nanoseconds
            'duration_hours': 10 / 3600,  # 10 seconds in hours
            'geometry': None,  # Skip complex geometry
            'has_catenary': has_catenary,
            'available_catenary_power_kw': available_catenary_power,
            'power_consumption_kw': total_power,
            'datetime': int(current_time.timestamp() * 1000)  # Milliseconds
        })

        current_time += timedelta(seconds=10)

        # Advance segment
        segment_counter += 1
        if segment_counter >= current_segment["segment_length"]:
            segment_idx = (segment_idx + 1) % len(route_segments)
            segment_counter = 0

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    print("Creating mock trolleybus data...")
    df = create_mock_trolleybus_data()

    df.to_parquet('data/mock_trolleybus_day1.parquet', index=False)

    print(f"Created parquet file with {len(df)} rows")
    print(f"Time range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(
        f"Power consumption range: {df['power_consumption_kw'].min():.1f} to {df['power_consumption_kw'].max():.1f} kW")
    print(f"Average power: {df['power_consumption_kw'].mean():.1f} kW")
    print(f"Catenary coverage: {df['has_catenary'].mean() * 100:.1f}%")

    # Show sample
    print("\nFirst 5 rows:")
    print(df.head())