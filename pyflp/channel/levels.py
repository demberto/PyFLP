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

__all__ = ["ChannelLevels", "ChannelLevelsEvent"]


class ChannelLevelsEvent(_DataEvent):
    """Implements `Channel.EventID.Levels`."""

    CHUNK_SIZE = 24

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        self.__r = r = BytesIOEx(data)
        self.pan = r.read_i()
        self.volume = r.read_i()
        self.pitch_shift = r.read_i()
        self._u1 = r.read_i()
        self._u2 = r.read_i()
        self._u3 = r.read_i()

    def __repr__(self) -> str:
        return "<ChannelLevelsEvent {}, {}, {}>".format(
            f"pan={self.pan}",
            f"volume={self.volume}",
            f"pitch_shift={self.pitch_shift}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "pan":
            r.seek(0)
        elif n == "volume":
            r.seek(4)
        elif n == "pitch_shift":
            r.seek(8)
        elif n == "_u1":  # pragma: no cover
            r.seek(12)
        elif n == "_u2":  # pragma: no cover
            r.seek(16)
        elif n == "_u3":  # pragma: no cover
            r.seek(20)
        r.write_i(v)
        r.seek(0)
        super().dump(r.read())


class ChannelLevels(_FLObject):
    """Used by `Channel.levels`."""

    def _setprop(self, n, v):
        self.__cle.dump(n, v)
        super()._setprop(n, v)

    pan = _IntProperty()

    volume = _IntProperty()

    pitch_shift = _IntProperty()
    """Pitch shift (in cents)."""

    def _parse_data_event(self, e: ChannelLevelsEvent) -> None:
        self.__cle = self._events["levels"] = e
        self._pan = e.pan
        self._volume = e.volume
        self._pitch_shift = e.pitch_shift
