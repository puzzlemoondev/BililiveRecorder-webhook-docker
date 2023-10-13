from celery.canvas import Signature

from .signature import (
    BurnDanmakuSignature,
    BurnAndUploadSignature,
    UploadAndBurnSignature,
    UploadSignature,
)
from ..config import Config
from ..event import Event


class Composer:
    def __init__(self, event: Event, config: Config):
        self.event = event
        self.config = config

    def __call__(self) -> Signature:
        burn_danmaku_signature = BurnDanmakuSignature(self.config, self.event)
        if burn_danmaku_signature.is_valid:
            if self.config.bilibili_upload_burned:
                return BurnAndUploadSignature(self.config, self.event, burn_danmaku_signature).get()
            return UploadAndBurnSignature(self.config, self.event, burn_danmaku_signature).get()
        return UploadSignature(self.config, self.event).get()
