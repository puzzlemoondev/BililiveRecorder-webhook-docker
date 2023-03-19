import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    baidupcs_bduss: Optional[str] = field(init=False)
    baidupcs_stoken: Optional[str] = field(init=False)
    baidupcs_max_upload_parallel: Optional[str] = field(init=False)
    aliyunpan_rtoken: Optional[str] = field(init=False)
    burn_danmaku: bool = field(init=False)
    bilibili_upload_burned: bool = field(init=False)
    remove_local: bool = field(init=False)

    def __post_init__(self):
        self.baidupcs_bduss = os.environ.get("BAIDUPCS_BDUSS") or None
        self.baidupcs_stoken = os.environ.get("BAIDUPCS_STOKEN") or None
        self.baidupcs_max_upload_parallel = os.environ.get("BAIDUPCS_MAX_UPLOAD_PARALLEL")
        self.aliyunpan_rtoken = os.environ.get("ALIYUNPAN_RTOKEN") or None
        self.burn_danmaku = os.environ.get("BURN_DANMAKU", "0") != "0"
        self.bilibili_upload_burned = os.environ.get("BILIBILI_UPLOAD_BURNED", "0") != "0"
        self.remove_local = os.environ.get("REMOVE_LOCAL", "0") != "0"
