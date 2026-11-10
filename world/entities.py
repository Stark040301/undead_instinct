"""Entities that occupy the world."""

from dataclasses import dataclass


@dataclass
class Entity:
    name: str
    reserve: int = 0


class Terrain(Entity):
    regeneration: int = 0


class WorldObject(Entity):
    depletion: int = 1


class Creature(Entity):
    health: int = 1
    age: int = 0
