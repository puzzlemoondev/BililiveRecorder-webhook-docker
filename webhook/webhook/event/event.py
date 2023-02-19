import json
from collections import UserDict
from datetime import datetime
from pathlib import Path
from typing import Iterator


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

    def get_data_path(self, strict: bool = True) -> Path:
        return self.root.joinpath(self.data["EventData"]["RelativePath"]).resolve(
            strict=strict
        )

    def get_metadata_paths(self) -> Iterator[Path]:
        data_path = self.get_data_path()
        for path in data_path.parent.glob(f"{data_path.stem}.*"):
            if path != data_path:
                yield path

    def save(self) -> Path:
        output_path = self.get_data_path().with_suffix(".json")
        with open(output_path, "w") as f:
            json.dump(self.data, f, indent=4, sort_keys=True, ensure_ascii=False)
        return output_path
