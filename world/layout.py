"""A loaded map, already resolved against the loaded terrains and objects."""
from __future__ import annotations

from dataclasses import dataclass

from .element_types import ObjectType, TerrainType


@dataclass(frozen=True)
class MapLayout:
    name: str
    terrains: tuple[tuple[TerrainType, ...], ...]          # [y][x]
    objects: tuple[tuple[ObjectType | None, ...], ...]     # [y][x]
    source: str = ""

    @property
    def height(self) -> int:
        return len(self.terrains)

    @property
    def width(self) -> int:
        return len(self.terrains[0])
