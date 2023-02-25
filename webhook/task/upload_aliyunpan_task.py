from dataclasses import dataclass
from pathlib import Path

from .task import Task, Input, Output
from ..command import AliyunpanCommand


@dataclass
class UploadAliyunpanTaskInput(Input):
    path: str
    rtoken: str


@dataclass
class UploadAliyunpanTaskOutput(Output):
    path: str


class UploadAliyunpanTask(Task[UploadAliyunpanTaskInput, UploadAliyunpanTaskOutput]):
    def __init__(self, input: UploadAliyunpanTaskInput):
        super().__init__(input)
        self.aliyunpan = AliyunpanCommand(rtoken=self.input.rtoken)

    def run(self) -> UploadAliyunpanTaskOutput:
        exists = Path(self.input.path).exists()
        if exists:
            self.aliyunpan.login_if_needed()
            self.aliyunpan.upload_and_verify(self.input.path)

        return UploadAliyunpanTaskOutput(path=self.input.path, skipped=not exists)
