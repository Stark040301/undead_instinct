"""Line-oriented tokenizer for Instinct source files."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int


def tokenize(source: str) -> list[Token]:
    """Tokenize source; parsing rules are intentionally handled by parser.py."""
    tokens: list[Token] = []
    for line_number, line in enumerate(source.splitlines(), 1):
        for value in line.split():
            tokens.append(Token("word", value, line_number))
    return tokens
