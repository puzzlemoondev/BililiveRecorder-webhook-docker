from typing import Optional

from celery.canvas import Signature as CelerySignature, chord, group

from .signature import Signature
from ....util import compact


class CompositeSignature(Signature):
    def __init__(self, *signatures: Signature):
        self.signatures = signatures
        self.callback: Optional[Signature] = None
        self.error_callback: Optional[Signature] = None

    @property
    def is_valid(self) -> bool:
        return bool(self.signatures)

    def get(self) -> Optional[CelerySignature]:
        if not self.is_valid:
            return

        def resolve(signature: Signature):
            return signature.get()

        resolved = compact(map(resolve, self.signatures))

        if self.callback is not None and (callback := self.callback.get()):
            result = chord(resolved, callback)
        else:
            result = group(resolved)

        if self.error_callback is not None:
            result = result.on_error(self.error_callback.get())

        return result
