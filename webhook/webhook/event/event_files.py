from dataclasses import dataclass
from pathlib import Path

from ..util import DictionaryConvertible


@dataclass
class EventFiles(DictionaryConvertible):
    data: Path
    event: Path
    danmaku: Path
    burned: Path
    subtitles: Path
    error_log: Path

    def __init__(self, data_path: Path):
        self.data = data_path
        self.event = data_path.with_suffix(".json")
        self.danmaku = data_path.with_suffix(".xml")
        self.burned = data_path.with_suffix(".mp4")
        self.subtitles = data_path.with_suffix(".ass")
        self.error_log = data_path.with_suffix(".txt")

    def get_video_paths(self) -> list[Path]:
        return [self.data, self.burned]

    def get_metadata_paths(self) -> list[Path]:
        return [self.event, self.danmaku, self.subtitles, self.error_log]
