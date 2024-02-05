from pathlib import Path
from typing import Optional

from celery.canvas import Signature as CelerySignature

from .base import Signature
from ...config import Config
from ...task import UploadBaidupcsTaskInput
from ...tasks import upload_baidupcs


class UploadBaidupcsSignature(Signature):
    def __init__(self, config: Config, path: Path):
        self.config = config
        self.path = path

    @property
    def is_valid(self) -> bool:
        return bool(self.config.baidupcs_bduss and self.config.baidupcs_stoken)

    def get(self) -> Optional[CelerySignature]:
        if not self.is_valid:
            return

        input = UploadBaidupcsTaskInput(
            path=str(self.path),
            remote_dir=self.config.baidupcs_upload_dir,
            bduss=self.config.baidupcs_bduss,
            stoken=self.config.baidupcs_stoken,
            max_upload_parallel=self.config.baidupcs_max_upload_parallel,
        )
        return upload_baidupcs.si(input.to_dict())
