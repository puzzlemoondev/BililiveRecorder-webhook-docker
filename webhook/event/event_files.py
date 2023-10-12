from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

from boltons.setutils import IndexedSet

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

    def get_files(self) -> IndexedSet[Path]:
        return IndexedSet(self.to_dict().values())

    def get_burn_files(self) -> IndexedSet[Path]:
        return IndexedSet([self.burned, self.subtitles])

    def get_burn_dependencies(self) -> IndexedSet[Path]:
        return IndexedSet([self.data, self.danmaku])

    def is_danmaku_empty(self) -> bool:
        tree = ElementTree.parse(self.danmaku)
        root = tree.getroot()
        return not len(root.findall("d"))
