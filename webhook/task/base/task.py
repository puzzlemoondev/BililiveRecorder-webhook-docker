from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic

from ...util import DictionaryConvertible


@dataclass
class Input(DictionaryConvertible):
    pass


@dataclass
class Output(DictionaryConvertible):
    skipped: bool


T = TypeVar("T", bound=Input)
R = TypeVar("R", bound=Output)


class Task(ABC, Generic[T, R]):
    def __init__(self, input: T):
        self.input = input

    @abstractmethod
    def run(self) -> R:
        pass
