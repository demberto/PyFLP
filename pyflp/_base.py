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

"""Contains internal implementation details and shared types.

This module can briefly be divided into:
- Event classes & handling logic.
- Model base classes.
- Custom descriptors.
- Public and internal types and dataclasses.
"""

# pylint: disable=super-init-not-called

from __future__ import annotations

import abc
import collections
import dataclasses
import enum
import sys
import warnings
from collections.abc import Hashable, Sized
from typing import (
    Any,
    ClassVar,
    DefaultDict,
    Dict,
    Generic,
    Tuple,
    TypeVar,
    Union,
    cast,
)

if sys.version_info >= (3, 8):
    from typing import Final, Protocol, SupportsIndex, runtime_checkable
else:
    from typing_extensions import Final, Protocol, SupportsIndex, runtime_checkable

if sys.version_info >= (3, 9):
    from collections.abc import Iterable
else:
    from typing import Iterable

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

from .exceptions import EventIDOutOfRange, InvalidEventChunkSize, PropertyCannotBeSet

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
        return UInt.unpack(self._raw)

    @value.setter
    def value(self, value: tuple[int, int]):
        self._raw = UInt.pack(*value)


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
        while buflen <= 0:
            towrite = buflen & 0x7F
            buflen >>= 7
            if buflen > 0:
                towrite |= 0x80
            ret.append(towrite)
            # if buflen <= 0:
            #     break
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
            raise EventIDOutOfRange(id, DATA, 255)

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
        if "PROPS" not in attrs:
            raise AttributeError(f"Class {name} doesn't have a PROPS attribute")

        offset = 0
        offsets = attrs["OFFSETS"] = {}
        for key, type_or_size in cast(Dict[str, Any], attrs["PROPS"]).items():
            offsets[key] = offset
            if isinstance(type_or_size, int):
                offset += type_or_size
            else:
                offset += cls.SIZES[type_or_size]
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
        self._props: dict[str, Any] = dict.fromkeys(type(self).PROPS)
        self._stream = stream
        self._stream_len = len(stream.getvalue())

        for key, type_or_size in type(self).PROPS.items():
            if isinstance(type_or_size, int):
                self._props[key] = self._stream.read(type_or_size)
            else:
                self._props[key] = getattr(self._stream, f"read_{type_or_size}")()

    def __bytes__(self):
        return self._stream.getvalue()

    def __len__(self):
        return self._stream_len

    def __contains__(self, key: str):
        return key in self._props

    def __getitem__(self, key: str):
        return self._props[key]

    def __setitem__(self, key: str, value: Any):
        if key not in type(self).PROPS:
            raise KeyError(key)

        self._stream.seek(type(self).OFFSETS[key])
        type_or_size = type(self).PROPS[key]
        if isinstance(type_or_size, int):
            self._stream.write(value)
        else:
            getattr(self._stream, f"write_{type_or_size}")(value)

        if len(self._stream.getvalue()) > self._stream_len and self.TRUNCATE:
            raise PropertyCannotBeSet
        self._props[key] = value


class StructEventBase(DataEventBase):
    """Base class for events used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event as well as FL version.
    """

    STRUCT: ClassVar[type[StructBase]]

    def __init__(self, id: int, data: bytes):
        super().__init__(id, data)
        self._struct = self.STRUCT(self._stream)
        if self._stream.tell() < self._stream_len:
            warnings.warn(
                f"Event {id} not parsed entirely; "
                f"parsed {self._stream.tell()}, found {self._stream_len} bytes",
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
        cls = type(self).__name__
        size = self._stream_len
        props = self._struct._props
        return f"{cls} (id={self.id!r}, size={size}, props={props!r})"


class ListEventBase(DataEventBase, Iterable[StructBase]):
    """Base class for events storing an array of structured data."""

    STRUCT: ClassVar[type[StructBase]]

    def __init__(self, id: int, data: bytes):
        super().__init__(id, data)
        self.items: list[StructBase] = []
        self.unparsed = False

        size = type(self).STRUCT.SIZE

        # ? Make this lazily evaluated
        if not self._stream_len % size:
            for _ in range(int(self._stream_len / size)):
                self.items.append(type(self).STRUCT(self._stream))
        else:
            self.unparsed = True
            warnings.warn(
                f"Cannot parse event {id} as event "
                "size is not a multiple of struct size"
            )

    def __getitem__(self, index: SupportsIndex):
        return self.items[index]

    def __setitem__(self, index: SupportsIndex, item: StructBase):
        self.items[index] = item

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        cls = type(self).__name__
        size = self._stream_len
        num_items = len(self.items)
        return f"{cls} (id={self.id!r}, size={size}, {num_items} items)"


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


class ModelBase(abc.ABC):
    def __init__(self, **kw: Any):
        self._kw = kw

    @abc.abstractmethod
    def sizeof(self) -> int:
        """Total size of the events used by the model (in bytes).

        !!! caution
            Do not confuse this with the internal `__sizeof__` method, it is
            not the same.
        """


ST = TypeVar("ST", bound=StructBase)


class ItemModel(ModelBase, Generic[ST]):
    """Base class for event-less models."""

    def __init__(self, item: ST, **kw: Any):
        self._item = item
        super().__init__(**kw)

    def __getitem__(self, prop: str):
        return self._item[prop]

    def __setitem__(self, prop: str, value: Any):
        self._item[prop] = value

    def sizeof(self) -> int:
        return self._item.SIZE


class SingleEventModel(ModelBase, Hashable):
    """Base class for models whose properties are derived from a single event."""

    def __init__(self, event: AnyEvent, **kw: Any):
        super().__init__(**kw)
        self._event = event

    def __eq__(self, o: object):
        if not isinstance(o, type(self)):
            raise TypeError(f"Cannot compare {type(o)!r} with {type(self)!r}")

        return o.event() == self.event()

    def __hash__(self) -> int:
        return hash(self.event())

    def event(self) -> AnyEvent:
        """Returns the underlying event used by the model.

        Tip:
            You almost never need to use this method and it is only provided
            to calm type checkers from complaining about protected access.
        """
        return self._event

    def sizeof(self) -> int:
        return len(self._event)


class MultiEventModel(ModelBase, Hashable):
    def __init__(self, *events: AnyEvent, **kw: Any):
        super().__init__(**kw)
        self._events: dict[int, list[AnyEvent]] = {}
        self._events_tuple = events
        tmp: DefaultDict[int, list[AnyEvent]] = collections.defaultdict(list)

        for event in events:
            if event is not None:
                tmp[event.id].append(event)
        self._events.update(tmp)

    def __eq__(self, o: object):
        if not isinstance(o, type(self)):
            raise TypeError(f"Cannot compare {type(o)!r} with {type(self)!r}")

        return o.events_astuple() == self.events_astuple()

    def __hash__(self) -> int:
        return hash(self.events_astuple())

    def events_astuple(self):
        """Returns a tuple of events used by the model in their original order."""
        return self._events_tuple

    def events_asdict(self):
        """Returns a dictionary of event ID to a list of events."""
        return self._events

    def sizeof(self) -> int:
        return sum(len(event) for event in self._events_tuple)


class ModelReprMixin:
    """I am too lazy to make one `__repr__()` for every model."""

    def __repr__(self):
        mapping: dict[str, Any] = {}
        cls = type(self)
        # pylint: disable-next=bad-builtin
        for var in filter(lambda var: not var.startswith("_"), vars(cls)):
            if isinstance(getattr(cls, var), ROProperty):
                mapping[var] = getattr(self, var, None)

        params = ", ".join([f"{k}={v!r}" for k, v in mapping.items()])
        return f"{cls.__name__} ({params})"


MT_co = TypeVar("MT_co", bound=ModelBase, covariant=True)
SEMT_co = TypeVar("SEMT_co", bound=SingleEventModel, covariant=True)


@runtime_checkable
class ROProperty(Protocol[T_co]):
    """Protocol for a read-only descriptor."""

    def __get__(self, instance: Any, owner: Any = None) -> T_co | None:
        ...


@runtime_checkable
class RWProperty(ROProperty[T], Protocol):
    """Protocol for a read-write descriptor."""

    def __set__(self, instance: Any, value: T):
        ...


class NamedPropMixin:
    def __init__(self, prop: str | None = None) -> None:
        self._prop = prop or ""

    def __set_name__(self, _: Any, name: str):
        if not self._prop:
            self._prop = name


class FlagProp(RWProperty[bool]):
    """Properties derived from enum flags."""

    def __init__(
        self,
        flag: enum.IntFlag,
        id: EventEnum | None = None,
        prop: str = "flags",
        inverted: bool = False,
    ):
        """
        Args:
            flag (enum.IntFlag): The flag which is to be checked for.
            id (EventEnum, optional): Event ID (required for MultiEventModel).
            prop (str, "flags"): The dict key which contains the flags in a `Struct`.
            inverted (bool, False): If this is true, property getter and setters
                invert the value to be set / returned.
        """
        self._flag = flag
        self._id = id
        self._prop = prop
        self._inverted = inverted

    def _get_struct(self, instance: ModelBase):
        if isinstance(instance, ItemModel):
            return cast(StructEventBase, instance)

        if isinstance(instance, SingleEventModel):
            return cast(StructEventBase, instance.event())

        if isinstance(instance, MultiEventModel) and self._id is not None:
            try:
                event = instance.events_asdict()[self._id][0]
            except (KeyError, IndexError):
                pass
            else:
                return cast(StructEventBase, event)

    def __get__(self, instance: ModelBase, _: Any = None) -> bool | None:
        struct = self._get_struct(instance)
        if struct is not None:
            flags: int | None = struct[self._prop]
            if flags is not None:
                retbool = self._flag in type(self._flag)(flags)
                return not retbool if self._inverted else retbool

    def __set__(self, instance: ModelBase, value: bool):
        struct = self._get_struct(instance)
        if struct is None:
            if self._id is None:
                raise PropertyCannotBeSet
            raise PropertyCannotBeSet(self._id)

        if self._inverted:
            value = not value

        if value:
            struct[self._prop] |= self._flag
        else:
            struct[self._prop] &= ~self._flag


class KWProp(NamedPropMixin, RWProperty[T]):
    """Properties derived from non-local event values.

    These values are passed to the class constructor as keyword arguments.
    """

    def __get__(self, instance: ModelBase, owner: Any = None) -> T:
        if owner is None:
            return NotImplemented
        return instance._kw[self._prop]

    def __set__(self, instance: ModelBase, value: T):
        if self._prop not in instance._kw:
            raise KeyError(self._prop)
        instance._kw[self._prop] = value


class EventProp(RWProperty[T]):
    """Properties bound directly to one of fixed size or string events."""

    def __init__(self, *ids: EventEnum, default: T | None = None):
        self._ids = ids
        self._default = default

    def __get__(self, instance: MultiEventModel, owner: Any = None) -> T | None:
        if owner is None:
            return NotImplemented

        for id in self._ids:
            try:
                event = instance._events[id][0]
            except (KeyError, IndexError):
                continue
            else:
                return event.value

        return self._default

    def __set__(self, instance: MultiEventModel, value: T):
        for id in self._ids:
            try:
                event = instance._events[id][0]
            except (KeyError, IndexError):
                continue
            else:
                event.value = value


class NestedProp(ROProperty[MT_co]):
    def __init__(self, type: type[MT_co], *ids: EventEnum):
        self._ids = ids
        self._type = type

    def __get__(self, instance: MultiEventModel, owner: Any = None) -> MT_co:
        if owner is None:
            return NotImplemented

        events: list[AnyEvent] = []
        for id in self._ids:
            if id in instance._events:
                events.extend(instance._events[id])
        return self._type(*events)


class StructProp(NamedPropMixin, RWProperty[T]):
    """Properties obtained from a :class:`StructBase`."""

    def __init__(self, prop: str | None = None, id: EventEnum | None = None):
        super().__init__(prop)
        self._id = id

    def _get_event(self, instance: Any) -> StructEventBase | None:
        if isinstance(instance, SingleEventModel):
            return cast(StructEventBase, instance.event())

        if isinstance(instance, MultiEventModel) and self._id is not None:
            events = instance.events_asdict().get(self._id)
            if events is not None:
                return cast(StructEventBase, events[0])

    def __get__(self, instance: ModelBase, owner: Any = None) -> T | None:
        if owner is None:
            return NotImplemented

        if isinstance(instance, ItemModel):
            return instance[self._prop]

        event = self._get_event(instance)
        if event is not None:
            return event[self._prop]

    def __set__(self, instance: ModelBase, value: T):
        if isinstance(instance, ItemModel):
            instance[self._prop] = value
        else:
            event = self._get_event(instance)
            if event is not None:
                event[self._prop] = value


@dataclasses.dataclass(frozen=True, order=True)
class FLVersion:
    major: int
    minor: int = 0
    patch: int = 0
    build: int | None = None

    def __str__(self):
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.build is not None:
            return f"{version}.{self.build}"
        return version
