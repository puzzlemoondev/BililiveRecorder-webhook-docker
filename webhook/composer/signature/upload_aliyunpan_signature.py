from pathlib import Path
from typing import Optional

from celery.canvas import Signature as CelerySignature

from .base import Signature
from ...config import Config
from ...task import UploadAliyunpanTaskInput
from ...tasks import upload_aliyunpan


class UploadAliyunpanSignature(Signature):
    def __init__(self, config: Config, path: Path):
        self.config = config
        self.path = path

    @property
    def is_valid(self) -> bool:
        return self.config.aliyunpan_rtoken is not None

    def get(self) -> Optional[CelerySignature]:
        if not self.is_valid:
            return

        input = UploadAliyunpanTaskInput(
            path=str(self.path), remote_dir=self.config.aliyunpan_upload_dir, rtoken=self.config.aliyunpan_rtoken
        )
        return upload_aliyunpan.si(input.to_dict())
