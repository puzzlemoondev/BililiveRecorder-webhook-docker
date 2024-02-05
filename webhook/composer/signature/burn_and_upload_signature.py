from .base import CompositeSignature
from .batch_remove_signature import BatchRemoveSignature
from .batch_upload_cloud_signature import BatchUploadCloudSignature
from .burn_danmaku_signature import BurnDanmakuSignature
from .upload_bilibili_and_cloud_signature import UploadBilibiliAndCloudSignature
from .upload_cloud_signature import UploadCloudSignature
from ...config import Config
from ...event import Event


class BurnAndUploadSignature(CompositeSignature):
    def __init__(self, config: Config, event: Event, burn_danmaku_signature: BurnDanmakuSignature):
        files = event.get_event_files()
        all_files = files.get_files()
        burn_files = files.get_burn_files()
        burn_dependencies = files.get_burn_dependencies()

        burn_upload_signature = CompositeSignature(burn_danmaku_signature)
        burn_upload_signature.callback = CompositeSignature(
            UploadBilibiliAndCloudSignature(config, event, files.burned),
            UploadCloudSignature(config, files.subtitles),
        )
        burn_upload_signature.error_callback = BatchRemoveSignature(config, files.burned, files.subtitles)

        upload_signature = BatchUploadCloudSignature(
            config, *(all_files - burn_files), remove_after=lambda path: path not in burn_dependencies
        )

        super().__init__(upload_signature, burn_upload_signature)

        remove_dangling_signature = BatchRemoveSignature(config, *burn_dependencies)
        self.callback = remove_dangling_signature
