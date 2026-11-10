"""The `id value` line format shared by .te, .ob and the .ins header.

Rules:
  * blank lines and lines whose first non-blank character is '#' are ignored;
  * a line is `key value`; the value is the FIRST token after the key;
  * anything after the value must be empty or a comment starting with '#'.

Taking only the first token as the value is what lets `char #` work: the '#'
is the value, not the start of a comment.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import SourceError

# Letter or underscore first, then letters, digits or underscores.
_IDENTIFIER = re.compile(r"[^\W\d]\w*")


@dataclass(frozen=True)
class Entry:
    key: str
    value: str
    line: int


def parse_entry_line(raw: str, number: int, source: str) -> Entry | None:
    """Parse one line. Returns None for blanks and comments."""
    text = raw.strip()
    if not text or text.startswith("#"):
        return None
    parts = text.split(None, 1)
    key = parts[0]
    if not _IDENTIFIER.fullmatch(key):
        raise SourceError(f"invalid key {key!r}", number, source)
    if len(parts) == 1:
        raise SourceError(f"key '{key}' has no value", number, source)
    value, *tail = parts[1].split()
    if tail and not tail[0].startswith("#"):
        raise SourceError(
            f"unexpected text after the value of '{key}': {tail[0]!r}", number, source
        )
    return Entry(key, value, number)


def parse_entries(text: str, source: str) -> list[Entry]:
    entries = []
    # split("\n") instead of splitlines(): keeps line numbers identical to editors.
    for number, raw in enumerate(text.split("\n"), start=1):
        entry = parse_entry_line(raw, number, source)
        if entry is not None:
            entries.append(entry)
    return entries
