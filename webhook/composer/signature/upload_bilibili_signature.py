from pathlib import Path
from typing import Optional

from celery.canvas import Signature as CelerySignature

from .base import Signature
from ...config import BILIUP_CONFIG_DIR
from ...event import Event
from ...task import UploadBilibiliTaskInput
from ...tasks import upload_bilibili
from ...util import filter_suffixes


class UploadBilibiliSignature(Signature):
    def __init__(self, event: Event, path: Path):
        self.event = event
        self.path = path
        self.config_path = next(filter_suffixes(BILIUP_CONFIG_DIR.glob("config.*"), ".yml", ".yaml"), None)

    @property
    def is_valid(self) -> bool:
        return self.config_path is not None

    def get(self) -> Optional[CelerySignature]:
        if not self.is_valid:
            return

        input = UploadBilibiliTaskInput(
            event_json=self.event.data,
            config_path=str(self.config_path),
            path=str(self.path),
        )
        return upload_bilibili.si(input.to_dict())
