from typing import Iterable

from celery import group
from fastapi import FastAPI, Body

from .event import Event
from .tasks import upload_aliyunpan, upload_baidupcs, upload_biliup, remove

app = FastAPI()


def tasks(event: Event) -> Iterable:
    def action(*args):
        return group(args) | remove.s()

    event_data_path = str(event.get_data_path())
    yield action(
        upload_biliup.s(event.data),
        upload_aliyunpan.s(event_data_path),
        upload_baidupcs.s(event_data_path),
    )
    for path in event.get_metadata_paths():
        path = str(path)
        yield action(upload_aliyunpan.s(path), upload_baidupcs.s(path))


@app.post("/hooks/recorder-file-closed")
def recorder_file_closed(payload: dict = Body()):
    if payload["EventType"] != "FileClosed":
        return
    event = Event(payload)
    event.save()

    group(tasks(event)).delay()
