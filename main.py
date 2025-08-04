from simulation_runner import SimulationRunner
from data.simulation_parameters import SimulationParameters

def main():
    runner = SimulationRunner()

    soft = SimulationParameters(
        charging_c_rate=0.3,
        regen_c_rate=0.15,
        discharge_c_rate=0.2,
        overhead_coverage=0.25,  # 25% overhead coverage
        charging_soc_threshold=0.45,  # Start charging at 45%
        regen_soc_limit=0.80  # Stop regen at 80%
    )
    
    standard = SimulationParameters(
        charging_c_rate=0.5,
        regen_c_rate=0.2,
        discharge_c_rate=0.3,
        overhead_coverage=0.35,  # 35% overhead coverage
        charging_soc_threshold=0.40,  # Start charging at 40%
        regen_soc_limit=0.85  # Stop regen at 85%
    )
    
    rough = SimulationParameters(
        charging_c_rate=1.0,
        regen_c_rate=0.4,
        discharge_c_rate=0.5,
        overhead_coverage=0.50,  # 50% overhead coverage
        charging_soc_threshold=0.35,  # Start charging at 35%
        regen_soc_limit=0.90  # Stop regen at 90%
    )

    runner.run_simulation(
        duration_days=30.0,
        temperature=25.0,
        soc_window=(0.4, 0.8),
        sim_params=soft,
        bus_id="SOC40-80_Soft"
    )
    
    runner.run_simulation(
        duration_days=30.0,
        temperature=25.0,
        soc_window=(0.5, 0.75),
        sim_params=standard,
        bus_id="SOC50-75_Standard"
    )
    
    runner.run_simulation(
        duration_days=30.0,
        temperature=25.0,
        soc_window=(0.3, 0.9),
        sim_params=rough,
        bus_id="SOC30-90_Rough"
    )


if __name__ == "__main__":
    main()