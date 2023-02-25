import subprocess


class Command:
    def __init__(self, executable: str):
        self.executable = executable

    def __call__(self, *args) -> str:
        return subprocess.check_output([self.executable, *args], encoding="utf8")
