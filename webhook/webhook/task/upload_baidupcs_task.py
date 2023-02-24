from dataclasses import dataclass
from pathlib import Path

from .task import Task, Input, Output
from ..command import BaidupcsCommand


@dataclass
class UploadBaidupcsTaskInput(Input):
    bduss: str
    stoken: str
    path: str


@dataclass
class UploadBaidupcsTaskOutput(Output):
    path: str


class UploadBaidupcsTask(Task[UploadBaidupcsTaskInput, UploadBaidupcsTaskOutput]):
    def __init__(self, input: UploadBaidupcsTaskInput):
        super().__init__(input)
        self.baidupcs = BaidupcsCommand(bduss=self.input.bduss, stoken=self.input.stoken)

    def run(self) -> UploadBaidupcsTaskOutput:
        exists = Path(self.input.path).exists()
        if exists:
            self.baidupcs.login_if_needed()
            self.baidupcs.upload_and_verify(self.input.path)

        return UploadBaidupcsTaskOutput(path=self.input.path, skipped=not exists)
