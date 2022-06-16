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
from pyflp._properties import _UIntProperty
from pyflp.plugin._plugin import _SynthPlugin


class BooBass(_SynthPlugin):
    """Implements BooBass. 3 knobs. 16 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/BooBass.htm)"""  # noqa

    CHUNK_SIZE = 16

    def _setprop(self, n: str, v: int) -> None:
        r = self._r
        if n == "bass":
            r.seek(4)
        elif n == "mid":
            r.seek(8)
        elif n == "high":
            r.seek(12)
        r.write_I(v)

    bass: int = _UIntProperty(max_=65535)
    """Min: 0, Max: 65535, Default: 32767."""

    mid: int = _UIntProperty(max_=65535)
    """Min: 0, Max: 65535, Default: 32767."""

    high: int = _UIntProperty(max_=65535)
    """Min: 0, Max: 65535, Default: 32767."""

    def _parse_data_event(self, e: DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        r.seek(4)  # 1, 0, 0, 0
        self._bass = r.read_I()
        self._mid = r.read_I()
        self._high = r.read_I()
