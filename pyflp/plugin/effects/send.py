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

__all__ = ["FSend"]


class FSend(_EffectPlugin):
    """Implements Fruity Send. 4 knobs. 16 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Send.htm)
    """

    CHUNK_SIZE = 16

    def _setprop(self, n: str, v: int) -> None:
        r = self._r
        if n == "dry":
            r.seek(0)
        elif n == "pan":
            r.seek(4)
        elif n == "volume":
            r.seek(8)
        elif n == "send_to":
            r.seek(12)
        r.write_i(v)

    # * Properties
    dry: int = _UIntProperty(max_=256)
    """Dry/wet. Min: 0 (0%), Max: 256 (100%), Default: 256 (100%). Linear."""

    pan: int = _IntProperty(min_=-128, max_=127)
    """Pan. Min: -128 (100% left), Max: 127 (100% right),
    Default: 0 (Centred). Linear."""

    volume: int = _UIntProperty(max_=320)
    """Volume. Min: 0 (-INF db, 0.00), Max: 320 (5.6 dB, 1.90),
    Default: 256 (0.0 dB, 1.00). Logarithmic."""

    send_to: int = _IntProperty()
    """Target insert index; depends on insert routing. Default: -1 (Master)."""

    # * Parsing logic
    def _parse_data_event(self, e: DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        self._pan = r.read_I()
        self._dry = r.read_I()
        self._volume = r.read_I()
        self._send_to = r.read_i()
