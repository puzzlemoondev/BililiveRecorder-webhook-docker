from dataclasses import dataclass

from .task import Task, Input, Output
from ..command import DanmakuFactoryCommand, FFMPEGCommand
from ..event import Event


@dataclass
class BurnDanmakuTaskInput(Input):
    event_json: dict
    danmaku_factory_args: list[str]


@dataclass
class BurnDanmakuTaskOutput(Output):
    event_json: dict


class BurnDanmakuTask(Task[BurnDanmakuTaskInput, BurnDanmakuTaskOutput]):
    def __init__(self, input: BurnDanmakuTaskInput):
        super().__init__(input)
        self.danmaku_factory = DanmakuFactoryCommand()
        self.ffmpeg = FFMPEGCommand()

    def run(self) -> BurnDanmakuTaskOutput:
        event = Event(self.input.event_json)
        files = event.get_event_files()

        self.danmaku_factory.convert(
            str(files.danmaku), str(files.subtitles), *self.input.danmaku_factory_args
        )

        self.ffmpeg.add_subtitles(
            str(files.data), str(files.subtitles), str(files.burned)
        )

        return BurnDanmakuTaskOutput(event_json=self.input.event_json, skipped=False)
