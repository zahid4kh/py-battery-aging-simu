from data.simulation_parameters import SimulationParameters
from simulation_runner import SimulationRunner
import os

def main():

    runner = SimulationRunner()

    sim_params = SimulationParameters(
        battery_voltage=360.0,
        max_charge_c_rate=1.0,
        max_discharge_c_rate=2.0
    )

    path = "pfiles"
    pfiles = os.listdir(path=path)
    pfiles.sort(key=lambda f: int(f.split('-')[1].split('.')[0]))

    for file in pfiles:
        day_number = file.split("-")[1].split(".")[0]
        bus_id = f"March_Day{day_number}"

        print(f"Running simulation for file: {file} with bus_id: {bus_id}")
        
        runner.run_simulation(
            parquet_file_path=f"pfiles/{file}",
            soc_window=(0.3, 0.9),
            sim_params=sim_params,
            bus_id=bus_id
        )


if __name__ == "__main__":
    main()