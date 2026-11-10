"""Registries for language-visible actions, functions, perceptions, and constants."""


class Catalog:
    def __init__(self) -> None:
        self.actions: dict[str, object] = {}
        self.functions: dict[str, object] = {}
        self.perceptions: dict[str, object] = {}
        self.constants: dict[str, int | str] = {}
