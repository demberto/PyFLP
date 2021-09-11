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
    DATA_TEXT_EVENTS
)
from pyflp.event import (
    Event,
    ByteEvent,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)
from pyflp.enums import (
    BYTE,
    DWORD,
    TEXT,
    DATA,
    WORD
)

class FLObject(abc.ABC):
    """Abstract base class for the FLP object model
    
    Rules for subclassing:
    1. __init__() should call super().__init__() before anything
    2. Use self._log for logging, no module-level logging
    3. Set _count = 0
    4. Set max_count wherever applicable 
    """
    _count = 0
    fl_version: FLVersion = None	# Set by ProjectParser and can be modified by Misc.version
    _verbose = False                # Set by ProjectParser._verbose
    
    def setprop(self, name: str, value: Any):
        """Reduces property setter boilerplate.
        Don't use this for properties derived from data events!
        
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
        # Assign value for use by getattr()
        setattr(self, '_' + name, value)

    def parse(self, event: Event) -> None:
        """Adds and parses and event from the event store.

        Args:
            event (Event): Event to parse
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

    def save(self) -> Optional[ValuesView[Event]]:
        return self._events.values()
    
    def __init__(self):
        self._idx = self._count
        FLObject._count += 1
        self._events: Dict[str, Event] = {}
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(logging.DEBUG if FLObject._verbose else logging.WARNING)
        super().__init__()