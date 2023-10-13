from pathlib import Path
from typing import Optional

from celery.canvas import Signature as CelerySignature

from .base import Signature
from ...config import Config
from ...task import RemoveTaskInput
from ...tasks import remove


class RemoveSignature(Signature):
    def __init__(self, config: Config, path: Path):
        self.config = config
        self.path = path

    @property
    def is_valid(self) -> bool:
        return self.config.remove_local

    def get(self) -> Optional[CelerySignature]:
        if not self.is_valid:
            return

        input = RemoveTaskInput(path=str(self.path))
        return remove.si(input.to_dict())
