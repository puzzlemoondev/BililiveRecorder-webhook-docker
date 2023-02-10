from pathlib import Path

from .command import Command
from ..util.string_utils import count_lines


class CloudStorageCommand(Command):
    def upload(self, local_path: str, remote_dir: str) -> str:
        print(f"{self.executable} uploading {local_path}")
        return self("upload", local_path, remote_dir)

    def login(self, *args) -> str:
        print(f"{self.executable} logging in")
        return self("login", *args)

    def loglist(self) -> str:
        print(f"{self.executable} loglist")
        return self("loglist")

    def ls(self, path: str) -> str:
        print(f"{self.executable} listing {path}")
        return self("ls", path)

    def has_account(self) -> int:
        accounts = count_lines(self.loglist()) - 1  # subtracts header
        return accounts > 0

    def remote_contains(self, local_path: str, remote_dir: str):
        remote_content = self.ls(remote_dir)
        return Path(local_path).name in remote_content
