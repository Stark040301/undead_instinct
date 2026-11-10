"""Static definitions loaded from .te / .ob files.

These are *types* (immutable, shared). The live things on the grid
(Terrain, WorldObject, Creature instances with a mutable reserve).

The only difference between a terrain and an object is the extra `regen` key.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, kw_only=True)
class ElementType(ABC):
    name: str
    char: str
    resource_max: int
    # Unknown keys are kept (raw strings) so extensions can read their own attributes.
    extra: Mapping[str, str] = field(default_factory=dict, compare=False, repr=False)
    # key -> line number in the source file (for error reporting; "name" is always present).
    lines: Mapping[str, int] = field(default_factory=dict, compare=False, repr=False)
    source: str = field(default="", compare=False, repr=False)

    @abstractmethod
    def cell_for(self, default_terrain: "TerrainType | None"):
        """(terrain, object) of a map cell drawn with this element's char."""


@dataclass(frozen=True, kw_only=True)
class TerrainType(ElementType):
    regen: int

    def cell_for(self, default_terrain):
        return self, None


@dataclass(frozen=True, kw_only=True)
class ObjectType(ElementType):
    def cell_for(self, default_terrain):
        # Objects sit on the first declared terrain.
        return default_terrain, self
