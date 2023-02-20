from dataclasses import dataclass, asdict
from datetime import datetime
from fnmatch import fnmatch
from itertools import chain
from pathlib import Path
from typing import Optional

import yaml

from ..event import Event
from ..util import filter_suffixes

BILIUP_CONFIG_DIR = Path("/etc/biliup")


def custom_fmtstr(string: str, date: datetime, title: str, streamer: str):
    return (
        date.strftime(string.encode("unicode-escape").decode())
        .encode()
        .decode("unicode-escape")
        .format(title=title, streamer=streamer)
    )


@dataclass
class BiliupConfig:
    line: Optional[str] = None
    limit: Optional[int] = None
    user_cookie: Path = BILIUP_CONFIG_DIR.joinpath("cookies.json")
    copyright: Optional[int] = None
    source: Optional[str] = None
    tid: Optional[int] = None
    cover: Optional[str] = None
    title: Optional[str] = None
    desc: Optional[str] = None
    dynamic: Optional[str] = None
    tag: Optional[str] = None
    dtime: Optional[int] = None
    dolby: Optional[int] = None
    hires: Optional[int] = None
    no_reprint: Optional[int] = None
    open_elec: Optional[int] = None

    def __init__(self, event: Event):
        config = dict()
        config_path = next(
            filter_suffixes(BILIUP_CONFIG_DIR.glob("config.*"), ".yml", ".yaml"),
            None,
        )
        if config_path is not None:
            with open(config_path) as f:
                config = yaml.safe_load(f)

        event_date = event.get_date()
        event_title = event.get_title()
        event_streamer = event.get_streamer()
        streamer_data = next(
            (
                v
                for k, v in config.get("streamers", dict()).items()
                if fnmatch(event_streamer, k)
            ),
            dict(),
        )

        if line := config.get("line"):
            self.line = line
        if limit := config.get("limit"):
            self.limit = limit
        if user_cookie := streamer_data.get("user_cookie"):
            # force resolve path since file is expected to exist.
            self.user_cookie = BILIUP_CONFIG_DIR.joinpath(user_cookie).resolve(
                strict=True
            )
        if copyright := streamer_data.get("copyright"):
            self.copyright = copyright
        if source := streamer_data.get("source"):
            self.source = source
        if tid := streamer_data.get("tid"):
            self.tid = tid
        if cover := streamer_data.get("cover"):
            self.cover = cover
        if title := streamer_data.get("title"):
            self.title = custom_fmtstr(title, event_date, event_title, event_streamer)
        if desc := streamer_data.get("desc"):
            self.desc = custom_fmtstr(desc, event_date, event_title, event_streamer)
        if dynamic := streamer_data.get("dynamic"):
            self.dynamic = dynamic
        if tag := streamer_data.get("tag"):
            if isinstance(tag, list):
                tag = ",".join(tag)
            self.tag = tag
        if dtime := streamer_data.get("dtime"):
            self.dtime = dtime
        if dolby := streamer_data.get("dolby"):
            self.dolby = dolby
        if hires := streamer_data.get("hires"):
            self.hires = hires
        if no_reprint := streamer_data.get("no_reprint"):
            self.no_reprint = no_reprint
        if open_elec := streamer_data.get("open_elec"):
            self.open_elec = open_elec

    def to_command_args(self) -> list[str]:
        return list(
            chain.from_iterable(
                [f"--{k.replace('_', '-')}", str(v)]
                for k, v in asdict(self).items()
                if k != "user_cookie" and v is not None
            )
        )
