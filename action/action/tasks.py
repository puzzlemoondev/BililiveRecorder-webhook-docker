import os
from pathlib import Path

from biliup.plugins.bili_webup import BiliBili

from .celery import app
from .command import CloudStorageCommand
from .config import BiliupConfig
from .event import Event
from .util import filter_suffixes, is_empty

BILIUP_CONFIG_DIR = Path("/etc/biliup")
DEFAULT_TASK_ARGS = dict(autoretry_for=(Exception,), default_retry_delay=10)


def result(path: str, skipped: bool = False):
    return dict(path=path, skipped=skipped)


@app.task(**DEFAULT_TASK_ARGS)
def upload_aliyunpan(path: str) -> dict:
    rtoken = os.environ.get("ALIYUNPAN_RTOKEN")
    if not rtoken:
        return result(path, True)

    command = CloudStorageCommand("aliyunpan")

    resolved_path = Path(path).resolve(strict=True)
    local_path = str(resolved_path)
    remote_dir = f"/{resolved_path.parent.name}"

    if not command.has_account():
        command.login("-RefreshToken", rtoken)
    command.upload(local_path, remote_dir)
    if not command.remote_contains(local_path, remote_dir):
        raise AssertionError(f"{resolved_path} not uploaded to aliyunpan")
    return result(path)


@app.task(**DEFAULT_TASK_ARGS)
def upload_baidupcs(path: str) -> dict:
    bduss = os.environ.get("BAIDUPCS_BDUSS")
    stoken = os.environ.get("BAIDUPCS_STOKEN")
    if not (bduss and stoken):
        return result(path, True)

    command = CloudStorageCommand("baidupcs-go")
    resolved_path = Path(path).resolve(strict=True)
    local_path = str(resolved_path)
    remote_dir = f"/{resolved_path.parent.name}"

    if not command.has_account():
        command.login("-bduss", bduss, "-stoken", stoken)
    command.upload(local_path, remote_dir)
    if not command.remote_contains(local_path, remote_dir):
        raise AssertionError(f"{resolved_path} not uploaded to baidupcs")
    return result(path)


@app.task(**DEFAULT_TASK_ARGS)
def upload_biliup(event_json: str) -> dict:
    event = Event(event_json)
    config_path = next(
        filter_suffixes(BILIUP_CONFIG_DIR.glob("config.*"), ".yml", ".yaml"),
        None,
    )
    if config_path is None:
        return result(str(event.get_data_path(strict=False)), True)

    config = BiliupConfig(config_path)
    user = config.get_user()
    video = config.to_data(event)
    video_path = str(event.get_data_path())
    with BiliBili(video) as bili:
        bili.login(BILIUP_CONFIG_DIR.joinpath("bili.cookie"), user)
        video_part = bili.upload_file(video_path)
        video.append(video_part)
        if video.cover:
            video.cover = bili.cover_up(video.cover).replace("http:", "")
        bili.submit()
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
