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

"""Parses insert params event. Occurs after all insert events."""

import enum
import warnings
from typing import List

from bytesioex import BytesIOEx

from pyflp._event import _DataEvent
from pyflp.constants import DATA
from pyflp.insert.insert import Insert

try:
    from typing import Final
except ImportError:
    from typing_extensions import Final

__all__ = ["InsertParamsEvent"]


class InsertParamsEvent(_DataEvent):
    @enum.unique
    class EventID(enum.IntEnum):
        """Events inside event, nice design IL"""

        SlotEnabled = 0
        # SlotVolume = 1
        SlotMix = 1
        SendLevelStart = 64  # 64 - 191 are send level events
        Volume = 192
        Pan = 193
        StereoSeparation = 194
        LowLevel = 208
        BandLevel = 209
        HighLevel = 210
        LowFreq = 216
        BandFreq = 217
        HighFreq = 218
        LowQ = 224
        BandQ = 225
        HighQ = 226

    ID: Final = DATA + 17

    def __init__(self, ev: _DataEvent):
        super().__init__(ev.index, InsertParamsEvent.ID, ev.data)

    def parse(self, inserts: List[Insert]) -> bool:
        if not len(self.data) % 12 == 0:  # pragma: no cover
            warnings.warn("Unexpected data size; expected a divisible of 12.")
            return False
        data = BytesIOEx(self.data)

        while True:
            u1 = data.read_i()  # 4
            if u1 is None:
                break
            id = data.read_B()  # 5
            data.seek(1, 1)  # 6
            channel_data = data.read_H()  # 8
            msg = data.read_i()  # 12

            slot = channel_data & 0x3F
            insert = (channel_data >> 6) & 0x7F
            _ = channel_data >> 13  # TODO: Insert type
            ins = inserts[insert]

            if id == self.EventID.SlotEnabled:
                ins.slots[slot].enabled = True if msg != 0 else False
            elif id == self.EventID.SlotMix:
                ins.slots[slot].mix = msg
            elif id == self.EventID.Volume:
                ins.volume = msg
            elif id == self.EventID.Pan:
                ins.pan = msg
            elif id == self.EventID.StereoSeparation:
                ins.stereo_separation = msg
            elif id == self.EventID.LowLevel:
                ins.eq.low_level = msg
            elif id == self.EventID.BandLevel:
                ins.eq.band_level = msg
            elif id == self.EventID.HighLevel:
                ins.eq.high_level = msg
            elif id == self.EventID.LowFreq:
                ins.eq.low_freq = msg
            elif id == self.EventID.BandFreq:
                ins.eq.band_freq = msg
            elif id == self.EventID.HighFreq:
                ins.eq.high_freq = msg
            elif id == self.EventID.LowQ:
                ins.eq.low_q = msg
            elif id == self.EventID.BandQ:
                ins.eq.band_q = msg
            elif id == self.EventID.HighQ:
                ins.eq.high_q = msg
            elif id in range(self.EventID.SendLevelStart, len(inserts) + 1):
                route_id = id - self.EventID.SendLevelStart
                ins.route_volumes[route_id] = msg
        return True
