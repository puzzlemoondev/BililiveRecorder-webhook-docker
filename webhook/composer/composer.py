from pathlib import Path
from typing import Optional, Callable, Iterator

from celery.canvas import chain, chord, group, Signature

from ..config import Config, BILIUP_CONFIG_DIR
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
from ..util import compact, filter_suffixes


class Composer:
    def __init__(self, event: Event, config: Config):
        self.event = event
        self.config = config

    def __call__(self) -> Signature:
        files = self.event.get_event_files()

        if burn_danmaku_signature := self.get_burn_danmaku_signature():
            burn_danmaku_signature = self.get_burn_danmaku_remove_on_error_signature(files, burn_danmaku_signature)
            if self.config.bilibili_upload_burned:
                return self.get_burn_danmaku_upload_bilibili_upload_cloud_signature(files, burn_danmaku_signature)
            return self.get_upload_bilibili_burn_danmaku_upload_cloud_signature(files, burn_danmaku_signature)
        return self.get_upload_bilibili_upload_cloud_signature(files)

    def get_burn_danmaku_remove_on_error_signature(
        self, files: EventFiles, burn_danmaku_signature: Signature
    ) -> Signature:
        return burn_danmaku_signature.on_error(self.get_batch_remove_signature(files.burned, files.subtitles))

    def get_burn_danmaku_upload_bilibili_upload_cloud_signature(
        self, files: EventFiles, burn_danmaku_signature: Signature
    ) -> Signature:
        burn_files = files.get_burn_files()
        burn_dependencies = files.get_burn_dependencies()

        def upload_signature(path: Path) -> Signature:
            remove_after = path not in burn_dependencies
            return self.get_upload_cloud_signature(path, remove_after=remove_after)

        upload_signatures = map(upload_signature, files.get_files() - burn_files)

        burn_upload_signature = chain(
            burn_danmaku_signature,
            group(
                [
                    self.get_upload_bilibili_and_cloud_signature(files.burned),
                    self.get_upload_cloud_signature(files.subtitles),
                ]
            ),
        )

        remove_dangling_signature = self.get_batch_remove_signature(*burn_dependencies)

        return chord([burn_upload_signature, *upload_signatures], remove_dangling_signature)

    def get_upload_bilibili_burn_danmaku_upload_cloud_signature(
        self, files: EventFiles, burn_danmaku_signature: Signature
    ) -> Signature:
        burn_files = files.get_burn_files()
        burn_dependencies = files.get_burn_dependencies()

        def upload_signature(path: Path) -> Signature:
            remove_after = path not in burn_dependencies
            if path == files.data:
                return self.get_upload_bilibili_and_cloud_signature(path, remove_after=remove_after)
            return self.get_upload_cloud_signature(path, remove_after=remove_after)

        upload_signatures = map(upload_signature, files.get_files() - burn_files)

        burn_upload_signature = chain(
            burn_danmaku_signature,
            group(map(self.get_upload_cloud_signature, burn_files)),
        )

        remove_dangling_signature = self.get_batch_remove_signature(*burn_dependencies)

        return chord([*upload_signatures, burn_upload_signature], remove_dangling_signature)

    def get_upload_bilibili_upload_cloud_signature(self, files: EventFiles) -> Signature:
        def upload_signature(path: Path) -> Signature:
            if path == files.data:
                return self.get_upload_bilibili_and_cloud_signature(path)
            return self.get_upload_cloud_signature(path)

        upload_signatures = map(upload_signature, files.get_files())

        return group(upload_signatures)

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

    def get_batch_remove_signature(self, *paths: Path) -> Signature:
        return group(compact(map(self.get_remove_signature, paths)))

    def get_burn_danmaku_signature(self) -> Optional[Signature]:
        if not self.config.burn_danmaku:
            return

        input = BurnDanmakuTaskInput(
            event_json=self.event.data,
        )
        return burn_danmaku.si(input.to_dict())

    def get_upload_bilibili_signature(self, path: Path) -> Optional[Signature]:
        try:
            config_path = next(filter_suffixes(BILIUP_CONFIG_DIR.glob("config.*"), ".yml", ".yaml"))
        except StopIteration:
            return
        if not config_path.exists():
            return

        input = UploadBilibiliTaskInput(
            event_json=self.event.data,
            config_path=str(config_path),
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
                path=str(path), bduss=bduss, stoken=stoken, max_upload_parallel=self.config.baidupcs_max_upload_parallel
            )
            return upload_baidupcs.si(input.to_dict())

    def get_remove_signature(self, path: Path) -> Optional[Signature]:
        if not self.config.remove_local:
            return

        input = RemoveTaskInput(path=str(path))
        return remove.si(input.to_dict())
