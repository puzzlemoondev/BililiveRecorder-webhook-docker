from collections import UserDict
from dataclasses import replace
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Optional

import yaml
from biliup.plugins.bili_webup import Data

from ..event import Event


def custom_fmtstr(string: str, date: datetime, title: str, streamer: str):
    return (
        date.strftime(string.encode("unicode-escape").decode())
        .encode()
        .decode("unicode-escape")
        .format(title=title, streamer=streamer)
    )


class BiliupConfig(UserDict):
    def __init__(self, path: Path):
        with open(path) as f:
            super().__init__(yaml.safe_load(f))

    def get_user(self):
        return self.data["user"]

    def to_data(self, event: Event) -> Data:
        event_date = event.get_date()
        event_title = event.get_title()
        event_streamer = event.get_streamer()

        streamer_data = self._get_streamer_data(event_streamer)
        if streamer_data is None:
            raise ValueError(
                f"config for {event_streamer} not found inside config yaml"
            )

        data = Data()
        if copyright := streamer_data.get("copyright"):
            data = replace(data, copyright=int(copyright))
        if source := streamer_data.get("source"):
            data = replace(data, source=source)
        if tid := streamer_data.get("tid"):
            data = replace(data, tid=int(tid))
        if cover_path := streamer_data.get("cover_path"):
            data = replace(data, cover=cover_path)
        if title := streamer_data.get("title"):
            data = replace(
                data,
                title=custom_fmtstr(title, event_date, event_title, event_streamer),
            )
        if desc_format_id := streamer_data.get("desc_format_id"):
            data = replace(data, desc_format_id=int(desc_format_id))
        if description := streamer_data.get("description"):
            data = replace(
                data,
                desc=custom_fmtstr(
                    description, event_date, event_title, event_streamer
                ),
            )
        if dynamic := streamer_data.get("dynamic"):
            data = replace(data, dynamic=dynamic)
        if tags := streamer_data.get("tags"):
            data = replace(data, tag=tags)
        if dtime := streamer_data.get("dtime"):
            data = replace(data, dtime=dtime)

        return data

    def _get_streamer_data(self, streamer: str) -> Optional[dict]:
        streamer_dict = self.data["streamers"]
        for streamer_key in streamer_dict.keys():
            if fnmatch(streamer, streamer_key):
                return streamer_dict[streamer_key]
