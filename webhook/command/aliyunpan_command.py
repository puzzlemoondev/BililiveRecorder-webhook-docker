from .cloud_storage_command import CloudStorageCommand


class AliyunpanCommand(CloudStorageCommand):
    def __init__(self, rtoken: str):
        super().__init__("aliyunpan")
        self.rtoken = rtoken

    def login(self) -> str:
        return self("-RefreshToken", self.rtoken)
