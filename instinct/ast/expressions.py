"""Expression nodes for Instinct programs."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class Expr(ABC):
    @abstractmethod
    def evaluate(self, context: object) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class Literal(Expr):
    value: int | str | bool

    def evaluate(self, context: object) -> int | str | bool:
        del context
        return self.value


@dataclass(frozen=True)
class Variable(Expr):
    name: str

    def evaluate(self, context: object) -> Any:
        return getattr(context, self.name)


@dataclass(frozen=True)
class Unary(Expr):
    operator: str
    operand: Expr

    def evaluate(self, context: object) -> Any:
        value = self.operand.evaluate(context)
        if self.operator == "not":
            return not value
        if self.operator == "-":
            return -value
        raise ValueError(f"Unknown unary operator: {self.operator}")


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: str
    right: Expr

    def evaluate(self, context: object) -> Any:
        left = self.left.evaluate(context)
        right = self.right.evaluate(context)
        operations = {
            "+": lambda: left + right,
            "-": lambda: left - right,
            "*": lambda: left * right,
            "/": lambda: left // right,
            "==": lambda: left == right,
            "!=": lambda: left != right,
            "<": lambda: left < right,
            "<=": lambda: left <= right,
            ">": lambda: left > right,
            ">=": lambda: left >= right,
            "and": lambda: left and right,
            "or": lambda: left or right,
        }
        try:
            return operations[self.operator]()
        except KeyError as error:
            raise ValueError(f"Unknown binary operator: {self.operator}") from error


@dataclass(frozen=True)
class Call(Expr):
    name: str
    arguments: tuple[Expr, ...] = ()

    def evaluate(self, context: object) -> Any:
        function = getattr(context, self.name)
        return function(*(argument.evaluate(context) for argument in self.arguments))
