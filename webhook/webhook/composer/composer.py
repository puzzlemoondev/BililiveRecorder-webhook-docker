from pathlib import Path
from typing import Optional, Iterator, Iterable, Callable

from celery.canvas import chain, chord, group, Signature

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
            return chain(
                burn_danmaku_signature.on_error(upload_signature), upload_signature
            )
        return upload_signature

    def get_upload_signatures(self) -> Iterator[Signature]:
        files = self.event.get_event_files()

        def get_signature(
            signatures_builder: Callable[[Path], Iterable[Signature]], path: Path
        ) -> Signature:
            signatures = signatures_builder(path)
            if remove_signature := self.get_remove_signature(path):
                return chord(signatures, remove_signature)
            return group(signatures)

        # TODO refactor: move burn checking out and prioritize upload if not upload burned
        bilibili_upload_path = (
            files.burned
            if self.config.burn_danmaku and self.config.bilibili_upload_burned
            else files.data
        )
        yield get_signature(self.get_all_upload_signatures, bilibili_upload_path)

        for cloud_storage_upload_path in filter(
            lambda path: path != bilibili_upload_path, files
        ):
            yield get_signature(
                self.get_cloud_storage_upload_signatures, cloud_storage_upload_path
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

    def get_remove_signature(self, path: Path) -> Optional[Signature]:
        if not self.config.remove_local:
            return

        input = RemoveTaskInput(path=str(path))
        return remove.si(input.to_dict())
