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
import enum
from typing import Any, Dict, Iterable, Optional

from pyflp._event import (
    _ByteEvent,
    _ColorEvent,
    _DataEventType,
    _DWordEvent,
    _DWordEventType,
    _EventType,
    _TextEvent,
    _WordEvent,
)
from pyflp._properties import _Property
from pyflp._validators import _OneOfValidator
from pyflp.constants import BYTE, DATA, DATA_TEXT_EVENTS, DWORD, TEXT, VALID_PPQS, WORD
from pyflp.exceptions import MaxInstancesError
from pyflp.utils import FLVersion


class _FLObjectMeta(type):
    """Metaclass for `_FLObject`."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_ppq":
            _OneOfValidator(VALID_PPQS).validate(value)
        return super().__setattr__(name, value)


class _FLOBjectAbstractMeta(_FLObjectMeta, abc.ABCMeta):
    """Abstract metaclass for `_FLObject` (to avoid MRO errors)."""

    pass


class _FLObject(metaclass=_FLOBjectAbstractMeta):
    """ABC for the FLP object model."""

    _ppq = 0
    _count = 0

    # Set by Parser and can be modified by Misc.version
    _fl_version: Optional[FLVersion] = None

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

    def _setprop(self, n, v):
        """Dumps a property value to the underlying event
        provided `_events` has a key with name `n`."""

        ev = self._events.get(n)
        if ev is not None:
            ev.dump(v)

    # * Parsing logic
    def parse_event(self, event: _EventType) -> None:
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
            event.id = self.EventID(event.id)
        except ValueError:
            # The delegates below should assign the proper value
            pass

        id = event.id

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

    def _parse_byte_event(self, _: _ByteEvent) -> None:  # pragma: no cover
        pass

    def _parse_word_event(self, _: _WordEvent) -> None:  # pragma: no cover
        pass

    def _parse_dword_event(self, _: _DWordEventType) -> None:  # pragma: no cover
        pass

    def _parse_text_event(self, _: _TextEvent) -> None:  # pragma: no cover
        pass

    def _parse_data_event(self, _: _DataEventType) -> None:  # pragma: no cover
        pass

    # * Property parsing logic
    def _parseprop(self, event: _EventType, key: str, value: Any):
        """Reduces boilerplate for `parse_event()` delegate methods.

        Not to be used unless helper `_parse_*` methods aren't useful.
        """
        self._events[key] = event
        setattr(self, "_" + key, value)

    def _parse_bool(self, event: _ByteEvent, key: str):
        """`self._parseprop` for boolean properties."""
        self._parseprop(event, key, event.to_bool())

    def _parse_B(self, event: _ByteEvent, key: str):
        """`self._parseprop` for uint8 properties."""
        self._parseprop(event, key, event.to_uint8())

    def _parse_b(self, event: _ByteEvent, key: str):
        """`self._parseprop` for int8 properties."""
        self._parseprop(event, key, event.to_int8())

    def _parse_H(self, event: _WordEvent, key: str):
        """`self._parseprop` for uint16 properties."""
        self._parseprop(event, key, event.to_uint16())

    def _parse_h(self, event: _WordEvent, key: str):
        """`self._parseprop` for int16 properties."""
        self._parseprop(event, key, event.to_int16())

    def _parse_I(self, event: _DWordEvent, key: str):
        """`self._parseprop` for uint32 properties."""
        self._parseprop(event, key, event.to_uint32())

    def _parse_i(self, event: _DWordEvent, key: str):
        """`self._parseprop` for int32 properties."""
        self._parseprop(event, key, event.to_int32())

    def _parse_s(self, event: _TextEvent, key: str):
        """`self._parseprop` for string properties."""
        self._parseprop(event, key, event.to_str())

    def _parse_color(self, event: _ColorEvent, key: str = "color"):
        """`self._parseprop` for Color properties."""
        self._parseprop(event, key, event.to_color())

    def _parse_flobject(self, event: _EventType, key: str, value: Any):
        """`self._parseprop` for `FLObject` properties.

        e.g `Channel.delay` is of type `ChannelDelay` which is itself an
        `FLObject` subclass. This method works only for classes which work on
        a single event and occur once inside the container class!
        """
        if not hasattr(self, "_" + key):
            if not isinstance(value, _FLObject):
                raise TypeError
            self._parseprop(event, key, value)
        obj: _FLObject = getattr(self, "_" + key)
        obj.parse_event(event)

    def _save(self) -> Iterable[_EventType]:
        """Returns the events stored in `self._events` as an iterable."""
        return self._events.values()

    def __init__(self):
        cls = type(self)
        self._idx = cls._count
        cls._count += 1
        self._events: Dict[str, _EventType] = {}


class _MaxInstancedFLObject(_FLObject):
    """Used when a limit has too be imposed on the number of instances."""

    max_count = 1

    def __init__(self):
        cls = type(self)
        if cls._count > cls.max_count:
            raise MaxInstancesError(cls)
        super().__init__()
