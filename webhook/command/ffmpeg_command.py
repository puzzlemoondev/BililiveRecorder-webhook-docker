import shlex
from pathlib import Path

from .command import Command


class FFMPEGCommand(Command):
    def __init__(self):
        super().__init__("ffmpeg")

    def add_subtitles(self, source: str, subtitles: str, output: str) -> str:
        if Path(output).suffix != ".mp4":
            raise ValueError(f"invalid extension: {output}")
        return self(
            "-y",
            "-i",
            source,
            "-vf",
            shlex.quote(f"ass={subtitles}"),
            "-c:a",
            "copy",
            output,
        )
