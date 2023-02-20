import os
from pathlib import Path
from tempfile import TemporaryDirectory

from .celery import app
from .command import CloudStorageCommand, BiliupCommand, FFMPEGCommand, DanmakuFactoryCommand
from .config import BiliupConfig
from .event import Event
from .util import is_empty

DEFAULT_TASK_ARGS = dict(autoretry_for=(Exception,), default_retry_delay=10)


def result(path: str, skipped: bool = False):
    return dict(path=path, skipped=skipped)


@app.task(**DEFAULT_TASK_ARGS)
def upload_aliyunpan(path: str) -> dict:
    rtoken = os.environ.get("ALIYUNPAN_RTOKEN")
    if not rtoken:
        return result(path, True)

    aliyunpan = CloudStorageCommand("aliyunpan")

    resolved_path = Path(path).resolve(strict=True)
    local_path = str(resolved_path)
    remote_dir = f"/{resolved_path.parent.name}"

    if not aliyunpan.has_account():
        aliyunpan.login("-RefreshToken", rtoken)
    aliyunpan.upload(local_path, remote_dir)
    if not aliyunpan.remote_contains(local_path, remote_dir):
        raise AssertionError(f"{resolved_path} not uploaded to aliyunpan")
    return result(path)


@app.task(**DEFAULT_TASK_ARGS)
def upload_baidupcs(path: str) -> dict:
    bduss = os.environ.get("BAIDUPCS_BDUSS")
    stoken = os.environ.get("BAIDUPCS_STOKEN")
    if not (bduss and stoken):
        return result(path, True)

    baidupcs = CloudStorageCommand("baidupcs")
    resolved_path = Path(path).resolve(strict=True)
    local_path = str(resolved_path)
    remote_dir = f"/{resolved_path.parent.name}"

    if not baidupcs.has_account():
        baidupcs.login("-bduss", bduss, "-stoken", stoken)
    baidupcs.upload(local_path, remote_dir)
    if not baidupcs.remote_contains(local_path, remote_dir):
        raise AssertionError(f"{resolved_path} not uploaded to baidupcs")
    return result(path)


@app.task(**DEFAULT_TASK_ARGS)
def upload_biliup(event_json: dict) -> dict:
    event = Event(event_json)
    config = BiliupConfig(event)
    if not config.user_cookie.exists():
        return result(str(event.get_data_path(strict=False)), True)

    video_path = event.get_data_path()
    biliup = BiliupCommand(str(config.user_cookie))

    with TemporaryDirectory() as tmpdir:
        if os.environ.get("BILIUP_BURN_DANMAKU", "0") != "0":
            source_path = video_path
            danmaku_path = event.get_danmaku_path()
            video_path = Path(tmpdir).joinpath(video_path.name)
            subtitles_path = video_path.with_suffix('.ass')

            danmaku_factory = DanmakuFactoryCommand()
            danmaku_factory(str(danmaku_path), str(subtitles_path))

            ffmpeg = FFMPEGCommand()
            ffmpeg.add_subtitles(
                str(source_path),
                str(video_path),
                str(subtitles_path)
            )

        video_path = str(video_path)

        biliup.renew()
        biliup.upload(video_path, *config.to_command_args())
        return result(video_path)


@app.task(**DEFAULT_TASK_ARGS)
def remove(results: list[dict]):
    if all(map(lambda r: r["skipped"], results)):
        return

    for path in set(map(lambda r: Path(r["path"]), results)):
        path.unlink(missing_ok=True)
        parent = path.parent
        if is_empty(parent):
            parent.rmdir()
