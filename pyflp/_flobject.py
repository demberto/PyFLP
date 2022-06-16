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

import abc
import dataclasses
import enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar

from pyflp._event import (
    ByteEventType,
    ColorEventType,
    DataEventType,
    DWordEventType,
    EventType,
    TextEventType,
    WordEventType,
)
from pyflp._properties import _Property
from pyflp.constants import BYTE, DATA, DATA_TEXT_EVENTS, DWORD, TEXT, WORD

if TYPE_CHECKING:
    from pyflp.project import Project


@dataclasses.dataclass
class MaxInstances:
    inserts: int = 0
    """Maximum number of inserts per project."""

    slots: int = 10
    """Maximum number of slots per insert."""


class _FLObject(abc.ABC):
    """ABC for the FLP object model."""

    @enum.unique
    class EventID(enum.IntEnum):
        """Stores event IDs used by `parse_event` delegates."""

    def __repr__(self) -> str:
        reprs = []
        for k in vars(type(self)).keys():
            prop = getattr(type(self), k)
            attr = getattr(self, k)
            if isinstance(prop, _Property):
                reprs.append(f"{k}={attr!r}")
        return f"<{type(self).__name__} {', '.join(reprs)}>"

    def _setprop(self, n: str, v: Any) -> None:
        """Dumps a property value to the underlying event
        provided `_events` has a key with name `n`."""

        ev = self._events.get(n)
        if ev is not None:
            ev.dump(v)

    # * Parsing logic
    def parse_event(self, event: EventType) -> None:
        """Adds and parses an event from the event store.

        Note: Delegates
            Uses delegate methods `_parse_byte_event`, `_parse_word_event`,
            `_parse_dword_event`, `_parse_text_event` and `_parse_data_event`.

        Tip: Overriding
            Can be overriden when a derived class contains properties
            holding `FLObject` derived classes, *for e.g.* `Insert.slots` holds
            `List[InsertSlot]` and whenever the event ID belongs to
            `InsertSlot.EventID`, it is passed to the slot's `parse_event`
            method directly.

        Args:
            event (Event): Event to dispatch to `self._parseprop`."""

        # Convert event.id from an int to a member of the class event ID
        try:
            event.id_ = self.EventID(event.id_)
        except ValueError:
            # The delegates below should assign the proper value
            pass

        id = event.id_

        if id >= BYTE and id < WORD:
            self._parse_byte_event(event)
        elif id >= WORD and id < DWORD:
            self._parse_word_event(event)
        elif id >= DWORD and id < TEXT:
            self._parse_dword_event(event)
        elif (id >= TEXT and id < DATA) or id in DATA_TEXT_EVENTS:
            self._parse_text_event(event)
        else:
            self._parse_data_event(event)

    def _parse_byte_event(self, _: ByteEventType) -> None:  # pragma: no cover
        pass

    def _parse_word_event(self, _: WordEventType) -> None:  # pragma: no cover
        pass

    def _parse_dword_event(self, _: DWordEventType) -> None:  # pragma: no cover
        pass

    def _parse_text_event(self, _: TextEventType) -> None:  # pragma: no cover
        pass

    def _parse_data_event(self, _: DataEventType) -> None:  # pragma: no cover
        pass

    # * Property parsing logic
    def _parseprop(self, event: EventType, key: str, value: Any) -> None:
        """Reduces boilerplate for `parse_event()` delegate methods.

        Not to be used unless helper `_parse_*` methods aren't useful.
        """
        self._events[key] = event
        setattr(self, "_" + key, value)

    def _parse_bool(self, event: ByteEventType, key: str) -> None:
        """`self._parseprop` for bool properties."""
        self._parseprop(event, key, event.to_bool())

    def _parse_B(self, event: ByteEventType, key: str) -> None:  # noqa
        """`self._parseprop` for uint8 properties."""
        self._parseprop(event, key, event.to_uint8())

    def _parse_b(self, event: ByteEventType, key: str) -> None:
        """`self._parseprop` for int8 properties."""
        self._parseprop(event, key, event.to_int8())

    def _parse_H(self, event: WordEventType, key: str) -> None:  # noqa
        """`self._parseprop` for uint16 properties."""
        self._parseprop(event, key, event.to_uint16())

    def _parse_h(self, event: WordEventType, key: str) -> None:
        """`self._parseprop` for int16 properties."""
        self._parseprop(event, key, event.to_int16())

    def _parse_I(self, event: DWordEventType, key: str) -> None:  # noqa
        """`self._parseprop` for uint32 properties."""
        self._parseprop(event, key, event.to_uint32())

    def _parse_i(self, event: DWordEventType, key: str) -> None:
        """`self._parseprop` for int32 properties."""
        self._parseprop(event, key, event.to_int32())

    def _parse_s(self, event: TextEventType, key: str) -> None:
        """`self._parseprop` for string properties."""
        self._parseprop(event, key, event.to_str())

    def _parse_color(self, event: ColorEventType, key: str = "color") -> None:
        """`self._parseprop` for Color properties."""
        self._parseprop(event, key, event.to_color())

    def _parse_flobject(self, event: EventType, key: str, value: Any) -> None:
        """`self._parseprop` for `FLObject` properties.

        e.g `Channel.delay` is of type `ChannelDelay` which is itself an
        `FLObject` subclass. This method works only for classes which work on
        a single event and occur once inside the container class!
        """
        if not hasattr(self, "_" + key):
            self._parseprop(event, key, value)
        obj: _FLObject = getattr(self, "_" + key)
        obj.parse_event(event)

    def _save(self) -> List[EventType]:
        """Dumps pending changes into the events and returns them a list."""
        return list(self._events.values())

    def __init__(
        self,
        project: "Optional[Project]" = None,
        max_instances: Optional[MaxInstances] = None,
    ) -> None:
        self._project = project
        self._max_instances = max_instances
        self._events: Dict[str, EventType] = {}


_FLObjectType = TypeVar("_FLObjectType", bound=_FLObject)
