from dataclasses import dataclass, asdict, fields
from typing import Self, Type, TypeVar

from boltons.cacheutils import LRU

T = TypeVar("T")


class DataclassFactory:
    cache = LRU()

    @classmethod
    def instantiate(cls, dataclass_name: Type[T], data: dict) -> T:
        if dataclass_name not in cls.cache:
            cls.cache[dataclass_name] = {f.name for f in fields(dataclass_name) if f.init}

        field_set = cls.cache[dataclass_name]
        filtered_data = {k: v for k, v in data.items() if k in field_set}
        return dataclass_name(**filtered_data)


@dataclass
class DictionaryConvertible:
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return DataclassFactory.instantiate(cls, data)
