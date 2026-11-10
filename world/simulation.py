"""Tick-based world simulation."""

import random

from .grid import World


class Simulation:
    def __init__(self, world: World, seed: int | None = None) -> None:
        self.world = world
        self.random = random.Random(seed)
        self.tick_number = 0

    def tick(self) -> None:
        self.tick_number += 1
