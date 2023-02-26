from pathlib import Path

from .command import Command


class DanmakuFactoryCommand(Command):
    """
    DanmakuFactory expects user interaction when output exists.
    We have to delete output file first to avoid this.
    upstream issue: https://github.com/hihkm/DanmakuFactory/issues/43
    """

    def __init__(self):
        super().__init__("DanmakuFactory")

    def convert(self, source: str, output: str, *args: str) -> str:
        Path(output).unlink(missing_ok=True)
        return self("-i", source, "-o", output, *args)
