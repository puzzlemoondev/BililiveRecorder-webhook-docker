from abc import ABC, abstractmethod
from typing import Optional

from celery.canvas import Signature as CelerySignature


class Signature(ABC):
    @abstractmethod
    @property
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def get(self) -> Optional[CelerySignature]:
        pass
