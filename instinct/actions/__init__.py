"""Built-in actions exposed to Instinct programs."""

from abc import ABC, abstractmethod


class Action(ABC):
    @abstractmethod
    def execute(self, context: object, *arguments: object) -> None:
        raise NotImplementedError


class Wait(Action):
    def execute(self, context: object, *arguments: object) -> None:
        context.wait(*arguments)


class Move(Action):
    def execute(self, context: object, *arguments: object) -> None:
        context.move(*arguments)


class Attack(Action):
    def execute(self, context: object, *arguments: object) -> None:
        context.attack(*arguments)


class Consume(Action):
    def execute(self, context: object, *arguments: object) -> None:
        context.consume(*arguments)


class Reproduce(Action):
    def execute(self, context: object, *arguments: object) -> None:
        context.reproduce(*arguments)


class Roar(Action):
    def execute(self, context: object, *arguments: object) -> None:
        context.roar(*arguments)


class Say(Action):
    def execute(self, context: object, *arguments: object) -> None:
        context.say(*arguments)
