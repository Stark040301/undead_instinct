"""Terrain and occupant layers for the world grid."""


class World:
    def __init__(self, width: int = 0, height: int = 0) -> None:
        self.width = width
        self.height = height
        self.terrain: list[list[object | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.occupants: list[list[object | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
