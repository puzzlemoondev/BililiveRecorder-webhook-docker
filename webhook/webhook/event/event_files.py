from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from ..util import DictionaryConvertible


@dataclass
class EventFiles(DictionaryConvertible):
    data: Path
    event: Path = field(init=False)
    danmaku: Path = field(init=False)
    burned: Path = field(init=False)
    subtitles: Path = field(init=False)
    error_log: Path = field(init=False)

    def __post_init__(self):
        self.event = self.data.with_suffix(".json")
        self.danmaku = self.data.with_suffix(".xml")
        self.burned = self.data.with_suffix(".mp4")
        self.subtitles = self.data.with_suffix(".ass")
        self.error_log = self.data.with_suffix(".txt")

    def __iter__(self) -> Iterator[Path]:
        yield from self.to_dict().values()
