from pathlib import Path
from typing import Callable

from boltons.setutils import IndexedSet

from .base import CompositeSignature
from .upload_bilibili_and_cloud_signature import UploadBilibiliAndCloudSignature
from .upload_cloud_signature import UploadCloudSignature
from ...config import Config
from ...event import Event, EventFiles


class UploadSignature(CompositeSignature):
    def __init__(
        self,
        config: Config,
        event: Event,
        paths: Callable[[EventFiles], IndexedSet[Path]] = lambda files: files.get_files(),
        remove_after: Callable[[Path], bool] = lambda path: True,
    ):
        def resolve():
            files = event.get_event_files()
            for path in paths(files):
                if path == files.data:
                    yield UploadBilibiliAndCloudSignature(config, event, path, remove_after=remove_after(path))
                else:
                    yield UploadCloudSignature(config, path, remove_after=remove_after(path))

        super().__init__(*resolve())
