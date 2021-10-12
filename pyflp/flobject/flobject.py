import abc
import logging
from typing import Any, Dict, Optional, ValuesView

from pyflp.utils import FLVersion, DATA_TEXT_EVENTS, BYTE, DWORD, TEXT, DATA, WORD
from pyflp.event import (
    Event,
    ByteEvent,
    EventType,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent,
)

__all__ = ["FLObject"]

logging.basicConfig()


class FLObject(abc.ABC):
    """Abstract base class for the FLP object model.

    Rules for subclassing:
    1. `__init__()` should call `super().__init__()` before anything
    2. Use `self._log` for logging, no pre-module logging!
    3. Set `_count` = 0
    4. Set `max_count` wherever applicable."""

    _count = 0

    # Set by Parser and can be modified by Misc.version
    fl_version: Optional[FLVersion] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object>"

    def _setprop(self, name: str, value: Any):
        """Reduces property setter boilerplate.

        1. Gets corresponding event from event store.
        2. Dumps the value to that event.
        3. Assigns the local variable the value.

        Don't use this for `pyflp.event.data_event.DataEvent` properties!

        Args:
            name (str): Name of the property
            value (Any): Value to assign to property and dump in event store."""

        # Dump value to event store if event exists
        event = self._events.get(name)
        if event:
            self._log.info(f"Dumping value {value} to {repr(event)}")
            event.dump(value)
        else:
            self._log.error(f"'{name}' not present in events dict")

        # Assign value to local variable
        setattr(self, "_" + name, value)

    # * Parsing logic
    def parse_event(self, event: EventType) -> None:
        """Adds and parses an event from the event store.

        Uses delegate methods `__parse_byte_event`, ``,
        `_parse_dword_event`, `__parse_text_event` and `__parse_data_event`.

        Can be overriden when a derived class contains properties holding
        `FLObject` derived classes, for e.g. `pyflp.flobject.insert.insert.Insert.slots`
        holds `List[pyflp.flobject.insert.insert_slot.InsertSlot]` and whenever the
        event ID belongs to `pyflp.flobject.insert.event_id.InsertSlotEventID`,
        it is passed to the slot's `parse()` method directly.

        Args:
            event (Event): Event to send to `self._parseprop`."""

        id = event.id
        if id in range(BYTE, WORD):
            assert isinstance(event, ByteEvent)
            self._parse_byte_event(event)
        elif id in range(WORD, DWORD):
            assert isinstance(event, WordEvent)
            self._parse_word_event(event)
        elif id in range(DWORD, TEXT):
            assert isinstance(event, DWordEvent)
            self._parse_dword_event(event)
        elif id in range(TEXT, DATA) or id in DATA_TEXT_EVENTS:
            assert isinstance(event, TextEvent)
            self._parse_text_event(event)
        else:
            assert isinstance(event, DataEvent)
            self._parse_data_event(event)

    def _parse_byte_event(self, ev: ByteEvent) -> None:
        pass

    def _parse_word_event(self, ev: WordEvent) -> None:
        pass

    def _parse_dword_event(self, ev: DWordEvent) -> None:
        pass

    def _parse_text_event(self, ev: TextEvent) -> None:
        pass

    def _parse_data_event(self, ev: DataEvent) -> None:
        pass

    # * Property parsing logic
    def _parseprop(self, event: EventType, key: str, value: Any):
        """Reduces boilerplate for `parse_event()` delegate methods.

        Conditions to use this function:
            The name of the local variable and the dictionary key must be equal.

        Args:
            event (Event): Event to parse and add to event store `_events`.
            key (str): Dictionary key, provided that '_' + key == *name_of_local_variable*.
            value (Any): Value to assign to the local variable.

        Not to be used unless helper `__parse_*_prop` methods aren't useful."""

        self._events[key] = event
        setattr(self, "_" + key, value)

    def _parse_bool_prop(self, event: ByteEvent, key: str):
        """`self._parseprop` for boolean properties."""
        self._parseprop(event, key, event.to_bool())

    def _parse_uint8_prop(self, event: ByteEvent, key: str):
        """`self._parseprop` for uint8 properties."""
        self._parseprop(event, key, event.to_uint8())

    def _parse_int8_prop(self, event: ByteEvent, key: str):
        """`self._parseprop` for int8 properties."""
        self._parseprop(event, key, event.to_int8())

    def _parse_uint16_prop(self, event: WordEvent, key: str):
        """`self._parseprop` for uint16 properties."""
        self._parseprop(event, key, event.to_uint16())

    def _parse_int16_prop(self, event: WordEvent, key: str):
        """`self._parseprop` for int16 properties."""
        self._parseprop(event, key, event.to_int16())

    def _parse_uint32_prop(self, event: DWordEvent, key: str):
        """`self._parseprop` for uint32 properties."""
        self._parseprop(event, key, event.to_uint32())

    def _parse_int32_prop(self, event: DWordEvent, key: str):
        """`self._parseprop` for int32 properties."""
        self._parseprop(event, key, event.to_int32())

    def _parse_str_prop(self, event: TextEvent, key: str):
        """`self._parseprop` for string properties."""
        self._parseprop(event, key, event.to_str())

    def _parse_flobject_prop(self, event: DataEvent, key: str, value: Any):
        """`self._parseprop` for `FLObject` properties. e.g `Channel.delay`
        is of type `ChannelDelay` which is itself an `FLObject` subclass.

        This method works only for classes which work on a single event
        and occur once inside the container class!"""

        if not hasattr(self, "_" + key):
            assert issubclass(type(value), FLObject)
            self._parseprop(event, key, value)
        obj = getattr(self, "_" + key)  # type: ignore
        obj.parse_event(event)  # type: ignore

    def save(self) -> ValuesView[Event]:
        """Returns the events stored in `self._events` as a read only view.

        **Rules for overriding:**
        1. Since this function call must get logged, always call super().save() first.
        2. Save that to a variable called *events*, as this is a ValuesView, changes to
        the `self._events` dictionary while get reflected in *events*, if a list would
        have been returned, this would not have been possible.
        3. Simply return *events*, instead of calling `self._events.values()`."""

        self._log.info(f"index: {self._idx}")
        return self._events.values()

    def __init__(self):
        self._idx = self.__class__._count
        self.__class__._count += 1
        self._events: Dict[str, Event] = {}
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info(f"count: {self.__class__._count}")
        super().__init__()
