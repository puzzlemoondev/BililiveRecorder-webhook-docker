from pathlib import Path

from .command import Command

DANMAKU_FACTORY_CONFIG_DIR = Path("/etc/DanmakuFactory").resolve()


class DanmakuFactoryCommand(Command):
    def __init__(self):
        super().__init__("DanmakuFactory")

        config = DANMAKU_FACTORY_CONFIG_DIR.joinpath("DanmakuFactoryConfig.json")
        if config.exists():
            system_config = self.executable.with_name(config.name)
            system_config.unlink(missing_ok=True)
            system_config.symlink_to(config)

    def __call__(self, *args) -> str:
        return super().__call__("-c", *args, "--ignore-warnings")

    def convert(self, source: str, output: str) -> str:
        return self("-i", source, "-o", output)
