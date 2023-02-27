import subprocess
from pathlib import Path
from typing import Optional


class Command:
    def __init__(self, executable: str, cwd: Optional[Path] = None):
        self.executable = executable
        self.cwd = cwd

    def __call__(self, *args) -> str:
        return subprocess.check_output([self.executable, *args], cwd=self.cwd, encoding="utf8")
