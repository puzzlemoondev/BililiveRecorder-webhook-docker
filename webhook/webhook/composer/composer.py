from pathlib import Path
from typing import Optional, Iterator

from celery.canvas import chord, group, Signature

from ..config import Config, BiliupConfig
from ..event import Event
from ..task import (
    BurnDanmakuTaskInput,
    UploadAliyunpanTaskInput,
    UploadBaidupcsTaskInput,
    UploadBilibiliTaskInput,
    RemoveTaskInput,
)
from ..tasks import (
    burn_danmaku,
    upload_aliyunpan,
    upload_baidupcs,
    upload_bilibili,
    remove,
)


class Composer:
    def __init__(self, event: Event, config: Config):
        self.event = event
        self.config = config

    def __call__(self) -> Signature:
        upload_signature = group(self.get_upload_signatures())
        if burn_danmaku_signature := self.get_burn_danmaku_signature():
            return burn_danmaku_signature.on_error(upload_signature) | upload_signature
        return upload_signature

    def get_upload_signatures(self) -> Iterator[Signature]:
        files = self.event.get_event_files()

        for video_path in files.get_video_paths():
            yield chord(
                self.get_all_upload_signatures(video_path),
                self.get_remove_signature(video_path),
            )
        for metadata_path in files.get_metadata_paths():
            yield chord(
                self.get_all_upload_signatures(metadata_path),
                self.get_remove_signature(metadata_path),
            )

    def get_cloud_storage_upload_signatures(self, path: Path) -> Iterator[Signature]:
        signatures = [
            self.get_upload_aliyunpan_signature(path),
            self.get_upload_baidupcs_signature(path),
        ]
        return filter(bool, signatures)

    def get_all_upload_signatures(self, path: Path) -> Iterator[Signature]:
        signatures = [
            self.get_upload_bilibili_signature(path),
            *self.get_cloud_storage_upload_signatures(path),
        ]
        return filter(bool, signatures)

    def get_burn_danmaku_signature(self) -> Optional[Signature]:
        if not self.config.burn_danmaku:
            return

        input = BurnDanmakuTaskInput(
            event_json=self.event.data,
            danmaku_factory_args=self.config.danmaku_factory_args,
        )
        return burn_danmaku.si(input.to_dict())

    def get_upload_bilibili_signature(self, path: Path) -> Optional[Signature]:
        biliup_config = BiliupConfig(self.event)
        user_cookie = biliup_config.user_cookie
        if not user_cookie.exists():
            return

        input = UploadBilibiliTaskInput(
            event_json=self.event.data,
            user_cookie=str(user_cookie),
            path=str(path),
        )
        return upload_bilibili.si(input.to_dict())

    def get_upload_aliyunpan_signature(self, path: Path) -> Optional[Signature]:
        if not self.config.aliyunpan_rtoken:
            return

        input = UploadAliyunpanTaskInput(
            rtoken=self.config.aliyunpan_rtoken, path=str(path)
        )
        return upload_aliyunpan.si(input.to_dict())

    def get_upload_baidupcs_signature(self, path: Path) -> Optional[Signature]:
        if not (self.config.baidupcs_bduss and self.config.baidupcs_stoken):
            return

        input = UploadBaidupcsTaskInput(
            bduss=self.config.baidupcs_bduss,
            stoken=self.config.baidupcs_stoken,
            path=str(path),
        )
        return upload_baidupcs.si(input.to_dict())

    @staticmethod
    def get_remove_signature(path: Path) -> Signature:
        input = RemoveTaskInput(path=str(path))
        return remove.si(input.to_dict())
