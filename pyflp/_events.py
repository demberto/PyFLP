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
import sys
import warnings
from typing import Any, ClassVar, Generic, Iterator, Tuple, TypeVar, Union

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

import colour
import construct as c
import construct_typed as ct

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
    TEXT + 49,  # ArrangementID.Name
    TEXT + 39,  # DisplayGroupID.Name
    TEXT + 47,  # TrackID.Name
)

T = TypeVar("T")
ET = TypeVar("ET", bound=Union[ct.EnumBase, enum.IntFlag])
T_co = TypeVar("T_co", covariant=True)
FourByteBool: c.ExprAdapter[int, int, bool, int] = c.ExprAdapter(
    c.Int32ul, lambda obj_, *_: bool(obj_), lambda obj_, *_: int(obj_)  # type: ignore
)


class StdEnum(ct.Adapter[int, int, ET, ET]):
    def _encode(self, obj: ET, *_: Any):  # pylint: disable=no-self-use
        return obj.value

    def _decode(self, obj: int, *_: Any) -> ET:
        return self.__orig_class__.__args__[0](obj)  # type: ignore


# Resolves TypeError: unsupported operand type(s) for 'in': 'int' and 'EnumMeta'
class EventEnumMeta(enum.EnumMeta):
    def __contains__(self, id: object):
        if not isinstance(id, int):
            return NotImplemented

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


class EventBase(Generic[T]):  # pylint: disable=eq-without-hash
    """Generic ABC representing an event."""

    def __init__(self, id: int, data: bytes):
        self.id: Final = id
        self._data: bytes = data

    def __eq__(self, o: object):
        if not isinstance(o, EventBase):
            raise TypeError(f"Cannot find equality of an {type(o)} and {type(self)!r}")
        return self.id == o.id and self._data == o._data

    def __ne__(self, o: object):
        if not isinstance(o, EventBase):
            raise TypeError(f"Cannot find inequality of a {type(o)} and {type(self)!r}")
        return self.id != o.id or self._data != o._data

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        ...

    @property
    @abc.abstractmethod
    def size(self) -> int:
        """Serialised event size (in bytes)."""  # noqa: D402

    @property
    def value(self) -> T:
        """Deserialized event-type specific value."""
        ...  # pylint: disable=unnecessary-ellipsis

    @value.setter
    def value(self, value: T):
        """Converts Python types into bytes/bytes objects and stores it."""


AnyEvent = EventBase[Any]


class PODEventBase(EventBase[T]):
    """Base class for events whose size is predetermined (POD types)."""

    ID_RANGE: ClassVar[tuple[int, int]]
    CODEC: c.Construct[Any, Any]

    def __init__(self, id: int, data: bytes):
        if id not in range(*self.ID_RANGE):
            raise EventIDOutOfRange(id, *self.ID_RANGE)

        if len(data) != self.CODEC.sizeof():
            raise InvalidEventChunkSize(self.CODEC.sizeof(), len(data))

        super().__init__(id, data)

    def __bytes__(self):
        return c.Byte.build(self.id) + self._data

    def __repr__(self):
        return f"<{type(self).__name__!r} id={self.id!r}, value={self.value}>"

    @property
    def size(self):
        return 1 + self.CODEC.sizeof()

    @property
    def value(self) -> T:
        return self.CODEC.parse(self._data)

    @value.setter
    def value(self, value: T):
        self._data = self.CODEC.build(value)


class ByteEventBase(PODEventBase[T]):
    """Base class of events used for storing 1 byte data."""

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

    CODEC = c.Flag


class I8Event(ByteEventBase[int]):
    """An event used for storing a 1 byte signed integer."""

    CODEC = c.Int8sl


class U8Event(ByteEventBase[int]):
    """An event used for storing a 1 byte unsigned integer."""

    CODEC = c.Int8ul


class WordEventBase(PODEventBase[T], abc.ABC):
    """Base class of events used for storing 2 byte data."""

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

    CODEC = c.Int16sl


class U16Event(WordEventBase[int]):
    """An event used for storing a 2 byte unsigned integer."""

    CODEC = c.Int16ul


class DWordEventBase(PODEventBase[T], abc.ABC):
    """Base class of events used for storing 4 byte data."""

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

    CODEC = c.Float32l


class I32Event(DWordEventBase[int]):
    """An event used for storing a 4 byte signed integer."""

    CODEC = c.Int32sl


class U32Event(DWordEventBase[int]):
    """An event used for storing a 4 byte unsigned integer."""

    CODEC = c.Int32ul


class U16TupleEvent(DWordEventBase[Tuple[int, int]]):
    """An event used for storing a two-tuple of 2 byte unsigned integers."""

    CODEC: c.ExprAdapter[
        c.ListContainer[int], c.ListContainer[int], tuple[int, int], list[int]
    ] = c.ExprAdapter(
        c.Int16ul[2],
        lambda obj_, *_: tuple(obj_),  # type: ignore
        lambda obj_, *_: list(obj_),  # type: ignore
    )


class ColorEvent(DWordEventBase[colour.Color]):
    """A 4 byte event which stores a color."""

    CODEC: c.ExprAdapter[bytes, bytes, colour.Color, colour.Color] = c.ExprAdapter(
        c.Bytes(4),
        lambda obj, *_: ColorEvent.decode(obj),  # type: ignore
        lambda obj, *_: ColorEvent.encode(obj),  # type: ignore
    )

    @staticmethod
    def decode(buf: bytes | bytes):
        r, g, b = (c / 255 for c in buf[:3])
        return colour.Color(rgb=(r, g, b))

    @staticmethod
    def encode(color: colour.Color):
        return bytes(int(c * 255) for c in color.get_rgb()) + b"\x00"


class VarintEventBase(EventBase[T]):
    @staticmethod
    def _varint_len(buflen: int):
        ret = bytearray()
        while True:
            towrite = buflen & 0x7F
            buflen >>= 7
            towrite |= 0x80
            ret.append(towrite)
            if buflen <= 0:
                break
        return len(ret)

    @property
    def size(self):
        if self._data:
            return 1 + self._varint_len(len(self._data)) + len(self._data)
        return 2

    def __bytes__(self):
        id = c.Byte.build(self.id)

        if self._data:
            return id + c.VarInt.build(len(self._data)) + self._data
        return id + b"\x00"


class StrEventBase(VarintEventBase[str]):
    """Base class of events used for storing strings."""

    def __init__(self, id: int, data: bytes):
        """
        Args:
            id (int): **192** to **207** or in :attr:`NEW_TEXT_IDS`.
            data (bytes): ASCII or UTF16 encoded string data.

        Raises:
            ValueError: When `id` is not in 192-207 or in :attr:`NEW_TEXT_IDS`.
        """
        if id not in {*range(TEXT, DATA), *NEW_TEXT_IDS}:
            raise ValueError(f"Unexpected ID{id!r}")

        super().__init__(id, data)

    def __repr__(self):
        return f"<{type(self).__name__} id={self.id!r}, string={self.value!r}>"


class AsciiEvent(StrEventBase):
    @property
    def value(self):
        return self._data.decode("ascii").rstrip("\0")

    @value.setter
    def value(self, value: str):
        if value is not None:
            self._data = value.encode("ascii") + b"\0"


class UnicodeEvent(StrEventBase):
    @property
    def value(self):
        return self._data.decode("utf-16-le").rstrip("\0")

    @value.setter
    def value(self, value: str):
        if value is not None:
            self._data = value.encode("utf-16-le") + b"\0\0"


class DataEventBase(VarintEventBase[bytes]):
    def __init__(self, id: int, data: bytes):
        """
        Args:
            id (int): **208** to **255**.
            data (bytes): Event data (no size limit).

        Raises:
            EventIDOutOfRange: `id` is not in the range of 208-255.
        """
        if id < DATA:
            raise EventIDOutOfRange(id, DATA, 256)

        super().__init__(id, data)

    def __repr__(self):
        return f"<{type(self).__name__} id={self.id!r}, size={len(self._data)}>"


class StructEventBase(DataEventBase):
    """Base class for events used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event as well as FL version.
    """

    STRUCT: ClassVar[c.Construct[c.Container[Any], Any]]

    def __init__(self, id: int, data: bytes):
        super().__init__(id, data)
        self._struct = self.STRUCT.parse(data)

    def __bytes__(self):
        new_data = self.STRUCT.build(self._struct)
        if len(new_data) != len(self._data):
            warnings.warn(
                "{} built a stream of incorrect size {}; expected {}.".format(
                    type(self.STRUCT).__name__, len(new_data), len(self._data)
                ),
                BytesWarning,
                stacklevel=0,
            )
        # Effectively, overwrite new data over old one to ensure the stream
        # size remains unmodified
        self._data = new_data + self._data[len(new_data) :]
        return super().__bytes__()

    def __contains__(self, prop: str):
        return prop in self._struct

    def __getitem__(self, key: str):
        return self._struct[key]

    def __setitem__(self, key: str, value: Any):
        if key not in self or self[key] is None:
            raise PropertyCannotBeSet
        self._struct[key] = value

    def __repr__(self):
        return f"{type(self).__name__} (id={self.id}, size={len(self._data)})"


class ListEventBase(DataEventBase):
    """Base class for events storing an array of structured data."""

    STRUCT: ClassVar[c.Construct[c.Container[Any], Any]]

    def __init__(self, id: int, data: bytes):
        super().__init__(id, data)
        self.unparsed = False

        if len(data) % self.STRUCT.sizeof():  # pragma: no cover
            self.unparsed = True
            warnings.warn(
                f"Cannot parse event {id} as event "
                "size is not a multiple of struct size"
            )

    def __len__(self):
        if self.unparsed:  # pragma: no cover
            raise ListEventNotParsed

        return len(self._data) // self.STRUCT.sizeof()

    def __getitem__(self, index: int):
        if self.unparsed:  # pragma: no cover
            raise ListEventNotParsed

        if index > len(self):
            raise IndexError(index)

        start = self.STRUCT.sizeof() * index
        count = self.STRUCT.sizeof()
        return self.STRUCT.parse(self._data[start : start + count])

    def __setitem__(self, index: int, item: c.Container[Any]):
        if self.unparsed:
            raise ListEventNotParsed

        if index > len(self):
            raise IndexError(index)

        start = self.STRUCT.sizeof() * index
        count = self.STRUCT.sizeof()
        self._data = (
            self._data[:start] + self.STRUCT.build(item) + self._data[start + count :]
        )

    def __iter__(self) -> Iterator[c.Container[Any]]:
        for i in range(len(self)):
            yield self[i]

    def __repr__(self):
        return "{} (id={}, size={}, {} items)".format(
            type(self).__name__, self.id, len(self._data), len(self)
        )


class UnknownDataEvent(DataEventBase):
    """Used for events whose structure is unknown as of yet."""

    @property
    def value(self):
        return self._data

    @value.setter
    def value(self, value: bytes):
        self._data = value
