from .cloud_storage_command import CloudStorageCommand


class BaidupcsCommand(CloudStorageCommand):
    def __init__(self, bduss: str, stoken: str):
        super().__init__("baidupcs")
        self.bduss = bduss
        self.stoken = stoken

    def login(self) -> str:
        return super().login("-bduss", self.bduss, "-stoken", self.stoken)
