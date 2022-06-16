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

from typing import List, Optional

from bytesioex import BytesIOEx

from pyflp._event import DataEventType, EventType
from pyflp._flobject import _FLObject


class _Plugin(_FLObject):
    """Represents a native or VST2/VST3 effect or instrument.

    Parses only `Channel.EventID.Plugin`/`InsertSlot.EventID.Plugin`.
    """

    CHUNK_SIZE: Optional[int] = None
    """Expected size of event data passed to `parse_event`.

    Parsing is skipped in case the size is not equal to this.
    """

    def _save(self) -> List[EventType]:
        self._r.seek(0)
        self._events["plugin"].dump(self._r.read())
        return super()._save()

    def _parse_data_event(self, e: DataEventType) -> None:
        self._events["plugin"] = e
        if self.CHUNK_SIZE is not None:
            dl = len(e.data)
            if dl != self.CHUNK_SIZE:  # pragma: no cover
                return
        self._r = BytesIOEx(e.data)


class _EffectPlugin(_Plugin):
    """Represents a native or VST2/VST3 effect. Used by `InsertSlot.plugin`."""


class _SynthPlugin(_Plugin):
    """Represents a native or VST2/VST3 instrument. Used by `Channel.plugin`."""
