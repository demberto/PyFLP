import enum
from typing import Union

from pyflp.event.event import Event
from pyflp.utils import WORD, DWORD

__all__ = ["WordEvent"]


class WordEvent(Event):
    """Represents a 2 byte event."""

    @property
    def size(self) -> int:
        return 3

    def dump(self, new_word: Union[bytes, int]):
        """Dumps 2 bytes of data; either an int or a bytes object to event data.

        Args:
            new_word (Union[bytes, int]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_word` is a bytes object and its size isn't equal to 2.
            OverflowError: When an integer is too big to be accumulated in 2 bytes.
            TypeError: When `new_word` isn't an int or a bytes object.
        """

        if isinstance(new_word, bytes):
            if len(new_word) != 2:
                raise ValueError(
                    f"Expected a bytes object of 2 bytes length; got {new_word}"  # type: ignore
                )
            self.data = new_word
        elif isinstance(new_word, int):
            if new_word != abs(new_word):
                if new_word not in range(-32768, 32768):
                    raise OverflowError(
                        f"Expected a value -32768 to 32767; got {new_word}"
                    )
            else:
                if new_word > 65535:
                    raise OverflowError(
                        f"Expected a value of 0 to 65535; got {new_word}"
                    )
            self.data = new_word.to_bytes(2, "little")
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(new_word)}")

    def to_uint16(self) -> int:
        return int.from_bytes(self.data, "little")

    def to_int16(self) -> int:
        return int.from_bytes(self.data, "little", signed=True)

    def __repr__(self) -> str:
        return f"{super().__repr__()}, Word: {self.to_uint16()}"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id not in range(WORD, DWORD):
            raise ValueError(f"Exepcted 64-127; got {id}")
        super().__init__(id, data)
