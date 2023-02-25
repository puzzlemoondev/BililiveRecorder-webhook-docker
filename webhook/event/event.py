import json
from collections import UserDict
from datetime import datetime
from pathlib import Path

from .event_files import EventFiles


class Event(UserDict):
    def __init__(self, data: dict, root: Path = Path("/rec")):
        super().__init__(data)
        self.root = root

    def get_date(self) -> datetime:
        return datetime.fromisoformat(self.data["EventData"]["FileOpenTime"])

    def get_title(self) -> str:
        return self.data["EventData"]["Title"]

    def get_streamer(self) -> str:
        return self.data["EventData"]["Name"]

    def get_event_files(self, ensure_data: bool = True) -> EventFiles:
        relative_path = self.data["EventData"]["RelativePath"]
        data_path = self.root.joinpath(relative_path).resolve(strict=ensure_data)
        return EventFiles(data=data_path)

    def save(self) -> Path:
        output_path = self.get_event_files(ensure_data=False).event
        with open(output_path, "w") as f:
            json.dump(self.data, f, indent=4, sort_keys=True, ensure_ascii=False)
        return output_path
