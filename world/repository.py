"""Everything that loaded correctly, plus every error that did not.

The application never crashes on a bad file: the error is recorded here
(with file and line) and loading continues with the next file.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TypeVar

from instinct.errors import SourceError
from .element_types import ElementType, ObjectType, TerrainType
from .layout import MapLayout
from .loaders import FileLoader, MapLoader, ObjectLoader, TerrainLoader

T = TypeVar("T")


class Repository:
    # Objects in a map sit on the "first declared terrain". Names of extra terrains
    # must not change what a teacher's map means, so the base terrain wins.
    BASE_TERRAIN = "Grass"

    def __init__(self) -> None:
        self._elements: dict[str, ElementType] = {}   # name -> terrain or object
        self._by_char: dict[str, ElementType] = {}
        self._maps: dict[str, MapLayout] = {}
        self.errors: list[SourceError] = []

    # ---- queries -------------------------------------------------------
    @property
    def terrains(self) -> list[TerrainType]:
        return [e for e in self._elements.values() if isinstance(e, TerrainType)]

    @property
    def objects(self) -> list[ObjectType]:
        return [e for e in self._elements.values() if isinstance(e, ObjectType)]

    @property
    def maps(self) -> list[MapLayout]:
        return list(self._maps.values())

    @property
    def default_terrain(self) -> TerrainType | None:
        terrains = self.terrains
        for terrain in terrains:
            if terrain.name == self.BASE_TERRAIN:
                return terrain
        return terrains[0] if terrains else None

    def find_by_char(self, char: str) -> ElementType | None:
        return self._by_char.get(char)

    def find_element(self, name: str) -> ElementType | None:
        return self._elements.get(name)

    # ---- registration (raise SourceError on conflicts) ------------------
    def register_element(self, element: ElementType) -> None:
        if element.name in self._elements:
            other = self._elements[element.name]
            raise SourceError(
                f"name '{element.name}' is already used by {other.source}",
                element.lines["name"], element.source,
            )
        if element.char in self._by_char:
            other = self._by_char[element.char]
            raise SourceError(
                f"char {element.char!r} is already used by '{other.name}' ({other.source})",
                element.lines["char"], element.source,
            )
        self._elements[element.name] = element
        self._by_char[element.char] = element

    def register_map(self, layout: MapLayout) -> None:
        if layout.name in self._maps:
            raise SourceError(
                f"map name '{layout.name}' is already used by {self._maps[layout.name].source}",
                1, layout.source,
            )
        self._maps[layout.name] = layout

    # ---- loading -------------------------------------------------------
    def load_all(self, root: str | Path) -> "Repository":
        """Terrains, then objects, then maps (maps need the other two)."""
        root = Path(root)
        self._load_directory(root / "terrains", TerrainLoader(), self.register_element)
        self._load_directory(root / "objects", ObjectLoader(), self.register_element)
        self._load_directory(root / "maps", MapLoader(self), self.register_map)
        return self

    def _load_directory(
        self, directory: Path, loader: FileLoader[T], register: Callable[[T], None]
    ) -> None:
        if not directory.is_dir():
            self.errors.append(SourceError("directory not found", None, directory.name))
            return
        files = sorted(
            (p for p in directory.iterdir()
             if p.is_file() and p.suffix.lower() == loader.extension),
            key=lambda p: p.name.lower(),  # deterministic order
        )
        for path in files:
            try:
                register(loader.load(path))
            except SourceError as error:
                self.errors.append(error)
