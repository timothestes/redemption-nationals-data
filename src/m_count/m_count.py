from dataclasses import dataclass

from src.m_count.decklist import Decklist
from src.m_count.spectrograph_simulation import SpectrographSimulation


@dataclass
class SimulationResults:
    m_count: float
    # whiff_percentage: float
    decklist: Decklist


def get_simulation_results(
    decklist_path: str,
    n_simulations: int,
    cycler_logic: str,
    crowds_ineffectiveness_weight: float,
    matthew_fizzle_rate: float,
) -> SimulationResults:
    simulation_results = SimulationResults(m_count=0, decklist=None)
    simulation = SpectrographSimulation(
        deck_file_path=decklist_path,
        n_simulations=n_simulations,
        cycler_logic=cycler_logic,
        crowds_ineffectiveness_weight=crowds_ineffectiveness_weight,
        matthew_fizzle_rate=matthew_fizzle_rate,
    )
    simulation.create_empty_log_file()
    simulation.initialize_decklist()
    simulation.run(only_matthew_results=True)
    simulation.print_results()
    simulation_results.m_count = simulation.m_count
    # simulation.whiff_percentage = simulation.whiff_percentage
    simulation_results.decklist = simulation.decklist

    return simulation_results
