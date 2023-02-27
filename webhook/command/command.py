import shutil
import subprocess
from pathlib import Path
from typing import Optional


class Command:
    def __init__(self, executable_name: str, cwd: Optional[Path] = None):
        if executable := shutil.which(executable_name):
            self.executable = executable
        else:
            raise FileNotFoundError(f"{executable_name} not found in path")
        self.cwd = cwd

    def __call__(self, *args) -> str:
        return subprocess.check_output([self.executable, *args], cwd=self.cwd, encoding="utf8")
