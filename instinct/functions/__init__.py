"""Built-in functions exposed to Instinct programs."""

from abc import ABC, abstractmethod
from typing import Any


class Function(ABC):
    @abstractmethod
    def evaluate(self, context: object, *arguments: object) -> Any:
        raise NotImplementedError


class See(Function):
    def evaluate(self, context: object, *arguments: object) -> Any:
        return context.see(*arguments)


class Name(Function):
    def evaluate(self, context: object, *arguments: object) -> Any:
        return context.name(*arguments)
