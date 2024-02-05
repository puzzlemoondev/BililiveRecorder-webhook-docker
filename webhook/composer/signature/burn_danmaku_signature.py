from typing import Optional

from celery.canvas import Signature as CelerySignature

from .base import Signature
from ...config import Config
from ...event import Event
from ...task import BurnDanmakuTaskInput
from ...tasks import burn_danmaku


class BurnDanmakuSignature(Signature):
    def __init__(self, config: Config, event: Event):
        self.config = config
        self.event = event
        self.files = event.get_event_files()

    @property
    def is_valid(self) -> bool:
        return self.config.burn_danmaku and not self.files.is_danmaku_empty()

    def get(self) -> Optional[CelerySignature]:
        if not self.is_valid:
            return

        input = BurnDanmakuTaskInput(
            event_json=self.event.data,
        )
        return burn_danmaku.si(input.to_dict())
