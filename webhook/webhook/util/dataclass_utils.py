from dataclasses import dataclass
from typing import Self

from dataclass_factory import Factory


@dataclass
class DictionaryConvertible:
    factory = Factory()

    def to_dict(self) -> dict:
        return self.factory.dump(self)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls.factory.load(data, cls)
