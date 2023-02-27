from .command import Command


class DanmakuFactoryCommand(Command):
    def __init__(self):
        super().__init__("DanmakuFactory")

    def __call__(self, *args) -> str:
        return super().__call__(*args, "--ignore-warnings")

    def convert(self, source: str, output: str, *args: str) -> str:
        return self("-i", source, "-o", output, *args)
