import os
from dataclasses import dataclass
from shlex import split


@dataclass
class Config:
    baidupcs_bduss: str
    baidupcs_stoken: str
    aliyunpan_rtoken: str
    burn_danmaku: bool
    danmaku_factory_args: list[str]
    bilibili_upload_burned: bool

    def __init__(self):
        self.baidupcs_bduss = os.environ.get("BAIDUPCS_BDUSS") or None
        self.baidupcs_stoken = os.environ.get("BAIDUPCS_STOKEN") or None
        self.aliyunpan_rtoken = os.environ.get("ALIYUNPAN_RTOKEN") or None
        self.burn_danmaku = os.environ.get("BURN_DANMAKU", "0") != "0"
        self.danmaku_factory_args = split(os.environ.get("DANMAKU_FACTORY_ARGS", ""))
        self.bilibili_upload_burned = (
            os.environ.get("BILIBILI_UPLOAD_BURNED", "0") != "0"
        )
