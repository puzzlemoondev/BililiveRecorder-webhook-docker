from pathlib import Path
from typing import Optional

from .command import Command
from ..util.string_utils import count_lines

REMOTE_ROOT = "/"


class CloudStorageCommand(Command):
    def upload(self, local_path: str, remote_dir: Optional[str]) -> str:
        return self("upload", local_path, remote_dir or REMOTE_ROOT)

    def login(self, *args) -> str:
        return self("login", *args)

    def loglist(self) -> str:
        return self("loglist")

    def ls(self, path: str) -> str:
        return self("ls", path)

    def login_if_needed(self):
        if not self.has_account():
            self.login()

    def upload_and_verify(self, local_path: str, remote_dir: Optional[str]):
        resolved_path = Path(local_path).resolve()
        local_path = str(resolved_path)

        if remote_dir:
            remote_dir = str(Path(REMOTE_ROOT).joinpath(remote_dir))

        self.upload(local_path, remote_dir)

        if not self.remote_contains(local_path, remote_dir):
            raise AssertionError(f"{resolved_path} not uploaded to {self.executable}")

    def has_account(self) -> bool:
        accounts = count_lines(self.loglist()) - 1
        return accounts > 0

    def remote_contains(self, local_path: str, remote_dir: str) -> bool:
        remote_content = self.ls(remote_dir)
        return Path(local_path).name in remote_content
