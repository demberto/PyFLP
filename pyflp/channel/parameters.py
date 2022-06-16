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
from pyflp.channel.arp import ChannelArp

__all__ = ["ChannelParameters", "ChannelParametersEvent"]


class ChannelParametersEvent(_DataEvent):
    """Implements `Channel.EventID.Parameters`."""

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        c = ChannelParameters()
        arp = c.arp = self.arp = ChannelArp()

        # The size of the event has increased over the years
        r = BytesIOEx(data)
        r.seek(40)
        arp.direction = ChannelArp.Direction(r.read_I())
        arp.range = r.read_I()
        arp.chord = r.read_I()
        arp.time = r.read_f() + 1.0
        arp.gate = r.read_f()
        arp.slide = r.read_bool()
        r.seek(31, 1)
        arp.repeat = r.read_I()

    def __repr__(self) -> str:
        return f"<ChannelParametersEvent size={len(self.data)}>"


class ChannelParameters(_FLObject):
    def __init__(self):
        super().__init__()
        self.arp = ChannelArp()

    def _save(self) -> ChannelParametersEvent:
        e = super()._save()[0]
        oldlen = len(e._data)
        r = BytesIOEx(e._data)
        if oldlen > 40:
            r.seek(40)
            arp = self.arp
            r.write_I(arp.direction)
            r.write_I(arp.range)
            r.write_I(arp.chord)
            r.write_f(arp.time - 1.0)
            r.write_f(arp.gate)
            r.write_bool(arp.slide)

        # Prevent writing more data than previously was since write_* methods
        # can add more data than actually was, possibly making the FLP unopenable.
        r.seek(0)
        newbuf = r.read(oldlen)
        r.seek(0)
        r.write(newbuf)
        return e
