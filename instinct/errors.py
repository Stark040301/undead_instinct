"""Errors shared by every loader (and by the compiler)."""
from __future__ import annotations


class SourceError(Exception):
    """A problem found in a text file, reported with its location.

    `line` is 1-based and may be None for file-level problems
    (unreadable file, missing directory).
    """

    def __init__(self, message: str, line: int | None = None, source: str | None = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.source = source

    def __str__(self) -> str:
        where = self.source or "<input>"
        if self.line is not None:
            where += f":{self.line}"
        return f"{where}: {self.message}"
