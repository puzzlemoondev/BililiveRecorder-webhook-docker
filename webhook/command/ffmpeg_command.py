from pathlib import Path
from tempfile import TemporaryDirectory

from .command import Command


class FFMPEGCommand(Command):
    def __init__(self):
        super().__init__("ffmpeg")

    def add_subtitles(self, source: str, subtitles: str, output: str) -> str:
        with TemporaryDirectory() as tmpdir:
            ass = Path(tmpdir).joinpath("subtitles.ass")
            ass.symlink_to(subtitles)

            return self(
                "-y",
                "-i",
                source,
                "-vf",
                f"ass={ass}",
                "-c:a",
                "copy",
                output,
            )
