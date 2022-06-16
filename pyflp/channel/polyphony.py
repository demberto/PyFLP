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

from bytesioex import BytesIOEx

from pyflp._event import EventIDType, _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _EnumProperty, _IntProperty

__all__ = ["ChannelPolyphony", "ChannelPolyphonyEvent"]


class ChannelPolyphonyEvent(_DataEvent):
    """Implements `Channel.EventID.Polyphony`."""

    CHUNK_SIZE = 9

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        self.__r = r = BytesIOEx(data)
        self.max = r.read_I()
        self.slide = r.read_I()
        self.flags = ChannelPolyphony.Flags(r.read_B())

    def __repr__(self):
        return "<ChannelPolyphonyEvent {}, {}, {}>".format(
            f"max={self.max}", f"slide={self.slide}", f"flags={self.flags}"
        )

    def dump(self, n, v):
        r = self.__r
        if n == "max":
            r.seek(0)
            r.write_I(v)
        elif n == "slide":
            r.seek(4)
            r.write_I(v)
        elif n == "flags":
            r.seek(8)
            r.write_B(int(v))
        r.seek(0)
        super().dump(r.read())


class ChannelPolyphony(_FLObject):
    """Used by `Channel.polyphony`. Implemented by `ChannelPolyphonyEvent`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#Polyphony)
    """

    def _setprop(self, n, v):
        self.__cpe.dump(n, v)
        super()._setprop(n, v)

    @enum.unique
    class Flags(enum.IntFlag):
        """Used by `ChannelPolyphony.flags`."""

        None_ = 0
        """No options are enabled."""

        Mono = 1 << 0
        """**Mono** is enabled."""

        Porta = 1 << 1
        """**Porta** is enabled."""

        U1 = 1 << 2
        U2 = 1 << 3
        U3 = 1 << 4
        U4 = 1 << 5
        U5 = 1 << 6
        U6 = 1 << 7

    max: int = _IntProperty()
    """Maximum number of voices."""

    slide: int = _IntProperty()
    """Portamento time."""

    flags: Flags = _EnumProperty(Flags)
    """**Mono** and **Porta** buttons. See `ChannelPolyphonyFlags`."""

    def _parse_data_event(self, e: ChannelPolyphonyEvent) -> None:
        self.__cpe = self._events["polyphony"] = e
        self._max = e.max
        self._slide = e.slide
        self._flags = e.flags
