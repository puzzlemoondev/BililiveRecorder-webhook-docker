from .command import Command


class BiliupCommand(Command):
    def __init__(self, user_cookie: str):
        super().__init__("biliup")
        self.user_cookie = user_cookie

    def __call__(self, *args) -> str:
        return super().__call__("-u", self.user_cookie, *args)

    def renew(self) -> str:
        return self("renew")

    def upload(self, video_path: str, *options: str) -> str:
        return self("upload", video_path, *options)
