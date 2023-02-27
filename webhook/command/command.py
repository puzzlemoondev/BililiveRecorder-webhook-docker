import shutil
import subprocess
from pathlib import Path


class Command:
    def __init__(self, executable_name: str):
        self.executable = Path(shutil.which(executable_name))

    def __call__(self, *args) -> str:
        return subprocess.check_output([self.executable, *args], encoding="utf8")
