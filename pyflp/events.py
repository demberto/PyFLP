# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
    Sized,
    SupportsBytes,
    Tuple,
    TypeVar,
    Union,
)
from warnings import warn

from colour import Color
from bytesioex import (
    Bool,
    Byte,
    BytesIOEx,
    Float,
    Int,
    SByte,
    Short,
    UInt,
    ULong,
    UShort,
)
from colour import Color

__all__ = [
    "AsciiEvent",
    "BoolEvent",
    "BYTE",
    "ColorEvent",
    "DATA",
    "DataArrayEvent",
    "DataEventBase",
    "DWORD",
    "Error",
    "EventType",
    "F32Event",
    "FixedSizeEventBase",
    "I8Event",
    "I16Event",
    "I32Event",
    "NEW_TEXT_IDS",
    "PluginEvent",
    "StrEventBase",
    "StructEventBase",
    "TEXT",
    "U8Event",
    "U16Event",
    "U16TupleEvent",
    "U32Event",
    "U64VariableEvent",
    "UnicodeEvent",
    "UnknownDataEvent",
    "WORD",
]

BYTE = 0
WORD = 64
DWORD = 128
TEXT = 192
DATA = 208
NEW_TEXT_IDS = (
    TEXT + 49,  # Arrangement.EventID.Name
    TEXT + 39,  # FilterChannel.EventID.Name
    TEXT + 47,  # Track.EventID.Name
)

_T = TypeVar("_T")


class Error(Exception):
    """Base class for PyFLP exceptions."""


class EventIDOutOfRangeError(Error, ValueError):
    def __init__(self, id, min_i, max_e):
        super().__init__(f"Expected ID in {min_i}-{max_e - 1}; got {id} instead")


class InvalidEventChunkSizeError(Error, TypeError):
    def __init__(self, expected, got):
        super().__init__(f"Expected a bytes object of length {expected}; got {got}")


class UnexpectedTypeError(Error, TypeError):
    def __init__(self, expected, got):
        super().__init__(f"Expected a {expected} object; got a {got} object instead")


class EventBase(ABC, Generic[_T], Sized, SupportsBytes):
    """Abstract base class representing an event."""

    def __init__(self, id: int, data: bytes) -> None:
        self.id = id
        self._raw = data

    def __eq__(self, o: "EventBase") -> bool:
        return self.id == o.id and self._raw == o._raw

    def __ne__(self, o: "EventBase") -> bool:
        return self.id != o.id or self._raw != o._raw

    @abstractmethod
    def __bytes__(self) -> bytes:
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Raw event size in bytes."""

    @property
    def value(self) -> _T:
        """Deserialized event-type specific value."""
        return self._raw

    @value.setter
    def value(self, value: _T) -> None:
        """Converts Python types into bytes/bytes objects and stores it."""
        self._raw = value


class FixedSizeEventBase(EventBase[_T], ABC):
    def __bytes__(self) -> bytes:
        return Byte.pack(self.id)[0] + self._raw

    def __repr__(self) -> str:
        rid = iid = int(self.id)
        if isinstance(self.id, IntEnum):
            rid = f"{self.id!r}, {iid!r}"
        return f"<{type(self).__name__!r} id={rid!r}, value={self.value}>"


class ByteEventBase(FixedSizeEventBase[_T], ABC):
    """Represents a byte-sized event."""

    def __init__(self, id: int, data) -> None:
        """
        Args:
            id (int): An event ID from **0** to **63**.
            data (bytes): A 1 byte sized `bytes` object.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 0-63.
            InvalidEventChunkSizeError: When size of `data` is not 1.
        """
        if id not in range(BYTE, WORD):
            raise EventIDOutOfRangeError(id, BYTE, WORD)

        if len(data) != 1:
            raise InvalidEventChunkSizeError(1, len(data))

        super().__init__(id, data)

    def __len__(self) -> int:
        return 2


class BoolEvent(ByteEventBase[bool]):
    @property
    def value(self) -> bool:
        return Bool.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[bool]) -> None:
        if value is not None:
            self._raw = Bool.pack(value)


class I8Event(ByteEventBase[int]):
    @property
    def value(self) -> int:
        return SByte.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = SByte.pack(value)


class U8Event(ByteEventBase[int]):
    @property
    def value(self) -> int:
        return Byte.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = Byte.pack(value)


class WordEventBase(FixedSizeEventBase[_T], ABC):
    """Represents a 2 byte event."""

    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID from **64** to **127**.
            data (bytes): A `bytes` object of size 2.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 64-127.
            InvalidEventChunkSizeError: When size of `data` is not 2.
        """
        if id not in range(WORD, DWORD):
            raise EventIDOutOfRangeError(id, WORD, DWORD)

        if len(data) != 2:
            raise InvalidEventChunkSizeError(2, len(data))

        super().__init__(id, data)

    def __len__(self) -> int:
        return 3


class I16Event(WordEventBase[int]):
    @property
    def value(self) -> int:
        return Short.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = Short.pack(value)


class U16Event(WordEventBase[int]):
    @property
    def value(self) -> int:
        return UShort.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = UShort.pack(value)


class DWordEventBase(FixedSizeEventBase[_T], ABC):
    """Represents a 4 byte event."""

    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID from **128** to **191**.
            data (bytes): A `bytes` object of size 4.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 128-191.
            InvalidEventChunkSizeError: When size of `data` is not 4.
        """
        if id not in range(DWORD, TEXT):
            raise EventIDOutOfRangeError(id, DWORD, TEXT)

        if len(data) != 4:
            raise InvalidEventChunkSizeError(4, len(data))

        super().__init__(id, data)

    def __len__(self) -> int:
        return 5


class F32Event(DWordEventBase[float]):
    @property
    def value(self) -> float:
        return Float.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[float]) -> None:
        if value is not None:
            self._raw = Float.pack(value)


class I32Event(DWordEventBase[int]):
    @property
    def value(self) -> int:
        return Int.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = Int.pack(value)


class U32Event(DWordEventBase[int]):
    @property
    def value(self) -> int:
        return UInt.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = UInt.pack(value)


class U16TupleEvent(DWordEventBase[Tuple[int, int]]):
    @property
    def value(self) -> Tuple[int, int]:
        return UInt.unpack(self._raw)

    @value.setter
    def value(self, value: Tuple[int, int]) -> None:
        self._raw = UInt.pack(*value)


class ColorEvent(DWordEventBase[Color]):
    """Represents a 4 byte event which stores a color."""

    @property
    def value(self) -> Color:
        r, g, b = (c / 255 for c in self._raw[:3])
        return Color(rgb=(r, g, b))

    @value.setter
    def value(self, value: Color) -> None:
        self._raw = bytes((int(c * 255) for c in value.rgb)) + b"\x00"


class VariableSizedEventBase(EventBase[_T], ABC):
    @staticmethod
    def _to_varint(buffer: bytes) -> bytearray:
        ret = bytearray()
        buflen = len(buffer)
        while True:
            towrite = buflen & 0x7F
            buflen >>= 7
            if buflen > 0:
                towrite |= 0x80
            ret.append(towrite)
            if buflen <= 0:
                break
        return ret

    def __len__(self) -> int:
        if self._raw is not None:
            return 1 + len(self._to_varint(self._raw)) + len(self._raw)
        return 2

    def __bytes__(self) -> bytes:
        id = Byte.pack(self.id)[0]

        if self._raw != b"":
            return id + self._to_varint(self._raw) + self._raw
        return id + b"\x00"


class UnknownDataEvent(VariableSizedEventBase[bytes]):
    pass


class U64VariableEvent(VariableSizedEventBase):
    def __len__(self):
        if self._raw:
            return 9 + len(self._raw)
        return 9


#     @property
#     def data(self, value):
#         self._raw = value.encode("ascii") if isinstance(value, str) else value

#     def __bytes__(self):
#         id = UInt.pack(self.id)
#         length = ULong.pack(len(self._raw))  # 8 bytes for denoting size, IL?
#         return id + length + self._raw if self._raw else id + length


class StrEventBase(VariableSizedEventBase[str], ABC):
    """Represents a variable sized event used for storing strings."""

    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID from **192** to **207** or in `NEW_TEXT_EVENTS`.
            data (bytes): Event data.

        Raises:
            ValueError: When `id` is not in range of 192-207 or in `NEW_TEXT_EVENTS`.
        """
        if id not in {*range(TEXT, DATA), *NEW_TEXT_IDS}:
            raise ValueError(f"Unexpected ID: {id!r}")

        super().__init__(id, data)

    def __repr__(self):
        return f"<{type(self).__name__} id={self.id!r}, string={self.value!r}>"


class AsciiEvent(StrEventBase):
    @property
    def value(self) -> str:
        return self._raw.decode("ascii").rstrip("\0")

    @value.setter
    def value(self, value: Optional[str]) -> None:
        if value is not None:
            self._raw = value.encode("ascii") + b"\0"


class UnicodeEvent(StrEventBase):
    @property
    def value(self) -> str:
        return self._raw.decode("utf-16-le").rstrip("\0")

    @value.setter
    def value(self, value: Optional[str]) -> None:
        if value is not None:
            self._raw = value.encode("utf-16-le") + b"\0\0"


class DataEventBase(VariableSizedEventBase[bytes], ABC):
    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID in from **208** to **255**.
            data (bytes): Event data.

        Raises:
            ValueError: When `id` is not in the range of 208-255.
        """
        if id < DATA:
            raise EventIDOutOfRangeError(id, DATA, 255)

        self.stream_len = len(data)
        self.stream = BytesIOEx(data)
        super().__init__(id, data)

    def __bytes__(self) -> bytes:
        self._raw = self.stream.getvalue()
        return super().__bytes__()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id!r}, size={self.stream_len}>"


class DataArrayEvent(DataEventBase):
    pass


class UnknownDataEvent(DataEventBase):
    pass


class StructEventBase(DataEventBase, ABC):
    """Represents an event used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event and also FL version sometimes.
    """

    SIZE: int = 0
    PROPS: dict[str, Union[str, int]] = {}

    def __init__(self, id: int, data: bytes, truncate=True) -> None:
        super().__init__(id, data)
        self.props: Dict[str, Any] = {}
        self._truncate = truncate

        if self.SIZE != 0 and len(data) != self.SIZE:
            warn(f"Expected chunk size {self.SIZE} for {id}; got {len(data)}")

        for name, type_or_size in self.PROPS.items():
            if isinstance(type_or_size, str):
                readfunc = getattr(self.stream, "read_" + type_or_size)
                self.props[name] = readfunc()
            else:
                self.props[name] = self.stream.read(type_or_size)

    def __bytes__(self) -> bytes:
        self.stream.seek(0)
        if self._truncate:
            self.stream.truncate(self.stream_len)  # Prevent accidental oversizing

        for name, type_or_size in self.PROPS.items():
            value = self.props[name]
            if isinstance(type_or_size, str) and value is not None:
                writefunc = getattr(self.stream, "write_" + type_or_size)
                writefunc(value)
            else:
                self.stream.write(value)
        return super().__bytes__()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id!r}, size={self.stream_len}, props={self.props!r}>"  # noqa


class PluginEvent(StructEventBase):
    def __init__(self, data: bytes, truncate=True) -> None:
        super().__init__(DATA + 5, data, truncate)


EventType = TypeVar("EventType", bound=EventBase)
