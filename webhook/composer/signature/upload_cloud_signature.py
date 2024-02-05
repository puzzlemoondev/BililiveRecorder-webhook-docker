from pathlib import Path

from .base import CompositeSignature
from .remove_signature import RemoveSignature
from .upload_aliyunpan_signature import UploadAliyunpanSignature
from .upload_baidupcs_signature import UploadBaidupcsSignature
from ...config import Config


class UploadCloudSignature(CompositeSignature):
    def __init__(self, config: Config, path: Path, remove_after=True):
        super().__init__(
            UploadAliyunpanSignature(config, path),
            UploadBaidupcsSignature(config, path),
        )
        self.config = config
        self.path = path
        if remove_after:
            self.callback = RemoveSignature(config, path)
