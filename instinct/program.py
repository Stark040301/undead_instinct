"""Compiled Instinct program representation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Program:
    instructions: list[Any] = field(default_factory=list)
    labels: dict[str, int] = field(default_factory=dict)

    def resolve_labels(self) -> None:
        self.labels = {
            instruction.name: index
            for index, instruction in enumerate(self.instructions)
            if hasattr(instruction, "name")
        }
