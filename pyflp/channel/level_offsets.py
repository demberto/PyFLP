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

from bytesioex import BytesIOEx

from pyflp._event import EventIDType, _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _IntProperty

__all__ = ["ChannelLevelOffsets", "ChannelLevelOffsetsEvent"]


class ChannelLevelOffsetsEvent(_DataEvent):
    """Implements `Channel.EventID.LevelOffsets`."""

    CHUNK_SIZE = 20

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        self.__r = r = BytesIOEx(data)
        self.pan = r.read_i()
        self.volume = r.read_i()
        self._u1 = r.read_i()
        self.mod_x = r.read_i()
        self.mod_y = r.read_i()

    def __repr__(self):
        return "<ChannelLevelOffsetsEvent {}, {}, {}, {}>".format(
            f"pan={self.pan}",
            f"volume={self.volume}",
            f"mod_x={self.mod_x}",
            f"mod_y={self.mod_y}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "pan":
            r.seek(0)
        elif n == "volume":
            r.seek(4)
        elif n == "_u1":  # pragma: no cover
            r.seek(8)
        elif n == "mod_x":
            r.seek(12)
        elif n == "mod_y":
            r.seek(16)
        r.write_I(v)
        r.seek(0)
        super().dump(r.read())


class ChannelLevelOffsets(_FLObject):
    """Used by `Channel.delay`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#EchoDelay)
    """

    def _setprop(self, n, v):
        self.__cloe.dump(n, v)
        super()._setprop(n, v)

    pan = _IntProperty()

    volume = _IntProperty()

    mod_x = _IntProperty()

    mod_y = _IntProperty()

    def _parse_data_event(self, e: ChannelLevelOffsetsEvent) -> None:
        self.__cloe = self._events["delay"] = e
        self._pan = e.pan
        self._volume = e.volume
        self._mod_x = e.mod_x
        self._mod_y = e.mod_y
