from dataclasses import dataclass

from .task import Task, Input, Output
from ..command import DanmakuFactoryCommand, FFMPEGCommand
from ..event import Event


@dataclass
class BurnDanmakuTaskInput(Input):
    event_json: dict


@dataclass
class BurnDanmakuTaskOutput(Output):
    burned_path: str
    subtitles_path: str


class BurnDanmakuTask(Task[BurnDanmakuTaskInput, BurnDanmakuTaskOutput]):
    def __init__(self, input: BurnDanmakuTaskInput):
        super().__init__(input)
        self.danmaku_factory = DanmakuFactoryCommand()
        self.ffmpeg = FFMPEGCommand()

    def run(self) -> BurnDanmakuTaskOutput:
        event = Event(self.input.event_json)
        files = event.get_event_files()

        self.danmaku_factory.convert(str(files.danmaku), str(files.subtitles))

        self.ffmpeg.add_subtitles(str(files.data), str(files.subtitles), str(files.burned))

        return BurnDanmakuTaskOutput(burned_path=str(files.burned), subtitles_path=str(files.subtitles), skipped=False)
