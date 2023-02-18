from .command import Command


class BiliupCommand(Command):
    def __init__(self, user_cookie: str):
        super().__init__("biliup")
        self.user_cookie = user_cookie

    def __call__(self, *args, **kwargs) -> str:
        args_with_user_cookie = ["-u", self.user_cookie, *args]
        return super().__call__(*args_with_user_cookie, **kwargs)

    def renew(self) -> str:
        return self("renew")

    def upload(self, video_path: str, **options) -> str:
        return self("upload", video_path, **options)
