"""Parser entry points for Instinct programs."""

from .lexer import tokenize
from .program import Program


def parse(source: str) -> Program:
    """Parse source into a program.

    Detailed header, statement, and expression parsing will be added without
    coupling this language package to the world or UI packages.
    """
    tokenize(source)
    return Program()
