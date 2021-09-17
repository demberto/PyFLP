import enum
from typing import Union

from pyflp.event.event import Event
from pyflp.utils import WORD, DWORD

__all__ = ['WordEvent']

class WordEvent(Event):
    """Represents a 2 byte event.

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