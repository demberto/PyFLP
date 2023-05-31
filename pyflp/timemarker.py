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

"""Contains the types required for pattern and playlist timemarkers."""

from __future__ import annotations

import enum

from pyflp._descriptors import EventProp
from pyflp._events import DWORD, TEXT, EventEnum, U8Event, U32Event
from pyflp._models import EventModel, ModelReprMixin

__all__ = ["TimeMarkerID", "TimeMarkerType", "TimeMarker"]


@enum.unique
class TimeMarkerID(EventEnum):
    Numerator = (33, U8Event)
    Denominator = (34, U8Event)
    Position = (DWORD + 20, U32Event)
    Name = TEXT + 13


class TimeMarkerType(enum.IntEnum):
    Marker = 0
    """Normal text marker."""

    Signature = 134217728
    """Used for time signature markers."""


class TimeMarker(EventModel, ModelReprMixin):
    """A marker in the timeline of an :class:`Arrangement`.

    ![](https://bit.ly/3gltKbt)
    """

    def __str__(self) -> str:
        if self.type == TimeMarkerType.Marker:
            if self.name:
                return f"Marker {self.name!r} @ {self.position!r}"
            return f"Unnamed marker @ {self.position!r}"

        time_sig = f"{self.numerator}/{self.denominator}"
        if self.name:
            return f"Signature {self.name!r} ({time_sig}) @ {self.position!r}"
        return f"Unnamed {time_sig} signature @ {self.position!r}"

    denominator: EventProp[int] = EventProp[int](TimeMarkerID.Denominator)
    name = EventProp[str](TimeMarkerID.Name)
    numerator = EventProp[int](TimeMarkerID.Numerator)

    @property
    def position(self) -> int | None:
        if TimeMarkerID.Position in self.events.ids:
            event = self.events.first(TimeMarkerID.Position)
            if event.value < TimeMarkerType.Signature:
                return event.value
            return event.value - TimeMarkerType.Signature

    @property
    def type(self) -> TimeMarkerType | None:
        """The action with which a time marker is associated.

        [![](https://bit.ly/3RDM1yn)]()
        """
        if TimeMarkerID.Position in self.events.ids:
            event = self.events.first(TimeMarkerID.Position)
            if event.value >= TimeMarkerType.Signature:
                return TimeMarkerType.Signature
            return TimeMarkerType.Marker
