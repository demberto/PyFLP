import struct
import warnings
from typing import List

from bytesioex import BytesIOEx

from pyflp._event import _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _FloatProperty, _UIntProperty

__all__ = ["PatternController", "PatternControllersEvent"]


class PatternController(_FLObject):
    position = _UIntProperty()
    """Position relative to pattern start."""

    target_channel = _UIntProperty()
    """Target channel"""

    target_flags = _UIntProperty()
    """TODO"""

    value = _FloatProperty()
    """Either 0.0 to 1.0 for VST parameters or
    0 to 12800 for FL's internal parameters."""

    u1 = _UIntProperty()
    """TODO"""

    u2 = _UIntProperty()
    """TODO"""

    def __repr__(self) -> str:
        return "<PatternController {}, {}, {}, {}>".format(
            f"position={self.position}",
            f"target_channel={self.target_channel}",
            f"target_flags={self.target_flags}",
            f"value={self.value}",
        )

    def _save(self) -> bytes:
        return struct.pack(
            "I4Bf",
            self.position,
            self.u1,
            self.u2,
            self.target_channel,
            self.target_flags,
            self.value,
        )


class PatternControllersEvent(_DataEvent):
    def __init__(self, data: bytes):
        from pyflp.pattern.pattern import Pattern

        super().__init__(Pattern.EventID.Controllers, data)
        self.controllers: List[PatternController] = []
        dl = len(data)
        if dl % 12 != 0:  # pragma: no cover
            warnings.warn(f"Unexpected data size. Expected a divisible of 12; got {dl}")
            return
        self.__r = r = BytesIOEx(data)
        while True:
            position = r.read_I()
            if position is None:
                break

            c = PatternController()
            c.position = position
            c.u1 = r.read_B()
            c.u2 = r.read_B()
            c.target_channel = r.read_B()
            c.target_flags = r.read_B()
            c.value = r.read_f()
            self.controllers.append(c)

    def __repr__(self) -> str:
        return f"<PatternControllersEvent: {len(self.controllers)} controllers>"
