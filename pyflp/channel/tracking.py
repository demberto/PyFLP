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

__all__ = ["ChannelTracking", "ChannelTrackingEvent"]


class ChannelTrackingEvent(_DataEvent):
    """Implements `Channel.EventID.Tracking`."""

    CHUNK_SIZE = 16

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        self.__r = r = BytesIOEx(data)
        self.middle_value = r.read_i()
        self.pan = r.read_i()
        self.mod_x = r.read_i()
        self.mod_y = r.read_i()

    def __repr__(self) -> str:
        return "<ChannelTrackingEvent {}, {}, {}, {}>".format(
            f"middle_value={self.middle_value}",
            f"pan={self.pan}",
            f"mod_x={self.mod_x}",
            f"mod_y={self.mod_y}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "middle_value":
            r.seek(0)
        elif n == "pan":
            r.seek(4)
        elif n == "mod_x":
            r.seek(8)
        elif n == "mod_y":
            r.seek(12)
        r.write_i(v)
        r.seek(0)
        super().dump(r.read())


class ChannelTracking(_FLObject):
    """Used by `Channel.tracking`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#Tracking)
    """

    def _setprop(self, n, v):
        self.__cte.dump(n, v)
        super()._setprop(n, v)

    middle_value: int = _IntProperty()

    pan: int = _IntProperty()

    mod_x: int = _IntProperty()

    mod_y: int = _IntProperty()

    def _parse_data_event(self, e: ChannelTrackingEvent) -> None:
        self.__cte = self._events["levels"] = e
        self._middle_value = e.middle_value
        self._pan = e.pan
        self._mod_x = e.mod_x
        self._mod_y = e.mod_y
