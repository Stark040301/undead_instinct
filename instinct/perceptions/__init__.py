"""Built-in perceptions exposed to Instinct programs."""

from abc import ABC, abstractmethod
from typing import Any


class Perception(ABC):
    @abstractmethod
    def read(self, context: object) -> Any:
        raise NotImplementedError


class SelfPerception(Perception):
    def read(self, context: object) -> Any:
        return context.self_state


class WorldPerception(Perception):
    def read(self, context: object) -> Any:
        return context.world_state


class NearbyPerception(Perception):
    def read(self, context: object) -> Any:
        return context.nearby
