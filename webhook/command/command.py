import shutil
import subprocess


class Command:
    def __init__(self, executable_name: str):
        if executable := shutil.which(executable_name):
            self.executable = executable
        else:
            raise FileNotFoundError(f"{executable_name} not found in path")

    def __call__(self, *args) -> str:
        return subprocess.check_output([self.executable, *args], encoding="utf8")
