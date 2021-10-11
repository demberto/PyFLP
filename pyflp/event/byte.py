import enum
from typing import Union

from pyflp.event.event import Event
from pyflp.utils import WORD

__all__ = ["ByteEvent"]


class ByteEvent(Event):
    """Represents a byte-sized event."""

    @property
    def size(self) -> int:
        return 2

    def dump(self, new_data: Union[bytes, int, bool]):
        """Dumps a single byte of data; either a bool, int or a bytes object to event data.

        Args:
            new_data (Union[bytes, int, bool]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_data` is a bytes object and its size isn't equal to 1.
            OverflowError: When an integer is too big to be accumulated in 1 byte.
            TypeError: When `new_data` isn't a bool, int or a bytes object.
        """

        if isinstance(new_data, bytes):
            if len(new_data) != 1:
                raise ValueError(
                    f"Expected a bytes object of 1 byte length; got {new_data}"  # type: ignore
                )
            self.data = new_data
        elif isinstance(new_data, int):
            if new_data != abs(new_data):
                if new_data not in range(-128, 128):
                    raise OverflowError(
                        f"Expected a value of -128 to 127; got {new_data}"
                    )
            else:
                if new_data > 255:
                    raise OverflowError(f"Expected a value of 0 to 255; got {new_data}")
            self.data = new_data.to_bytes(1, "little")
        elif isinstance(new_data, bool):
            data = 1 if new_data else 0
            self.data = data.to_bytes(1, "little")
        else:
            raise TypeError(
                f"Expected a bytes, bool or an int object; got {type(new_data)}"
            )

    def to_uint8(self) -> int:
        return int.from_bytes(self.data, "little")

    def to_int8(self) -> int:
        return int.from_bytes(self.data, "little", signed=True)

    def to_bool(self) -> bool:
        return self.to_int8() != 0

    def __repr__(self) -> str:
        return f"{super().__repr__()}, Byte: {self.to_uint8()}"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if not id < WORD:
            raise ValueError(f"Exepcted 0-63; got {id}")
        if len(data) != 1:
            raise TypeError(
                f"Expected a data of 1 byte; got a data of size {len(data)} instead"
            )
        super().__init__(id, data)
