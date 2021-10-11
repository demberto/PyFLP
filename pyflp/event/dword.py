import enum
from typing import Union

from pyflp.event.event import Event
from pyflp.utils import DWORD, TEXT

__all__ = ["DWordEvent"]


class DWordEvent(Event):
    """Represents a 4 byte event."""

    @property
    def size(self) -> int:
        return 5

    def dump(self, new_dword: Union[bytes, int]):
        """Dumps 4 bytes of data; either an int or a bytes object to event data.

        Args:
            new_dword (Union[bytes, int]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_dword` is a bytes object and its size isn't equal to 4.
            OverflowError: When an integer is too big to be accumulated in 4 bytes.
            TypeError: When `new_dword` isn't an int or a bytes object.
        """

        if isinstance(new_dword, bytes):
            if len(new_dword) != 4:
                raise ValueError(
                    f"Expected a bytes object of 4 bytes length; got {new_dword}"  # type: ignore
                )
            self.data = new_dword
        elif isinstance(new_dword, int):
            if new_dword != abs(new_dword):
                if new_dword not in range(-2_147_483_648, 2_147_483_648):
                    raise OverflowError(
                        f"Expected a value of -2,147,483,648 to 2,147,483,647; got {new_dword}"
                    )
            else:
                if new_dword > 4_294_967_295:
                    raise OverflowError(
                        f"Expected a value of 0 to 4,294,967,295; got {new_dword}"
                    )
            self.data = new_dword.to_bytes(4, "little")
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(new_dword)}")

    def to_uint32(self) -> int:
        """Deserializes `self.data` as a 32-bit unsigned integer as an `int`."""

        return int.from_bytes(self.data, "little")

    def to_int32(self) -> int:
        """Deserializes `self.data` as a 32-bit signed integer as an `int`."""

        return int.from_bytes(self.data, "little", signed=True)

    def __repr__(self) -> str:
        return f"{super().__repr__()}, DWord: {self.to_uint32()}"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id not in range(DWORD, TEXT):
            raise ValueError(f"Exepcted 128-191; got {id}")
        if len(data) != 4:
            raise TypeError(
                f"Expected a data of 4 bytes; got a data of size {len(data)} instead"
            )
        super().__init__(id, data)
