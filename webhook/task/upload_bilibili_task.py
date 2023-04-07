from dataclasses import dataclass
from pathlib import Path

from .task import Task, Input, Output
from ..command import BiliupCommand
from ..config import BiliupConfig
from ..event import Event


@dataclass
class UploadBilibiliTaskInput(Input):
    event_json: dict
    config_path: str
    path: str


@dataclass
class UploadBilibiliTaskOutput(Output):
    path: str


class UploadBilibiliTask(Task[UploadBilibiliTaskInput, UploadBilibiliTaskOutput]):
    def __init__(self, input: UploadBilibiliTaskInput):
        super().__init__(input)
        self._event = None
        self._config = None
        self._biliup = None

    @property
    def event(self) -> Event:
        if self._event is None:
            self._event = Event(self.input.event_json)
        return self._event

    @property
    def config(self) -> BiliupConfig:
        if self._config is None:
            self._config = BiliupConfig(self.event, Path(self.input.config_path))
        return self._config

    @property
    def biliup(self) -> BiliupCommand:
        if self._biliup is None:
            self._biliup = BiliupCommand(str(self.config.user_cookie))
        return self._biliup

    def run(self) -> UploadBilibiliTaskOutput:
        exists = Path(self.input.path).exists()
        if exists:
            self.biliup.renew()
            self.biliup.upload(self.input.path, *self.config.to_command_args())

        return UploadBilibiliTaskOutput(path=self.input.path, skipped=not exists)
