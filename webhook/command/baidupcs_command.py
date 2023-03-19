from typing import Optional

from .cloud_storage_command import CloudStorageCommand


class BaidupcsCommand(CloudStorageCommand):
    def __init__(self, bduss: str, stoken: str, max_upload_parallel: Optional[str] = None):
        super().__init__("baidupcs")
        self.bduss = bduss
        self.stoken = stoken

        if max_upload_parallel:
            self("config", "set", "--max_upload_parallel", max_upload_parallel)

    def login(self) -> str:
        return super().login("-bduss", self.bduss, "-stoken", self.stoken)
