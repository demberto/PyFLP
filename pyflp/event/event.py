import abc
import enum
from typing import Union

from pyflp.utils import (
    DATA_TEXT_EVENTS,
    buflen_to_varint,
    WORD,
    DWORD,
    TEXT,
    DATA
)

class Event(abc.ABC):
    """Abstract base class which represents an event"""
    
    _count = 0

    @abc.abstractproperty
    def size(self) -> int:
        pass

    @abc.abstractmethod
    def dump(self, new_data):
        """Converts python data types into equivalent C types and dumps them to self.data"""
        pass

    def to_raw(self) -> bytes:
        """Used by Project.save(). Overriden by _VariabledSizedEvent"""
        return int.to_bytes(self.id, 1, 'little') + self.data
    
    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        self.id = id
        self.data = data
        self.index = Event._count
        Event._count += 1

class VariableSizedEvent(Event):
    """Implements Event.size and Event.to_raw() for TextEvent and DataEvent"""
    
    @property
    def size(self) -> int:
        if self.data:
            return 1 + len(buflen_to_varint(self.data)) + len(self.data)
        return 2

    def to_raw(self) -> bytes:
        id = int.to_bytes(self.id, 1, 'little')
        length = buflen_to_varint(self.data) if self.data else b'\x00'
        data = self.data
        return id + length + data if self.data else id + length
