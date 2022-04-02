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
from typing import Optional

from pyflp._flobject import _FLObject
from pyflp._properties import (
    _BoolProperty,
    _EnumProperty,
    _FloatProperty,
    _UIntProperty,
)


class ChannelArp(_FLObject):
    """Miscellaneous settings -> Arp section.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#Arp)
    """

    class Direction(enum.IntEnum):
        """Arpeggio direction. Used by `ChannelArp.direction`."""

        Off = 0
        Up = 1
        Down = 2
        UpDownBounce = 3
        UpDownSticky = 4
        Random = 5

    # * Properties
    direction: Direction = _EnumProperty(Direction)

    range: Optional[int] = _UIntProperty()
    """Range (in octaves)."""

    chord: Optional[int] = _UIntProperty()
    """Index of the selected arpeggio chord."""

    repeat: Optional[int] = _UIntProperty()
    """Number of times a note is repeated."""

    time: Optional[float] = _FloatProperty()
    """Delay between two successive notes played."""

    gate: Optional[float] = _FloatProperty()
    """Results in a more staccato sound."""

    slide: Optional[bool] = _BoolProperty()
    """Whether arpeggio will slide between notes."""
