"""Headless command-line entry points and console rendering."""

from world.simulation import Simulation


def run(simulation: Simulation, ticks: int = 1) -> None:
    for _ in range(ticks):
        simulation.tick()


def render_console(simulation: Simulation) -> str:
    return f"tick {simulation.tick_number}"
