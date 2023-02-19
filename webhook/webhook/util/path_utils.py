from pathlib import Path
from typing import Iterable, Iterator


def filter_suffixes(paths: Iterable[Path], *suffixes: str) -> Iterator[Path]:
    for path in paths:
        if path.is_file() and path.suffix in suffixes:
            yield path


def is_empty(path: Path) -> bool:
    if not (path.exists() and path.is_dir()):
        return False
    return len(list(path.iterdir())) == 0
