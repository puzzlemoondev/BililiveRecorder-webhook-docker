import click

from .composer import Composer
from .config import Config
from .event import Event
from .util import JSON

config = Config()


@click.command()
@click.argument("event", type=JSON)
def main(event: dict):
    event = Event(event)
    event.save()

    composer = Composer(event, config)
    task = composer()
    task.delay()


if __name__ == "__main__":
    main()
