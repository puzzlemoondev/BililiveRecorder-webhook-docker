from pathlib import Path

from .command import Command

DANMAKU_FACTORY_CONFIG_DIR = Path("/etc/DanmakuFactory").resolve(strict=True)


class DanmakuFactoryCommand(Command):
    def __init__(self):
        super().__init__("DanmakuFactory", cwd=DANMAKU_FACTORY_CONFIG_DIR)

    def __call__(self, *args) -> str:
        return super().__call__("-c", *args, "--ignore-warnings")

    def convert(self, source: str, output: str) -> str:
        return self("-i", source, "-o", output)
