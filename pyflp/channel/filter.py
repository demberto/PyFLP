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

from pyflp._event import _TextEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _StrProperty
from pyflp.constants import TEXT

__all__ = ["Filter"]


class Filter(_FLObject):
    """Channel display filter. Default: 'Unsorted', 'Audio'
    and 'Automation'. Used by `Channel.filter_channel`."""

    @enum.unique
    class EventID(enum.IntEnum):
        """Event IDs used by `FilterChannel`."""

        Name = TEXT + 39
        """See `FilterChannel.name`."""

    name: str = _StrProperty()
    """Name of the filter channel."""

    def _parse_text_event(self, e: _TextEvent) -> None:
        if e.id_ == Filter.EventID.Name:
            self._parse_s(e, "name")
