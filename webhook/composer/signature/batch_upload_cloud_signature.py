from pathlib import Path

from .base import CompositeSignature
from .upload_cloud_signature import UploadCloudSignature
from ...config import Config


class BatchUploadCloudSignature(CompositeSignature):
    def __init__(self, config: Config, *paths: Path, remove_after=lambda path: True):
        super().__init__(*map(lambda path: UploadCloudSignature(config, path, remove_after(path)), paths))
