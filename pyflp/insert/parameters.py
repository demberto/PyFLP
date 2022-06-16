# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

import enum
from typing import Any, Optional

from bytesioex import BytesIOEx

from pyflp._event import EventIDType, _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _EnumProperty

__all__ = ["InsertFlags", "InsertParameters", "InsertParametersEvent"]


@enum.unique
class InsertFlags(enum.IntFlag):
    """Used by `InsertParametersEvent.flags`."""

    None_ = 0
    ReversePolarity = 1 << 0
    """Phase is inverted."""

    SwapLeftRight = 1 << 1
    """Left and right channels are swapped."""

    EnableEffects = 1 << 2
    """All slots are enabled. If this flag is absent, slots are bypassed."""

    Enabled = 1 << 3
    """Insert is in enabled state."""

    DisableThreadedProcessing = 1 << 4
    U5 = 1 << 5
    DockMiddle = 1 << 6
    """Layout -> Dock to -> Middle."""

    DockRight = 1 << 7
    """Layout -> Dock to -> Right."""

    U8 = 1 << 8
    U9 = 1 << 9
    ShowSeparator = 1 << 10
    """A separator is shown to the left of the insert."""

    Locked = 1 << 11
    """Insert is in locked state."""

    Solo = 1 << 12
    """Insert is the only active insert throught the mixer i.e soloed."""

    U13 = 1 << 13
    U14 = 1 << 14
    AudioTrack = 1 << 15
    """Whether insert is linked to an audio track."""


class InsertParametersEvent(_DataEvent):
    """Implements `Insert.EventID.Parameters`."""

    CHUNK_SIZE = 12

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        self.__r = r = BytesIOEx(data)
        self._u1 = r.read_I()
        self.flags = InsertFlags(r.read_I())
        self._u2 = r.read_I()

    def __repr__(self) -> str:
        return (
            f"<InsertParametersEvent flags={self.flags!r}, _u1={self._u1!r}, "
            f"_u2={self._u2!r}>"
        )

    def set(self, n: str, v: int):
        r = self.__r
        if n == "_u1":  # pragma: no cover
            r.seek(0)
            r.write_I(v)
        elif n == "flags":
            r.seek(4)
            r.write_I(v)
        elif n == "_u2":  # pragma: no cover
            r.seek(8)
            r.write_I(v)
        r.seek(0)
        self.dump(r.read())


class InsertParameters(_FLObject):
    """Used by `Insert.flags`, `Insert.enabled` and `Insert.locked`."""

    def _setprop(self, n: str, v: Any):
        self.__ipe.set(n, v)
        super()._setprop(n, v)

    flags: Optional[InsertFlags] = _EnumProperty(InsertFlags)

    def _parse_data_event(self, e: InsertParametersEvent) -> None:
        self.__ipe = self._events["polyphony"] = e
        self._flags = e.flags
