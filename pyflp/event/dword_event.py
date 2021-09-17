import enum
from typing import Union

from pyflp.event.event import Event
from pyflp.utils import DWORD, TEXT

__all__ = ['DWordEvent']

class DWordEvent(Event):
    """Represents a 4 byte event.

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