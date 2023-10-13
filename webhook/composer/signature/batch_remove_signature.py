from pathlib import Path

from .base import CompositeSignature
from .remove_signature import RemoveSignature
from ...config import Config


class BatchRemoveSignature(CompositeSignature):
    def __init__(self, config: Config, *paths: Path):
        super().__init__(*map(lambda path: RemoveSignature(config, path), paths))
