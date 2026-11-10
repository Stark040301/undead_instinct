"""Event log and observer support."""

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Event:
    name: str
    payload: dict[str, object] = field(default_factory=dict)


class EventLog:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self._observers: list[Callable[[Event], None]] = []

    def emit(self, event: Event) -> None:
        self.events.append(event)
        for observer in self._observers:
            observer(event)

    def subscribe(self, observer: Callable[[Event], None]) -> None:
        self._observers.append(observer)
