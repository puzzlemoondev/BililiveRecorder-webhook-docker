from json import loads, JSONDecodeError

from click import ParamType


class JSONParamType(ParamType):
    name = "json"

    def convert(self, value, param, ctx) -> dict:
        if isinstance(value, dict):
            return value

        try:
            return loads(value)
        except (TypeError, JSONDecodeError):
            self.fail(f"{value!r} is not a valid json", param, ctx)


JSON = JSONParamType()
