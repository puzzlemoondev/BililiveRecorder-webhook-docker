import argparse
from typing import Iterable

from celery import group

from action.event import Event
from action.tasks import upload_aliyunpan, upload_baidupcs, upload_biliup, remove


def tasks(event: Event) -> Iterable:
    def action(*args):
        return group(args) | remove.s()

    event_data_path = str(event.get_data_path())
    yield action(
        upload_biliup.s(event.text),
        upload_aliyunpan.s(event_data_path),
        upload_baidupcs.s(event_data_path),
    )
    for path in event.get_metadata_paths():
        path = str(path)
        yield action(upload_aliyunpan.s(path), upload_baidupcs.s(path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("event", type=str)
    args = parser.parse_args()

    event = Event(args.event)
    event.save()

    group(tasks(event)).delay()


if __name__ == "__main__":
    main()
