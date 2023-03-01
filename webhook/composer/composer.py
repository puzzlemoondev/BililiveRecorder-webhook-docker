from pathlib import Path
from typing import Optional, Callable, Iterator

from boltons.setutils import IndexedSet
from celery.canvas import chain, chord, group, Signature

from ..config import Config, BiliupConfig
from ..event import Event, EventFiles
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
from ..util import compact


class Composer:
    def __init__(self, event: Event, config: Config):
        self.event = event
        self.config = config

    def __call__(self) -> Signature:
        files = self.event.get_event_files()

        if burn_danmaku_signature := self.get_burn_danmaku_signature():
            if self.config.bilibili_upload_burned:
                return self.get_burn_danmaku_upload_bilibili_upload_cloud_signature(files, burn_danmaku_signature)
            return self.get_upload_bilibili_burn_danmaku_upload_cloud_signature(files, burn_danmaku_signature)
        return self.get_upload_bilibili_upload_cloud_signature(files)

    def get_burn_danmaku_upload_bilibili_upload_cloud_signature(
        self, files: EventFiles, burn_danmaku_signature: Signature
    ) -> Signature:
        return group(
            [
                chain(
                    burn_danmaku_signature,
                    group(
                        [
                            self.get_upload_bilibili_and_cloud_signature(files.burned),
                            self.get_upload_cloud_signature(files.subtitles),
                        ]
                    ),
                ),
                *(
                    self.get_upload_cloud_signature(path)
                    for path in IndexedSet(files).iter_difference({files.burned, files.subtitles})
                ),
            ]
        )

    def get_upload_bilibili_burn_danmaku_upload_cloud_signature(
        self, files: EventFiles, burn_danmaku_signature: Signature
    ) -> Signature:
        return group(
            [
                self.get_upload_bilibili_and_cloud_signature(files.data, remove_after=False),
                self.get_upload_cloud_signature(files.danmaku, remove_after=False),
                *(
                    self.get_upload_cloud_signature(path)
                    for path in IndexedSet(files).iter_difference(
                        {
                            files.burned,
                            files.subtitles,
                            files.data,
                            files.danmaku,
                        }
                    )
                ),
                chain(
                    burn_danmaku_signature,
                    group(
                        compact(
                            [
                                self.get_remove_signature(files.data),
                                self.get_remove_signature(files.danmaku),
                                self.get_upload_cloud_signature(files.burned),
                                self.get_upload_cloud_signature(files.subtitles),
                            ]
                        )
                    ),
                ),
            ]
        )

    def get_upload_bilibili_upload_cloud_signature(self, files: EventFiles) -> Signature:
        return group(
            [
                self.get_upload_bilibili_and_cloud_signature(files.data),
                *(
                    self.get_upload_cloud_signature(path)
                    for path in IndexedSet(files).iter_difference({files.burned, files.subtitles, files.data})
                ),
            ]
        )

    def get_upload_bilibili_and_cloud_signature(self, path: Path, remove_after: bool = True) -> Signature:
        def signatures_builder(_path: Path):
            return [
                self.get_upload_bilibili_signature(_path),
                self.get_upload_aliyunpan_signature(_path),
                self.get_upload_baidupcs_signature(_path),
            ]

        return self.get_signature(signatures_builder, path, remove_after)

    def get_upload_cloud_signature(self, path: Path, remove_after: bool = True) -> Signature:
        def signatures_builder(_path: Path):
            return [
                self.get_upload_aliyunpan_signature(_path),
                self.get_upload_baidupcs_signature(_path),
            ]

        return self.get_signature(signatures_builder, path, remove_after)

    def get_signature(
        self,
        signatures_builder: Callable[[Path], Iterator[Optional[Signature]]],
        path: Path,
        remove_after: bool,
    ) -> Signature:
        signatures = compact(signatures_builder(path))
        if remove_after and (remove_signature := self.get_remove_signature(path)):
            return chord(signatures, remove_signature)
        return group(signatures)

    def get_burn_danmaku_signature(self) -> Optional[Signature]:
        if not self.config.burn_danmaku:
            return

        input = BurnDanmakuTaskInput(
            event_json=self.event.data,
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
        if rtoken := self.config.aliyunpan_rtoken:
            input = UploadAliyunpanTaskInput(rtoken=rtoken, path=str(path))
            return upload_aliyunpan.si(input.to_dict())

    def get_upload_baidupcs_signature(self, path: Path) -> Optional[Signature]:
        if (bduss := self.config.baidupcs_bduss) and (stoken := self.config.baidupcs_stoken):
            input = UploadBaidupcsTaskInput(
                bduss=bduss,
                stoken=stoken,
                path=str(path),
            )
            return upload_baidupcs.si(input.to_dict())

    def get_remove_signature(self, path: Path) -> Optional[Signature]:
        if not self.config.remove_local:
            return

        input = RemoveTaskInput(path=str(path))
        return remove.si(input.to_dict())
