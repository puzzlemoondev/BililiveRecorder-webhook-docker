from dataclasses import dataclass
from pathlib import Path

from .base import Task, Input, Output
from ..util import is_empty


@dataclass
class RemoveTaskInput(Input):
    path: str


@dataclass
class RemoveTaskOutput(Output):
    path: str
    parent_removed: bool


class RemoveTask(Task[RemoveTaskInput, RemoveTaskOutput]):
    def __init__(self, input: RemoveTaskInput):
        super().__init__(input)

    def run(self) -> RemoveTaskOutput:
        path = Path(self.input.path)
        exists = path.exists()
        parent_removed = False

        if exists:
            path.unlink(missing_ok=True)
            parent_removed = self.remove_parent(path)

        return RemoveTaskOutput(path=self.input.path, parent_removed=parent_removed, skipped=not exists)

    @staticmethod
    def remove_parent(path: Path) -> bool:
        parent = path.parent
        if not is_empty(parent):
            return False
        parent.rmdir()
        return True
