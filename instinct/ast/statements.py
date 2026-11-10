"""Statement nodes for Instinct programs."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .expressions import Expr


class Statement(ABC):
    @abstractmethod
    def execute(self, context: object) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class Goto(Statement):
    target: str

    def execute(self, context: object) -> None:
        context.goto(self.target)


@dataclass(frozen=True)
class IfGoto(Statement):
    condition: Expr
    target: str

    def execute(self, context: object) -> None:
        if self.condition.evaluate(context):
            context.goto(self.target)


@dataclass(frozen=True)
class Assign(Statement):
    name: str
    value: Expr

    def execute(self, context: object) -> None:
        setattr(context, self.name, self.value.evaluate(context))


@dataclass(frozen=True)
class ActionCall(Statement):
    name: str
    arguments: tuple[Expr, ...] = ()

    def execute(self, context: object) -> None:
        action = getattr(context, self.name)
        action(*(argument.evaluate(context) for argument in self.arguments))


@dataclass(frozen=True)
class Label(Statement):
    name: str

    def execute(self, context: object) -> None:
        del context
