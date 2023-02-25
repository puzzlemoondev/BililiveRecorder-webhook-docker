from typing import TypeVar, Iterable, Iterator, Optional

T = TypeVar("T")


def compact(iterable: Iterable[Optional[T]]) -> Iterator[T]:
    return filter(lambda x: x is not None, iterable)
