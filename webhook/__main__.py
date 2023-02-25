import argparse

from .composer import Composer
from .config import Config
from .event import Event
from .util import ParseJSONAction

config = Config()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("event", action=ParseJSONAction)
    args = parser.parse_args()

    event = Event(args.event)
    event.save()

    composer = Composer(event, config)
    task = composer()
    task.delay()


if __name__ == "__main__":
    main()
