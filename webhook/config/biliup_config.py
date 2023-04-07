from dataclasses import dataclass, field, InitVar
from datetime import datetime
from fnmatch import fnmatch
from itertools import chain
from pathlib import Path
from typing import Optional

import yaml
from boltons.iterutils import first

from ..event import Event
from ..util import DictionaryConvertible

BILIUP_CONFIG_DIR = Path("/etc/biliup").resolve(strict=True)


def custom_fmtstr(string: str, date: datetime, title: str, streamer: str) -> str:
    return (
        date.strftime(string.encode("unicode-escape").decode())
        .encode()
        .decode("unicode-escape")
        .format(title=title, streamer=streamer)
    )


@dataclass
class BiliupConfig(DictionaryConvertible):
    line: Optional[str] = field(init=False)
    limit: Optional[int] = field(init=False)
    user_cookie: Path = field(init=False)
    copyright: Optional[int] = field(init=False)
    source: Optional[str] = field(init=False)
    tid: Optional[int] = field(init=False)
    cover: Optional[str] = field(init=False)
    title: Optional[str] = field(init=False)
    desc: Optional[str] = field(init=False)
    dynamic: Optional[str] = field(init=False)
    tag: Optional[str] = field(init=False)
    dtime: Optional[int] = field(init=False)
    dolby: Optional[int] = field(init=False)
    hires: Optional[int] = field(init=False)
    no_reprint: Optional[int] = field(init=False)
    open_elec: Optional[int] = field(init=False)
    event: InitVar[Event]
    config_path: InitVar[Path]

    def __post_init__(self, event: Event, config_path: Path):
        with open(config_path) as f:
            config = yaml.safe_load(f)

        event_date = event.get_date()
        event_title = event.get_title()
        event_streamer = event.get_streamer()
        _, streamer_data = first(
            config.get("streamers", dict()).items(),
            default=(str(), dict()),
            key=lambda item: fnmatch(event_streamer, item[0]),
        )

        self.line = config.get("line")
        self.limit = config.get("limit")
        self.user_cookie = (
            BILIUP_CONFIG_DIR.joinpath(user_cookie).resolve(strict=True)
            if (user_cookie := streamer_data.get("user_cookie"))
            else BILIUP_CONFIG_DIR.joinpath("cookies.json")
        )
        self.copyright = streamer_data.get("copyright")
        self.source = streamer_data.get("source")
        self.tid = streamer_data.get("tid")
        self.cover = streamer_data.get("cover")
        self.title = (
            custom_fmtstr(title, event_date, event_title, event_streamer)
            if (title := streamer_data.get("title"))
            else None
        )
        self.desc = (
            custom_fmtstr(desc, event_date, event_title, event_streamer)
            if (desc := streamer_data.get("desc"))
            else None
        )
        self.dynamic = streamer_data.get("dynamic")
        self.tag = (",".join(tag) if isinstance(tag, list) else tag) if (tag := streamer_data.get("tag")) else None
        self.dtime = streamer_data.get("dtime")
        self.dolby = streamer_data.get("dolby")
        self.hires = streamer_data.get("hires")
        self.no_reprint = streamer_data.get("no_reprint")
        self.open_elec = streamer_data.get("open_elec")

    def to_command_args(self) -> list[str]:
        data = self.to_dict()
        data.pop("user_cookie")

        return list(chain.from_iterable([f"--{k.replace('_', '-')}", str(v)] for k, v in data.items() if v is not None))
