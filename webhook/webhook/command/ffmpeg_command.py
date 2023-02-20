from .command import Command


class FFMPEGCommand(Command):
    def __init__(self):
        super().__init__("ffmpeg")

    def add_subtitles(self, source: str, output: str, subtitles: str) -> str:
        return self(
            "-y",
            "-i",
            source,
            "-vf",
            f'"ass={subtitles}"',
            "-crf",
            "18",
            "-c:a",
            "copy",
            output,
        )
