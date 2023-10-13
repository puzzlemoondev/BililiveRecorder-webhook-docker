from pathlib import Path

from .upload_bilibili_signature import UploadBilibiliSignature
from .upload_cloud_signature import UploadCloudSignature
from ...config import Config
from ...event import Event


class UploadBilibiliAndCloudSignature(UploadCloudSignature):
    def __init__(self, config: Config, event: Event, path: Path, remove_after=True):
        super().__init__(config, path, remove_after)
        self.signatures = (UploadBilibiliSignature(event, path), *self.signatures)
