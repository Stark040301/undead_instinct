"""File loaders. Each one turns text into a validated object or raises SourceError.

`parse(text, source)` is pure (easy to test); `load(path)` adds file reading.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, Generic, Mapping, Protocol, TypeVar

from instinct.errors import SourceError
from instinct.keyvalue import parse_entries
from .element_types import ElementType, ObjectType, TerrainType
from .layout import MapLayout

T = TypeVar("T")
_INTEGER = re.compile(r"[+-]?[0-9]+")


class FileLoader(ABC, Generic[T]):
    extension: ClassVar[str]

    def load(self, path: Path) -> T:
        source = f"{path.parent.name}/{path.name}"
        try:
            text = path.read_text(encoding="utf-8-sig")  # tolerate a BOM
        except UnicodeDecodeError:
            raise SourceError("file is not valid UTF-8", None, source) from None
        except OSError as exc:
            raise SourceError(f"cannot read file ({exc.strerror})", None, source) from None
        return self.parse(text, source)

    @abstractmethod
    def parse(self, text: str, source: str) -> T: ...


class ElementTypeLoader(FileLoader[ElementType]):
    """Shared logic for .te and .ob. Subclasses are pure configuration."""

    name_key: ClassVar[str]
    element_class: ClassVar[type[ElementType]]
    int_keys: ClassVar[Mapping[str, int]]  # integer key -> minimum allowed value

    def parse(self, text: str, source: str) -> ElementType:
        entries = parse_entries(text, source)
        fields: dict[str, str] = {}
        lines: dict[str, int] = {}
        for entry in entries:
            if entry.key in fields:
                raise SourceError(
                    f"duplicate key '{entry.key}' (first declared on line {lines[entry.key]})",
                    entry.line, source,
                )
            fields[entry.key] = entry.value
            lines[entry.key] = entry.line

        anchor = entries[0].line if entries else 1
        for key in (self.name_key, "char", *self.int_keys):
            if key not in fields:
                raise SourceError(f"missing required key '{key}'", anchor, source)

        char = fields.pop("char")
        if len(char) != 1:
            raise SourceError(f"'char' must be a single character, got {char!r}", lines["char"], source)

        name = fields.pop(self.name_key)
        ints = {
            key: self._parse_int(key, fields.pop(key), minimum, lines[key], source)
            for key, minimum in self.int_keys.items()
        }
        lines["name"] = lines[self.name_key]
        return self.element_class(
            name=name, char=char, extra=fields, lines=lines, source=source, **ints
        )

    @staticmethod
    def _parse_int(key: str, value: str, minimum: int, line: int, source: str) -> int:
        if not _INTEGER.fullmatch(value):
            raise SourceError(f"'{key}' must be an integer, got {value!r}", line, source)
        number = int(value)
        if number < minimum:
            raise SourceError(f"'{key}' must be at least {minimum}, got {number}", line, source)
        return number


class TerrainLoader(ElementTypeLoader):
    extension = ".te"
    name_key = "terrain"
    element_class = TerrainType
    int_keys = {"resource_max": 1, "regen": 0}


class ObjectLoader(ElementTypeLoader):
    extension = ".ob"
    name_key = "object"
    element_class = ObjectType
    int_keys = {"resource_max": 1}


class ElementCatalog(Protocol):
    """What the map loader needs from whoever knows the loaded elements."""

    @property
    def default_terrain(self) -> TerrainType | None: ...

    def find_by_char(self, char: str) -> ElementType | None: ...


class MapLoader(FileLoader[MapLayout]):
    """First line = name, then one row per line, all the same length.

    '#' is a plain map character here (the rock), so there are NO comments in maps.
    """

    extension = ".map"

    def __init__(self, catalog: ElementCatalog):
        self._catalog = catalog

    def parse(self, text: str, source: str) -> MapLayout:
        lines = text.split("\n")
        while lines and not lines[-1].strip():  # trailing blank lines are harmless
            lines.pop()
        if not lines or not lines[0].strip():
            raise SourceError("the first line must be the map name", 1, source)
        if len(lines) == 1:
            raise SourceError("the map has no rows", 1, source)

        name = lines[0].strip()
        default = self._catalog.default_terrain
        terrain_rows, object_rows = [], []
        width = None

        for number, raw in enumerate(lines[1:], start=2):
            row = raw.rstrip()  # whitespace can't be a char, so trailing blanks are noise
            if width is None:
                if not row:
                    raise SourceError("empty row", number, source)
                width = len(row)
            elif len(row) != width:
                raise SourceError(
                    f"row has {len(row)} cells but the first row has {width}", number, source
                )

            terrains, objects = [], []
            for column, char in enumerate(row, start=1):
                element = self._catalog.find_by_char(char)
                if element is None:
                    raise SourceError(
                        f"unknown character {char!r} (column {column}): "
                        "no loaded terrain or object declares it",
                        number, source,
                    )
                terrain, obj = element.cell_for(default)
                if terrain is None:
                    raise SourceError(
                        f"object character {char!r} (column {column}) needs a terrain "
                        "to sit on, but no terrain is loaded",
                        number, source,
                    )
                terrains.append(terrain)
                objects.append(obj)
            terrain_rows.append(tuple(terrains))
            object_rows.append(tuple(objects))

        return MapLayout(name, tuple(terrain_rows), tuple(object_rows), source)
