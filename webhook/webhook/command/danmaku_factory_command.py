from .command import Command


class DanmakuFactoryCommand(Command):
    def __init__(self):
        super().__init__("DanmakuFactory")

    def convert(self, source: str, output: str, *args: str) -> str:
        return super().__call__("-i", source, "-o", output, *args)
