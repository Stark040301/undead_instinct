"""Execution of one creature's Instinct turn."""

from .program import Program


class Interpreter:
    def __init__(self, program: Program) -> None:
        self.program = program

    def run_turn(self, context: object) -> None:
        """Run one turn using the supplied world-facing context."""
        del context
