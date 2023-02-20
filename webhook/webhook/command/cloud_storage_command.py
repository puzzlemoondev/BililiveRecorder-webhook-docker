from pathlib import Path

from .command import Command
from ..util.string_utils import count_lines


class CloudStorageCommand(Command):
    def upload(self, local_path: str, remote_dir: str) -> str:
        return self("upload", local_path, remote_dir)

    def login(self, *args) -> str:
        return self("login", *args)

    def loglist(self) -> str:
        return self("loglist")

    def ls(self, path: str) -> str:
        return self("ls", path)

    def login_if_needed(self):
        if not self.has_account():
            self.login()

    def upload_and_verify(self, local_path: str):
        resolved_path = Path(local_path).resolve()
        local_path = str(resolved_path)
        remote_dir = f"/{resolved_path.parent.name}"

        self.upload(local_path, remote_dir)

        if not self.remote_contains(local_path, remote_dir):
            raise AssertionError(f"{resolved_path} not uploaded to {self.executable}")

    def has_account(self) -> int:
        accounts = count_lines(self.loglist()) - 1  # subtracts header
        return accounts > 0

    def remote_contains(self, local_path: str, remote_dir: str):
        remote_content = self.ls(remote_dir)
        return Path(local_path).name in remote_content
