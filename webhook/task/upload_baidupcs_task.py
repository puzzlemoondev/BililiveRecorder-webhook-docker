from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .base import Task, Input, Output
from ..command import BaidupcsCommand


@dataclass
class UploadBaidupcsTaskInput(Input):
    path: str
    remote_dir: Optional[str]
    bduss: str
    stoken: str
    max_upload_parallel: Optional[int]


@dataclass
class UploadBaidupcsTaskOutput(Output):
    path: str


class UploadBaidupcsTask(Task[UploadBaidupcsTaskInput, UploadBaidupcsTaskOutput]):
    def __init__(self, input: UploadBaidupcsTaskInput):
        super().__init__(input)
        self.baidupcs = BaidupcsCommand(
            bduss=self.input.bduss, stoken=self.input.stoken, max_upload_parallel=self.input.max_upload_parallel
        )

    def run(self) -> UploadBaidupcsTaskOutput:
        exists = Path(self.input.path).exists()
        if exists:
            self.baidupcs.login_if_needed()
            self.baidupcs.upload_and_verify(self.input.path, self.input.remote_dir)

        return UploadBaidupcsTaskOutput(path=self.input.path, skipped=not exists)
