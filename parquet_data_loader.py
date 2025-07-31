import pandas as pd
from typing import List
from dataclasses import dataclass


@dataclass
class RealOperatingCondition:
    time_hours: float
    speed_kmh: float
    total_power_kw: float
    traction_power_kw: float
    aux_power_kw: float
    ambient_temp: float
    has_overhead_line: bool
    available_charging_kw: float
    route_id: int


class ParquetDataLoader:
    def __init__(self):
        pass

    def load_trolleybus_data(self, parquet_file: str) -> List[RealOperatingCondition]:
        print(f"Loading data from {parquet_file}...")
        df = pd.read_parquet(parquet_file)

        print(f"Loaded {len(df)} rows")
        print(f"Columns: {list(df.columns)}")

        conditions = []
        start_time = df['datetime'].iloc[0]

        for _, row in df.iterrows():
            time_hours = (row['datetime'] - start_time) / (1000 * 3600)

            aux_power = (row['heating_power_kw'] +
                         row['aircond_power_kw'] +
                         row['lv_aux_power_kw'] +
                         row['hv_aux_power_kw'])

            conditions.append(RealOperatingCondition(
                time_hours=time_hours,
                speed_kmh=row['velocity_kmh'],
                total_power_kw=row['power_consumption_kw'],
                traction_power_kw=row['traction_power_kw'],
                aux_power_kw=aux_power,
                ambient_temp=row['ambient_air_temp_degc'],
                has_overhead_line=row['has_catenary'],
                available_charging_kw=row['available_catenary_power_kw'],
                route_id=row['route_id']
            ))

        return conditions

    def get_data_summary(self, conditions: List[RealOperatingCondition]) -> dict:
        powers = [c.total_power_kw for c in conditions]
        temps = [c.ambient_temp for c in conditions]
        speeds = [c.speed_kmh for c in conditions]
        catenary_usage = sum(1 for c in conditions if c.has_overhead_line) / len(conditions)

        return {
            'duration_hours': conditions[-1].time_hours,
            'avg_power_kw': sum(powers) / len(powers),
            'max_power_kw': max(powers),
            'avg_speed_kmh': sum(speeds) / len(speeds),
            'avg_temp_c': sum(temps) / len(temps),
            'catenary_coverage_percent': catenary_usage * 100,
            'total_data_points': len(conditions)
        }