# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""Contains implementations for various types of event data representations.

These types serve as the backbone for model creation and simplify marshalling
and unmarshalling.
"""

from __future__ import annotations

import abc
import enum
import struct
import sys
import warnings
from collections.abc import Hashable, Sized
from typing import Any, ClassVar, Dict, Generic, Tuple, TypeVar, Union, cast

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

if sys.version_info >= (3, 9):
    from collections.abc import Iterable, Iterator
else:
    from typing import Iterable, Iterator

import colour
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

from .exceptions import (
    EventIDOutOfRange,
    InvalidEventChunkSize,
    ListEventNotParsed,
    PropertyCannotBeSet,
)

BYTE: Final = 0
WORD: Final = 64
DWORD: Final = 128
TEXT: Final = 192
DATA: Final = 208
NEW_TEXT_IDS: Final = (
    TEXT + 49,  # Arrangement.EventID.Name
    TEXT + 39,  # FilterChannel.EventID.Name
    TEXT + 47,  # Track.EventID.Name
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
UShortTuple = struct.Struct("HH")


# ! MRO erros when deriving from SupportsBytes on Python 3.7
class EventBase(Generic[T], Sized, Hashable):
    """Abstract base class representing an event."""

    def __init__(self, id: int, data: bytes):
        self.id: Final = id
        self._raw = data

    def __eq__(self, o: object):
        if not isinstance(o, EventBase):
            raise TypeError(f"Cannot find equality of an {type(o)} and {type(self)!r}")
        return self.id == o.id and self._raw == o._raw

    def __ne__(self, o: object):
        if not isinstance(o, EventBase):
            raise TypeError(f"Cannot find inequality of a {type(o)} and {type(self)!r}")
        return self.id != o.id or self._raw != o._raw

    def __hash__(self):
        return hash(bytes(self))

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        ...

    @abc.abstractmethod
    def __len__(self) -> int:
        """Serialised event size (in bytes)."""

    @property
    def value(self) -> T:
        """Deserialized event-type specific value."""
        ...  # pylint: disable=unnecessary-ellipsis

    @value.setter
    def value(self, value: T):
        """Converts Python types into bytes/bytes objects and stores it."""


AnyEvent = EventBase[Any]


class PODEventBase(EventBase[T], abc.ABC):
    """Base class for events whose size is predetermined (POD types)."""

    TYPE_SIZE: ClassVar[int]
    ID_RANGE: ClassVar[tuple[int, int]]

    def __init__(self, id: int, data: bytes):
        if id not in range(*self.ID_RANGE):
            raise EventIDOutOfRange(id, *self.ID_RANGE)

        if len(data) != self.TYPE_SIZE:
            raise InvalidEventChunkSize(self.TYPE_SIZE, len(data))

        super().__init__(id, data)

    def __bytes__(self):
        return Byte.pack(self.id) + self._raw

    def __repr__(self):
        rid = iid = int(self.id)
        if isinstance(self.id, enum.IntEnum):
            rid = f"{self.id!r}, {iid!r}"
        return f"<{type(self).__name__!r} id={rid!r}, value={self.value}>"

    def __len__(self):
        return 1 + self.TYPE_SIZE


class ByteEventBase(PODEventBase[T], abc.ABC):
    """Base class of events used for storing 1 byte data."""

    TYPE_SIZE = 1
    ID_RANGE = (BYTE, WORD)

    def __init__(self, id: int, data: bytes):
        """
        Args:
            id (int): **0** to **63**.
            data (bytes): Event data of size 1.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 0-63.
            InvalidEventChunkSizeError: When size of `data` is not 1.
        """
        super().__init__(id, data)


class BoolEvent(ByteEventBase[bool]):
    """An event used for storing a boolean."""

    @property
    def value(self) -> bool:
        return Bool.unpack(self._raw)[0]

    @value.setter
    def value(self, value: bool):
        if value is not None:
            self._raw = Bool.pack(value)


class I8Event(ByteEventBase[int]):
    """An event used for storing a 1 byte signed integer."""

    @property
    def value(self) -> int:
        return SByte.unpack(self._raw)[0]

    @value.setter
    def value(self, value: int):
        if value is not None:
            self._raw = SByte.pack(value)


class U8Event(ByteEventBase[int]):
    """An event used for storing a 1 byte unsigned integer."""

    @property
    def value(self) -> int:
        return Byte.unpack(self._raw)[0]

    @value.setter
    def value(self, value: int):
        if value is not None:
            self._raw = Byte.pack(value)


class WordEventBase(PODEventBase[T], abc.ABC):
    """Base class of events used for storing 2 byte data."""

    TYPE_SIZE = 2
    ID_RANGE = (WORD, DWORD)

    def __init__(self, id: int, data: bytes):
        """
        Args:
            id (int): **64** to **127**.
            data (bytes): Event data of size 2.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 64-127.
            InvalidEventChunkSizeError: When size of `data` is not 2.
        """
        super().__init__(id, data)


class I16Event(WordEventBase[int]):
    """An event used for storing a 2 byte signed integer."""

    @property
    def value(self) -> int:
        return Short.unpack(self._raw)[0]

    @value.setter
    def value(self, value: int):
        if value is not None:
            self._raw = Short.pack(value)


class U16Event(WordEventBase[int]):
    """An event used for storing a 2 byte unsigned integer."""

    @property
    def value(self) -> int:
        return UShort.unpack(self._raw)[0]

    @value.setter
    def value(self, value: int):
        if value is not None:
            self._raw = UShort.pack(value)


class DWordEventBase(PODEventBase[T], abc.ABC):
    """Base class of events used for storing 4 byte data."""

    TYPE_SIZE = 4
    ID_RANGE = (DWORD, TEXT)

    def __init__(self, id: int, data: bytes):
        """
        Args:
            id (int): **128** to **191**.
            data (bytes): Event data of size 4.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 128-191.
            InvalidEventChunkSizeError: When size of `data` is not 4.
        """
        super().__init__(id, data)


class F32Event(DWordEventBase[float]):
    """An event used for storing 4 byte floats."""

    @property
    def value(self) -> float:
        return Float.unpack(self._raw)[0]

    @value.setter
    def value(self, value: float):
        if value is not None:
            self._raw = Float.pack(value)


class I32Event(DWordEventBase[int]):
    """An event used for storing a 4 byte signed integer."""

    @property
    def value(self) -> int:
        return Int.unpack(self._raw)[0]

    @value.setter
    def value(self, value: int):
        if value is not None:
            self._raw = Int.pack(value)


class U32Event(DWordEventBase[int]):
    """An event used for storing a 4 byte unsigned integer."""

    @property
    def value(self):
        return UInt.unpack(self._raw)[0]

    @value.setter
    def value(self, value: int):
        if value is not None:
            self._raw = UInt.pack(value)


class U16TupleEvent(DWordEventBase[Tuple[int, int]]):
    """An event used for storing a two-tuple of 2 byte unsigned integers."""

    @property
    def value(self) -> tuple[int, int]:
        return UShortTuple.unpack(self._raw)

    @value.setter
    def value(self, value: tuple[int, int]):
        self._raw = UShortTuple.pack(*value)


class ColorEvent(DWordEventBase[colour.Color]):
    """A 4 byte event which stores a color."""

    @staticmethod
    def decode(buf: bytes):
        r, g, b = (c / 255 for c in buf[:3])
        return colour.Color(rgb=(r, g, b))

    @staticmethod
    def encode(color: colour.Color):
        return bytes(int(c * 255) for c in color.get_rgb()) + b"\x00"

    @property
    def value(self):
        return self.decode(self._raw)

    @value.setter
    def value(self, value: colour.Color):
        self._raw = self.encode(value)


class VarintEventBase(EventBase[T], abc.ABC):
    @staticmethod
    def _to_varint(buffer: bytes):
        ret = bytearray()
        buflen = len(buffer)
        while True:
            towrite = buflen & 0x7F
            buflen >>= 7
            if buflen <= 0:
                break
            towrite |= 0x80
            ret.append(towrite)
        return ret

    def __len__(self):
        if self._raw is not None:
            return 1 + len(self._to_varint(self._raw)) + len(self._raw)
        return 2

    def __bytes__(self):
        id = Byte.pack(self.id)

        if self._raw != b"":
            return id + self._to_varint(self._raw) + self._raw
        return id + b"\x00"


class U64DataEvent(VarintEventBase[Union[bytes, str]]):
    def __init__(self, id: int, data: bytes, isascii: bool = False):
        super().__init__(id, data)
        self._isascii = isascii

    def __len__(self):
        return 9 + len(self._raw)

    def __bytes__(self):
        id = UInt.pack(self.id)
        length = ULong.pack(len(self._raw))  # 8 bytes for denoting size, wth IL?
        return id + length + self._raw if self._raw else id + length

    @property
    def value(self):
        return self._raw.decode("ascii") if self._isascii else self._raw

    @value.setter
    def value(self, value: bytes | str):
        if isinstance(value, str):
            self._raw = value.encode("ascii")
        else:
            self._raw = value


class StrEventBase(VarintEventBase[str], abc.ABC):
    """Base class of events used for storing strings."""

    def __init__(self, id: int, data: bytes):
        """
        Args:
            id (int): **192** to **207** or in `NEW_TEXT_IDS`.
            data (bytes): Event data.

        Raises:
            ValueError: When `id` is not in 192-207 or in `NEW_TEXT_IDS`.
        """
        if id not in {*range(TEXT, DATA), *NEW_TEXT_IDS}:
            raise ValueError(f"Unexpected ID{id!r}")

        super().__init__(id, data)

    def __repr__(self):
        return f"<{type(self).__name__} id={self.id!r}, string={self.value!r}>"


class AsciiEvent(StrEventBase):
    @property
    def value(self):
        return self._raw.decode("ascii").rstrip("\0")

    @value.setter
    def value(self, value: str):
        if value is not None:
            self._raw = value.encode("ascii") + b"\0"


class UnicodeEvent(StrEventBase):
    @property
    def value(self):
        return self._raw.decode("utf-16-le").rstrip("\0")

    @value.setter
    def value(self, value: str):
        if value is not None:
            self._raw = value.encode("utf-16-le") + b"\0\0"


class DataEventBase(VarintEventBase[bytes]):
    def __init__(self, id: int, data: bytes):
        """
        Args:
            id (int)**208** to **255**.
            data (bytes): Event data (no size limit).

        Raises:
            EventIDOutOfRange: `id` is not in the range of 208-255.
        """
        if id < DATA:
            raise EventIDOutOfRange(id, DATA, 256)

        self._stream_len = len(data)
        self._stream = BytesIOEx(data)
        super().__init__(id, data)

    def __bytes__(self):
        self._raw = self._stream.getvalue()
        return super().__bytes__()

    def __repr__(self):
        return f"<{type(self).__name__} id={self.id!r}, size={self._stream_len}>"


class _StructMeta(type):
    """Metaclass for `Struct`."""

    SIZES: Final = {
        "bool": 1,
        "b": 1,
        "B": 1,
        "h": 2,
        "H": 2,
        "f": 4,
        "i": 4,
        "I": 4,
        "d": 8,
    }

    def __new__(cls, name: str, bases: Any, attrs: dict[str, Any]):
        """Populates :attr:`Struct.OFFSETS` and :attr:`Struct.SIZE`."""
        if "PROPS" not in attrs:  # pragma: no cover
            raise AttributeError(f"Class {name} doesn't have a PROPS attribute")

        offset = 0
        offsets = attrs["OFFSETS"] = {}
        for k, type_or_len in cast(Dict[str, Union[str, int]], attrs["PROPS"]).items():
            offsets[k] = offset
            if isinstance(type_or_len, int):
                offset += type_or_len
            else:
                offset += cls.SIZES[type_or_len]
        attrs["SIZE"] = offset
        return type.__new__(cls, name, bases, attrs)


class StructBase(metaclass=_StructMeta):
    OFFSETS: ClassVar[dict[str, int]] = {}
    """A mapping of property names to their offsets in the underlying stream."""

    PROPS: ClassVar[dict[str, str | int]] = {}
    """A mapping of property names to their underlying C types.

    Usually match `struct` format specifiers and used to get the correct read
    and write method attributes from the `BytesIOEx` stream.
    """

    SIZE: ClassVar = 0
    """A supposed size of the underlying structure to be parsed.

    The actual stream size maybe different and totally depends on FL version.
    """

    TRUNCATE: ClassVar = True
    """Whether or not to truncate the stream size to its size at initialisation.

    This ensures that data doesn't get written beyond the bounds of the stream.
    Should be set to False when the structure contains strings or any other
    type of variable data.
    """

    def __init__(self, stream: BytesIOEx):
        self._stream = stream
        self._initial_len = len(stream.getvalue())

    def __repr__(self):
        return "{} {}".format(
            type(self).__name__, [f"{prop}={self[prop]}" for prop in self.PROPS]
        )

    def __bytes__(self):
        return self._stream.getvalue()

    def __len__(self):
        return self._initial_len

    def __contains__(self, key: str):
        return key in self.PROPS

    def __getitem__(self, key: str) -> Any:
        self._stream.seek(self.OFFSETS[key])
        type_or_size = self.PROPS[key]
        if isinstance(type_or_size, int):
            return self._stream.read(type_or_size)
        else:
            return getattr(self._stream, f"read_{type_or_size}")()

    def __setitem__(self, key: str, value: Any):
        self._stream.seek(self.OFFSETS[key])
        type_or_size = self.PROPS[key]
        if isinstance(type_or_size, int):
            self._stream.write(value)
        else:
            getattr(self._stream, f"write_{type_or_size}")(value)

        if len(self._stream.getvalue()) > self._initial_len and self.TRUNCATE:
            raise PropertyCannotBeSet


class StructEventBase(DataEventBase):
    """Base class for events used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event as well as FL version.
    """

    STRUCT: ClassVar[type[StructBase]]

    def __init__(self, id: int, data: bytes):
        super().__init__(id, data)
        self._struct = self.STRUCT(self._stream)
        if self.STRUCT.SIZE < len(data):  # pragma: no cover
            warnings.warn(
                f"Event {id} not parsed entirely; "
                f"parsed {self._stream.tell()}, found {len(data)} bytes",
                RuntimeWarning,
                stacklevel=0,
            )

    def __bytes__(self):
        self._raw = bytes(self._struct)
        return super().__bytes__()

    def __contains__(self, prop: str):
        return prop in self._struct

    def __getitem__(self, key: str):
        return self._struct[key]

    def __setitem__(self, key: str, value: Any):
        self._struct[key] = value

    def __repr__(self):
        return "{} (id={}, size={}, props={})".format(
            type(self).__name__,
            self.id,
            len(self._stream.getvalue()),
            [f"{prop}={self[prop]}" for prop in self.STRUCT.PROPS],
        )


class ListEventBase(DataEventBase, Iterable[StructBase]):
    """Base class for events storing an array of structured data."""

    STRUCT: ClassVar[type[StructBase]]

    def __init__(self, id: int, data: bytes):
        super().__init__(id, data)
        self.unparsed = False

        if len(data) % self.STRUCT.SIZE:  # pragma: no cover
            self.unparsed = True
            warnings.warn(
                f"Cannot parse event {id} as event "
                "size is not a multiple of struct size"
            )

    @property
    def num_items(self):  # * __len__() is already used up
        if self.unparsed:  # pragma: no cover
            raise ListEventNotParsed

        return len(self._stream.getvalue()) // self.STRUCT.SIZE

    def __getitem__(self, index: int):
        if self.unparsed:  # pragma: no cover
            raise ListEventNotParsed

        if index > self.num_items:
            raise IndexError(index)

        self._stream.seek(self.STRUCT.SIZE * index)
        return self.STRUCT(BytesIOEx(self._stream.read(self.STRUCT.SIZE)))

    def __setitem__(self, index: int, item: StructBase):
        if self.unparsed:
            raise ListEventNotParsed

        if index > self.num_items:
            raise IndexError(index)

        self._stream.seek(self.STRUCT.SIZE * index)
        self._stream.write(bytes(item))

    def __iter__(self) -> Iterator[StructBase]:
        for i in range(self.num_items):
            yield self[i]

    def __repr__(self):
        return "{} (id={}, size={}, {} items)".format(
            type(self).__name__, self.id, len(self._stream.getvalue()), self.num_items
        )


class UnknownDataEvent(DataEventBase):
    """Used for events whose structure is unknown as of yet."""

    @property
    def value(self):
        return self._raw

    @value.setter
    def value(self, value: bytes):
        self._raw = value


class EventEnumMeta(enum.EnumMeta):
    def __contains__(self, id: int):
        try:
            self(id)  # type: ignore
        except ValueError:
            return False
        else:
            return True


class EventEnum(int, enum.Enum, metaclass=EventEnumMeta):
    """IDs used by events.

    Event values are stored as a tuple of event ID and its designated type.
    The types are used to serialise/deserialise events by the parser.

    All event names prefixed with an underscore (_) are deprecated w.r.t to
    the latest version of FL Studio, *to the best of my knowledge*.
    """

    def __new__(cls, id: int, type: type[AnyEvent] | None = None):
        obj = int.__new__(cls, id)
        obj._value_ = id
        setattr(obj, "type", type)
        return obj
