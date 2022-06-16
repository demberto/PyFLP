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

from pyflp._event import DataEventType
from pyflp._properties import _IntProperty, _UIntProperty
from pyflp.plugin._plugin import _EffectPlugin

__all__ = ["FBalance"]


class FBalance(_EffectPlugin):
    """Implements Fruity Balance. 2 knobs. 8 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Balance.htm)
    """

    CHUNK_SIZE = 8

    def _setprop(self, n: str, v: int) -> None:
        r = self._r
        if n == "pan":
            r.seek(0)
        elif n == "volume":
            r.seek(4)
        r.write_i(v)

    # * Properties
    pan: int = _IntProperty(min_=-128, max_=127)
    """Panning. Min: -128, Max: 127, Default: 0 (0.50, Centred). Linear."""

    volume: int = _UIntProperty(max_=320)
    """Volume. Min: 0, Max: 320, Default: 256 (0.80, 0dB). Logarithmic."""

    def _parse_data_event(self, e: DataEventType) -> None:
        super()._parse_data_event(e)
        self._pan = self._r.read_I()
        self._volume = self._r.read_I()
