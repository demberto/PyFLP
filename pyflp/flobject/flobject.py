import abc
import logging
from typing import (
    Any,
    Dict,
    Optional,
    ValuesView
)

from pyflp.utils import (
    FLVersion,
    DATA_TEXT_EVENTS,
    BYTE,
    DWORD,
    TEXT,
    DATA,
    WORD
)
from pyflp.event import (
    Event,
    ByteEvent,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)

__all__ = ['FLObject']

class FLObject(abc.ABC):
    """Abstract base class for the FLP object model.

    Rules for subclassing:
    1. __init__() should call super().__init__() before anything
    2. Use self._log for logging, no module-level logging
    3. Set `_count` = 0
    4. Set `max_count` wherever applicable
    """

    _count = 0
    fl_version: FLVersion = None	# Set by Parser and can be modified by Misc.version
    _verbose = False                # Set by Parser._verbose

    def setprop(self, name: str, value: Any):
        """Reduces property setter boilerplate.
        
        1. Gets corresponding event from event store.
        2. Dumps the value to that event.
        3. Assigns the local variable the value.
        
        Don't use this for `pyflp.event.data_event.DataEvent` properties!

        Args:
            name (str): Name of the property
            value (Any): Value to assign to property and dump in event store
        """

        # Dump value to event store if event exists
        event = self._events.get(name)
        if event:
            self._log.info(f"Dumping value {value} to {repr(event)}")
            event.dump(value)
        else:
            self._log.error(f"'{name}' not present in events dict")
        
        # Assign value to local variable
        setattr(self, '_' + name, value)

    #region Parsing logic
    def parse(self, event: Event) -> None:
        """Adds and parses an event from the event store.
        
        Uses delegate methods `_parse_byte_event`, `_parse_word_event`,
        `_parse_dword_event`, `_parse_text_event` and `_parse_data_event`.
        
        Can be overriden when a derived class contains properties holding
        FLObject derived classes, for e.g. `pyflp.flobject.insert.insert.Insert.slots`
        holds `List[pyflp.flobject.insert.insert_slot.InsertSlot]` and whenever the
        event ID belongs to `pyflp.flobject.insert.event_id.InsertSlotEventID`,
        it is passed to the slot's `parse()` method directly.

        Args:
            event (Event): Event to send to `parseprop`.
        """
        
        id = event.id
        if id in range(BYTE, WORD):
            self._parse_byte_event(event)
        elif id in range(WORD, DWORD):
            self._parse_word_event(event)
        elif id in range(DWORD, TEXT):
            self._parse_dword_event(event)
        elif id in range(TEXT, DATA) or id in DATA_TEXT_EVENTS:
            self._parse_text_event(event)
        else:
            self._parse_data_event(event)

    def _parse_byte_event(self, event: ByteEvent) -> None:
        pass

    def _parse_word_event(self, event: WordEvent) -> None:
        pass

    def _parse_dword_event(self, event: DWordEvent) -> None:
        pass

    def _parse_text_event(self, event: TextEvent) -> None:
        pass

    def _parse_data_event(self, event: DataEvent) -> None:
        pass
    #endregion
    
    #region Property parsing logic
    def parseprop(self, event: Event, key: str, value: Any):
        """Reduces boilerplate for `parse()` delegate methods.
        
        The name of the local variable and the dictionary key must be equal.
        
        Args:
            event (Event): Event to parse and add to event store `_events`.
            key (str): Dictionary key, provided that '_' + key == *name_of_local_variable*.
            value (Any): Value to assign to the local variable.
            
        Not to be used directly unless the helper `parse_*_prop` methods don't help.
        """
        
        self._events[key] = event
        setattr(self, '_' + key, value)
    
    def parse_bool_prop(self, event: ByteEvent, key: str):
        """`parseprop` for boolean properties."""
        
        self.parseprop(event, key, event.to_bool())
    
    def parse_uint8_prop(self, event: ByteEvent, key: str):
        """`parseprop` for uint8 properties."""
        
        self.parseprop(event, key, event.to_uint8())
    
    def parse_int8_prop(self, event: ByteEvent, key: str):
        """`parseprop` for int8 properties."""
        
        self.parseprop(event, key, event.to_int8())
    
    def parse_uint16_prop(self, event: WordEvent, key: str):
        """`parseprop` for uint16 properties."""
        
        self.parseprop(event, key, event.to_uint16())
    
    def parse_int16_prop(self, event: WordEvent, key: str):
        """`parseprop` for int16 properties."""
        
        self.parseprop(event, key, event.to_int16())
    
    def parse_uint32_prop(self, event: DWordEvent, key: str):
        """`parseprop` for uint32 properties."""
        
        self.parseprop(event, key, event.to_uint32())
    
    def parse_int32_prop(self, event: DWordEvent, key: str):
        """`parseprop` for int32 properties."""
        
        self.parseprop(event, key, event.to_int32())
    
    def parse_str_prop(self, event: TextEvent, key: str):
        """`parseprop` for string properties."""
        
        self.parseprop(event, key, event.to_str())
    #endregion
    
    def save(self) -> Optional[ValuesView[Event]]:
        """Returns the events stored in `_events`.
        
        When overriden a List should be returned instead of ValuesView.
        """
        
        return self._events.values()

    def __init__(self):
        self._idx = self._count
        self._count += 1
        self._events: Dict[str, Event] = {}
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(logging.DEBUG if FLObject._verbose else logging.WARNING)
        self._log.info(f"__init__() called, count: {self._count}")
        super().__init__()