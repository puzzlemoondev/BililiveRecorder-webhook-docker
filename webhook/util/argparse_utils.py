import json
from argparse import Action


class ParseJSONAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        json_data = json.loads(values)
        setattr(namespace, self.dest, json_data)
