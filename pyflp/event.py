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

class ByteEvent(Event):
    """Represents a byte-sized event
 
    Raises:
        ValueError & TypeError
    """
    
    @property
    def size(self) -> int:
        return 2
    
    def __repr__(self) -> str:
        return f"ByteEvent ID: {self.id} Data: {self.to_uint8()} (Index: {self.index})"

    def dump(self, new_data: Union[bytes, int, bool]):
        if isinstance(new_data, bytes):
            if len(new_data) != 1:
                raise ValueError(f"Expected a bytes object of 1 byte length; got {new_data}")
            self.data = new_data
        elif isinstance(new_data, int):
            if new_data != abs(new_data):
                if new_data not in range(-128, 128):
                    raise ValueError(f"Expected a value of -128 to 127; got {new_data}")
            else:
                if new_data > 255:
                    raise ValueError(f"Expected a value of 0 to 255; got {new_data}")
            self.data = new_data.to_bytes(1, 'little')
        elif isinstance(new_data, bool):
            data = 1 if new_data else 0
            self.data = data.to_bytes(1, 'little')
        else:
            raise TypeError(f"Expected a bytes, bool or an int object; got {type(new_data)}")
    
    def to_uint8(self) -> int:
        return int.from_bytes(self.data, 'little')
    
    def to_int8(self) -> int:
        return int.from_bytes(self.data, 'little', signed=True)
    
    def to_bool(self) -> bool:
        return self.to_int8() != 0
    
    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if not id < WORD:
            raise ValueError(f"Exepcted 0-63; got {id}")
        super().__init__(id, data)

class WordEvent(Event):
    """Represents a 2 byte event
 
    Raises:
        ValueError & TypeError
    """
    
    @property
    def size(self) -> int:
        return 3
    
    def __repr__(self) -> str:
        return f"WordEvent ID: {self.id} Data: {self.to_uint16()} (Index: {self.index})"

    def dump(self, new_data: Union[bytes, int]):
        if isinstance(new_data, bytes):
            if len(new_data) != 2:
                raise ValueError(f"Expected a bytes object of 2 bytes length; got {new_data}")
            self.data = new_data
        elif isinstance(new_data, int):
            if new_data != abs(new_data):
                if new_data not in range(-32768, 32768):
                    raise ValueError(f"Expected a value -32768 to 32767; got {new_data}")
            else:
                if new_data > 65535:
                    raise ValueError(f"Expected a value of 0 to 65535; got {new_data}")
            self.data = new_data.to_bytes(2, 'little')
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(new_data)}")

    def to_uint16(self) -> int:
        return int.from_bytes(self.data, 'little')
    
    def to_int16(self) -> int:
        return int.from_bytes(self.data, 'little', signed=True)
    
    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id not in range(WORD, DWORD):
            raise ValueError(f"Exepcted 64-127; got {id}")
        super().__init__(id, data)

class DWordEvent(Event):
    """Represents a 4 byte event
 
    Raises:
        ValueError & TypeError
    """
    
    @property
    def size(self) -> int:
        return 5
    
    def __repr__(self) -> str:
        return f"DWordEvent ID: {self.id} Data: {self.to_uint32()} (Index: {self.index})"

    def dump(self, new_data: Union[bytes, int]):
        if isinstance(new_data, bytes):
            if len(new_data) != 4:
                raise ValueError(f"Expected a bytes object of 4 bytes length; got {new_data}")
            self.data = new_data
        elif isinstance(new_data, int):
            if new_data != abs(new_data):
                if new_data not in range(-2_147_483_648, 2_147_483_648):
                    raise ValueError(f"Expected a value of -2,147,483,648 to 2,147,483,647; got {new_data}")
            else:
                if new_data > 4_294_967_295:
                    raise ValueError(f"Expected a value of 0 to 4,294,967,295; got {new_data}")
            self.data = new_data.to_bytes(4, 'little')
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(new_data)}")

    def to_uint32(self) -> int:
        return int.from_bytes(self.data, 'little')
    
    def to_int32(self) -> int:
        return int.from_bytes(self.data, 'little', signed=True)

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id not in range(DWORD, TEXT):
            raise ValueError(f"Exepcted 128-191; got {id}")
        super().__init__(id, data)

class _VariableSizedEvent(Event):
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

class TextEvent(_VariableSizedEvent):
    """Represents a variable sized event used for storing strings
 
	Raises:
		TypeError
	"""
 
    # ProjectParser will change this.
    uses_unicode = True
    
    def __repr__(self) -> str:
        return f"TextEvent ID: {self.id} Data: {self.to_str()} (Index: {self.index})"
    
    def dump(self, new_str: str):
        if not isinstance(new_str, str):
            raise TypeError(f"Expected an str object; got {type(new_str)}")
        # Version event (199) is always ASCII
        if TextEvent.uses_unicode and self.id != 199:
            self.data = new_str.encode('utf-16', errors='ignore') + b'\0\0'
        else:
            self.data = new_str.encode('ascii', errors='ignore') + b'\0'
    
    def to_str(self) -> str:
        if TextEvent.uses_unicode and self.id != 199:
            return self.data.decode('utf-16', errors='ignore').strip('\0')
        return self.data.decode('ascii', errors='ignore').strip('\0')

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id not in range(TEXT, DATA) and id not in DATA_TEXT_EVENTS:
            raise ValueError(f"Unexpected ID: {id}")
        super().__init__(id, data)

class DataEvent(_VariableSizedEvent):
    """Represents a variable sized event used for storing data,
    consists of a collection of POD types like int, bool, float.
    Its size is determined by the event and also FL version sometimes.
    The task of parsing is completely handled by one of the FLObject subclasses,
    hence no conversion method is provided.
 
	Raises:
		TypeError
	"""
    
    def __repr__(self) -> str:
        return f"DataEvent ID: {self.id} Data: {self.data} (Index: {self.index})"
    
    def dump(self, new_bytes: bytes):
        """Use this method over directly setting self.data for type-safety."""
        if not isinstance(new_bytes, bytes):
            raise TypeError(f"Expected a bytes object; got a {type(new_bytes)} object")
        self.data = new_bytes

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id < DATA:
            raise ValueError(f"Expected an event ID from 209 to 255; got {id}")
        super().__init__(id, data)
