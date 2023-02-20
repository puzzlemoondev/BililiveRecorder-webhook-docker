import argparse
import json

from .composer import Composer
from .config import Config
from .event import Event

config = Config()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("event", type=str)
    args = parser.parse_args()

    payload = json.loads(args.event)
    event = Event(payload)
    event.save()

    composer = Composer(event, config)
    task = composer()
    task.delay()


if __name__ == "__main__":
    main()
