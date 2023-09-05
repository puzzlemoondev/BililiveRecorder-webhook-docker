import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    baidupcs_upload_dir: Optional[str] = field(init=False)
    baidupcs_bduss: Optional[str] = field(init=False)
    baidupcs_stoken: Optional[str] = field(init=False)
    baidupcs_max_upload_parallel: Optional[int] = field(init=False)
    aliyunpan_upload_dir: Optional[str] = field(init=False)
    aliyunpan_rtoken: Optional[str] = field(init=False)
    burn_danmaku: bool = field(init=False)
    bilibili_upload_burned: bool = field(init=False)
    remove_local: bool = field(init=False)

    def __post_init__(self):
        self.baidupcs_upload_dir = self.get_str_env("BAIDUPCS_UPLOAD_DIR")
        self.baidupcs_bduss = self.get_str_env("BAIDUPCS_BDUSS")
        self.baidupcs_stoken = self.get_str_env("BAIDUPCS_STOKEN")
        self.baidupcs_max_upload_parallel = self.get_int_env("BAIDUPCS_MAX_UPLOAD_PARALLEL")
        self.aliyunpan_upload_dir = self.get_str_env("ALIYUNPAN_UPLOAD_DIR")
        self.aliyunpan_rtoken = self.get_str_env("ALIYUNPAN_RTOKEN")
        self.burn_danmaku = self.get_boolean_flag_env("BURN_DANMAKU")
        self.bilibili_upload_burned = self.get_boolean_flag_env("BILIBILI_UPLOAD_BURNED")
        self.remove_local = self.get_boolean_flag_env("REMOVE_LOCAL")

    @staticmethod
    def get_str_env(key: str) -> Optional[str]:
        if value := os.environ.get(key):
            return value

    @staticmethod
    def get_boolean_flag_env(key: str) -> bool:
        return os.environ.get(key, "0") != "0"

    @staticmethod
    def get_int_env(key: str) -> Optional[int]:
        if value := os.environ.get(key):
            try:
                return int(value)
            except ValueError:
                pass
