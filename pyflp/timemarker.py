"""Contains the types required for pattern and playlist timemarkers."""

import enum

from ._descriptors import EventProp
from ._events import DWORD, TEXT, EventEnum, U8Event, U32Event
from ._models import EventModel

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


class TimeMarker(EventModel):
    """A marker in the timeline of an :class:`Arrangement`.

    ![](https://bit.ly/3gltKbt)
    """

    def __repr__(self):
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
