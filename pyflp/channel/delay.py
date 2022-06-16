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

from typing import Any, Optional

from bytesioex import BytesIOEx

from pyflp._event import EventIDType, _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _IntProperty

__all__ = ["ChannelDelay", "ChannelDelayEvent"]


class ChannelDelayEvent(_DataEvent):
    """Implements `Channel.EventID.Delay`."""

    CHUNK_SIZE = 20

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        self.__r = r = BytesIOEx(data)
        self.feedback = r.read_I()
        self.pan = r.read_I()
        self.pitch_shift = r.read_I()
        self.echo = r.read_I()
        self.time = r.read_I()

    def __repr__(self) -> str:
        return "<ChannelDelayEvent {}, {}, {}, {}, {}>".format(
            f"feedback={self.feedback}",
            f"pan={self.pan}",
            f"pitch_shift={self.pitch_shift}",
            f"echo={self.echo}",
            f"time={self.time}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "feedback":
            r.seek(0)
        elif n == "pan":
            r.seek(4)
        elif n == "pitch_shift":
            r.seek(8)
        elif n == "echo":
            r.seek(12)
        elif n == "time":
            r.seek(16)
        r.write_I(v)
        r.seek(0)
        super().dump(r.read())


class ChannelDelay(_FLObject):
    """Used by `Channel.delay`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#EchoDelay)
    """

    def _setprop(self, n: str, v: Any):
        self.__cde.dump(n, v)
        super()._setprop(n, v)

    feedback: Optional[int] = _IntProperty()

    pan: Optional[int] = _IntProperty()

    pitch_shift: Optional[int] = _IntProperty()

    echo: Optional[int] = _IntProperty()

    time: Optional[int] = _IntProperty()

    def _parse_data_event(self, e: ChannelDelayEvent) -> None:
        self.__cde = self._events["delay"] = e
        self._feedback = e.feedback
        self._pan = e.pan
        self._pitch_shift = e.pitch_shift
        self._echo = e.echo
        self._time = e.time
