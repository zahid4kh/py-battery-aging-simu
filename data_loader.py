import pandas as pd
from typing import List
from datetime import datetime
from data.operating_condition import OperatingCondition


class DataLoader:
    def __init__(self, parquet_file_path: str):
        self.parquet_file_path = parquet_file_path
        self.df = None

    def load_data(self) -> pd.DataFrame:
        self.df = pd.read_parquet(self.parquet_file_path)
        print(f"Loaded {len(self.df)} data points from {self.parquet_file_path}")
        return self.df

    def determine_battery_operation(self, row) -> str:
        power_needed = row['power_consumption_kw']
        has_catenary = row['has_catenary']
        available_power = row['available_catenary_power_kw']

        if power_needed < 0:
            return "regenerating"  
        elif has_catenary and available_power >= power_needed:
            return "catenary_powered"
        else:
            return "battery_discharging"

    def convert_to_operating_conditions(self) -> List[OperatingCondition]:
        if self.df is None:
            self.load_data()

        conditions = []
        start_time = self.df['duration_hours'].index[0].timestamp()

        for index, row in self.df.iterrows():
            current_time = index.timestamp()
            time_hours = (current_time - start_time) / 3600.0

            battery_mode = self.determine_battery_operation(row)

            condition = OperatingCondition(
                time=time_hours,
                ambient_temp=row['ambient_air_temp_degc'],
                power_consumption_kw=row['power_consumption_kw'],
                available_catenary_power_kw=row['available_catenary_power_kw'],
                has_catenary=row['has_catenary'],
                battery_operation_mode=battery_mode
            )

            conditions.append(condition)

        start_hm = datetime.fromtimestamp(start_time).strftime("%H:%M:%S")
        end_time = self.df['duration_hours'].index[-1].timestamp()
        end_hm = datetime.fromtimestamp(end_time).strftime("%H:%M:%S")

        print(f"Start time: {start_hm}")
        print(f"End time: {end_hm}")
        print(f"Converted {len(conditions)} operating conditions")
        print(f"Duration: {conditions[-1].time:.2f} hours")
        return conditions
