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

from pyflp._event import DataEventType
from pyflp._properties import _EnumProperty, _UIntProperty
from pyflp.plugin._plugin import _EffectPlugin

__all__ = ["Soundgoodizer"]


class Soundgoodizer(_EffectPlugin):
    """Implements Soundgoodizer. 2 knobs. 12 bytes

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Soundgoodizer.htm)
    """

    CHUNK_SIZE = 12

    class Mode(enum.IntEnum):
        """One of the Soundgoodizer modes. Used by `Soundgoodizer.mode`."""

        A = 0
        B = 1
        C = 2
        D = 3

    def _setprop(self, n: str, v: int) -> None:
        r = self._r
        if n == "mode":
            r.seek(4)
        elif n == "amount":
            r.seek(8)
        r.write_I(v)

    mode: Mode = _EnumProperty(Mode)
    """See `Mode`. Default: `Mode.A`"""

    amount: int = _UIntProperty(max_=1000)
    """Amount. Min: 0, Max: 1000, Default: 600. Logarithmic."""

    def _parse_data_event(self, e: DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        r.seek(4)  # 3, 0, 0, 0
        self._mode = r.read_I()
        self._amount = r.read_I()
