from dataclasses import dataclass
from pathlib import Path

from .task import Task, Input, Output
from ..command import BiliupCommand
from ..config import BiliupConfig
from ..event import Event


@dataclass
class UploadBilibiliTaskInput(Input):
    event_json: dict
    user_cookie: str
    path: str


@dataclass
class UploadBilibiliTaskOutput(Output):
    path: str


class UploadBilibiliTask(Task[UploadBilibiliTaskInput, UploadBilibiliTaskOutput]):
    def __init__(self, input: UploadBilibiliTaskInput):
        super().__init__(input)
        self.biliup = BiliupCommand(self.input.user_cookie)

    def run(self) -> UploadBilibiliTaskOutput:
        exists = Path(self.input.path).exists()
        if exists:
            event = Event(self.input.event_json)
            config = BiliupConfig(event)

            self.biliup.renew()
            self.biliup.upload(self.input.path, *config.to_command_args())

        return UploadBilibiliTaskOutput(path=self.input.path, skipped=not exists)
