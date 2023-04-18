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

"""Contains implementations for various types of event data and its container.

These types serve as the backbone for model creation and simplify marshalling
and unmarshalling.
"""

from __future__ import annotations

import abc
import enum
import sys
import warnings
from dataclasses import dataclass, field
from itertools import zip_longest
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Iterator,
    NoReturn,
    Tuple,
    TypeVar,
    cast,
)

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

if sys.version_info >= (3, 10):
    from typing import Concatenate, ParamSpec
else:
    from typing_extensions import Concatenate, ParamSpec

import colour
import construct as c
from sortedcontainers import SortedList

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

P = ParamSpec("P")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
FourByteBool: c.ExprAdapter[int, int, bool, int] = c.ExprAdapter(
    c.Int32ul, lambda obj_, *_: bool(obj_), lambda obj_, *_: int(obj_)  # type: ignore
)


class _EventEnumMeta(enum.EnumMeta):
    # pylint: disable=bad-mcs-method-argument
    def __contains__(self, obj: object) -> bool:
        """Whether ``obj`` is one of the integer values of enum members.

        Args:
            obj: Can be an ``int`` or an ``EventEnum``.
        """
        return obj in tuple(self)  # type: ignore


class EventEnum(int, enum.Enum, metaclass=_EventEnumMeta):
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

    # This allows EventBase.id to actually use EventEnum for representation and
    # not just equality checks. It will be much simpler to debug problematic
    # events, if the name of the ID is directly visible.
    @classmethod
    def _missing_(cls, value: object) -> EventEnum | None:
        """Allows unknown IDs in the range of 0-255."""
        if isinstance(value, int) and 0 <= value <= 255:
            # First check in existing subclasses
            for sc in cls.__subclasses__():
                if value in sc:
                    return sc(value)

            # Else create a new pseudo member
            pseudo_member = cls._value2member_map_.get(value, None)
            if pseudo_member is None:
                new_member = int.__new__(cls, value)
                new_member._name_ = str(value)
                new_member._value_ = value
                pseudo_member = cls._value2member_map_.setdefault(value, new_member)
            return cast(EventEnum, pseudo_member)
        # Raises ValueError in Enum.__new__


class EventBase(Generic[T]):  # pylint: disable=eq-without-hash
    """Generic ABC representing an event."""

    def __init__(self, id: EventEnum, data: bytes) -> None:
        self.id: Final = EventEnum(id)
        self._data: bytes = data

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, EventBase):
            raise TypeError(f"Cannot find equality of an {type(o)} and {type(self)!r}")
        return self.id == o.id and self._data == o._data

    def __ne__(self, o: object) -> bool:
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
        raise NotImplementedError

    @value.setter
    def value(self, value: T) -> None:
        """Converts Python types into bytes/bytes objects and stores it."""


AnyEvent = EventBase[Any]


class PODEventBase(EventBase[T]):
    """Base class for events whose size is predetermined (POD types)."""

    ID_RANGE: ClassVar[tuple[int, int]]
    CODEC: c.Construct[Any, Any]

    def __init__(self, id: EventEnum, data: bytes) -> None:
        if id not in range(*self.ID_RANGE):
            raise EventIDOutOfRange(id, *self.ID_RANGE)

        if len(data) != self.CODEC.sizeof():
            raise InvalidEventChunkSize(self.CODEC.sizeof(), len(data))

        super().__init__(id, data)

    def __bytes__(self) -> bytes:
        return c.Byte.build(self.id) + self._data

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r}, value={self.value!r})"

    @property
    def size(self) -> int:
        return 1 + self.CODEC.sizeof()

    @property
    def value(self) -> T:
        return self.CODEC.parse(self._data)

    @value.setter
    def value(self, value: T) -> None:
        self._data = self.CODEC.build(value)


class ByteEventBase(PODEventBase[T]):
    """Base class of events used for storing 1 byte data."""

    ID_RANGE = (BYTE, WORD)

    def __init__(self, id: EventEnum, data: bytes) -> None:
        """
        Args:
            id: **0** to **63**.
            data: Event data of size 1.

        Raises:
            EventIDOutOfRangeError: When ``id`` is not in range of 0-63.
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

    def __init__(self, id: EventEnum, data: bytes) -> None:
        """
        Args:
            id: **64** to **127**.
            data: Event data of size 2.

        Raises:
            EventIDOutOfRangeError: When ``id`` is not in range of 64-127.
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

    def __init__(self, id: EventEnum, data: bytes) -> None:
        """
        Args:
            id: **128** to **191**.
            data: Event data of size 4.

        Raises:
            EventIDOutOfRangeError: When ``id`` is not in range of 128-191.
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

    CODEC: c.ExprAdapter[  # pyright: ignore
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
    def decode(buf: bytes | bytes) -> colour.Color:
        r, g, b = (c / 255 for c in buf[:3])
        return colour.Color(rgb=(r, g, b))

    @staticmethod
    def encode(color: colour.Color) -> bytes:
        return bytes(int(c * 255) for c in color.get_rgb()) + b"\x00"


class VarintEventBase(EventBase[T]):
    @staticmethod
    def _varint_len(buflen: int) -> int:
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
    def size(self) -> int:
        if self._data:
            return 1 + self._varint_len(len(self._data)) + len(self._data)
        return 2

    def __bytes__(self) -> bytes:
        id = c.Byte.build(self.id)

        if self._data:
            return id + c.VarInt.build(len(self._data)) + self._data
        return id + b"\x00"


class StrEventBase(VarintEventBase[str]):
    """Base class of events used for storing strings."""

    def __init__(self, id: EventEnum, data: bytes) -> None:
        """
        Args:
            id: **192** to **207** or in :attr:`NEW_TEXT_IDS`.
            data: ASCII or UTF16 encoded string data.

        Raises:
            ValueError: When ``id`` is not in 192-207 or in :attr:`NEW_TEXT_IDS`.
        """
        if id not in {*range(TEXT, DATA), *NEW_TEXT_IDS}:
            raise ValueError(f"Unexpected ID{id!r}")

        super().__init__(id, data)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r}, string={self.value!r})"


class AsciiEvent(StrEventBase):
    @property
    def value(self) -> str:
        return self._data.decode("ascii").rstrip("\0")

    @value.setter
    def value(self, value: str) -> None:
        if value:
            self._data = value.encode("ascii") + b"\0"


class UnicodeEvent(StrEventBase):
    @property
    def value(self) -> str:
        return self._data.decode("utf-16-le").rstrip("\0")

    @value.setter
    def value(self, value: str) -> None:
        if value:
            self._data = value.encode("utf-16-le") + b"\0\0"


class DataEventBase(VarintEventBase[bytes]):
    def __init__(self, id: EventEnum, data: bytes) -> None:
        """
        Args:
            id: **208** to **255**.
            data: Event data (no size limit).

        Raises:
            EventIDOutOfRange: ``id`` is not in the range of 208-255.
        """
        if id < DATA:
            raise EventIDOutOfRange(id, DATA, 256)

        super().__init__(id, data)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r}, size={len(self._data)})"


# TODO Due to construct's poor implementation of LazyStruct, this is no longer lazy
class StructEventBase(DataEventBase):
    """Base class for events used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event as well as FL version.
    """

    STRUCT: ClassVar[c.Construct[c.Container[Any], Any]]

    def __init__(self, id: EventEnum, data: bytes) -> None:
        super().__init__(id, data)
        self._struct = self.STRUCT.parse(data, len=len(self._data))

    def __bytes__(self) -> bytes:
        # pylint: disable=access-member-before-definition
        # pylint: disable=attribute-defined-outside-init
        new_data = self.STRUCT.build(self._struct, len=len(self._data))
        if len(new_data) != len(self._data):
            warnings.warn(
                "{} built a stream of incorrect size {}; expected {}.".format(
                    type(self).__name__, len(new_data), len(self._data)
                ),
                BytesWarning,
                stacklevel=0,
            )
        # Effectively, overwrite new data over old one to ensure the stream
        # size remains unmodified
        self._data = new_data + self._data[len(new_data) :]
        return super().__bytes__()

    def __contains__(self, prop: str) -> bool:
        return prop in self._struct

    def __getitem__(self, key: str):
        return self._struct[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in self or self[key] is None:
            raise PropertyCannotBeSet
        self._struct[key] = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id}, size={len(self._data)})"

    @property  # type: ignore[override]
    def value(self) -> NoReturn:
        raise NotImplementedError

    @value.setter
    def value(self, value: bytes) -> NoReturn:
        raise NotImplementedError


class ListEventBase(DataEventBase):
    """Base class for events storing an array of structured data.

    Attributes:
        kwds: Keyword args passed to :meth:`STRUCT.parse` & :meth:`STRUCT.build`.
    """

    STRUCT: ClassVar[c.Construct[c.Container[Any], Any]]
    SIZES: ClassVar[list[int]] = []
    """Manual :meth:`STRUCT.sizeof` override(s)."""

    def __init__(self, id: EventEnum, data: bytes, **kwds: Any) -> None:
        super().__init__(id, data)
        self._struct_size: int | None = None
        self.kwds = kwds

        if not self.SIZES:
            self._struct_size = self.STRUCT.sizeof()

        for size in self.SIZES:
            if not len(data) % size:
                self._struct_size = size
                break

        if self._struct_size is None:  # pragma: no cover
            warnings.warn(
                f"Cannot parse event {id} as event size {len(data)} "
                f"is not a multiple of struct size(s) {self.SIZES}"
            )

    def __len__(self) -> int:
        if self._struct_size is None:  # pragma: no cover
            raise ListEventNotParsed

        return len(self._data) // self._struct_size

    def __getitem__(self, index: int) -> c.Container[Any]:
        if self._struct_size is None:  # pragma: no cover
            raise ListEventNotParsed

        if index > len(self):
            raise IndexError(index)

        start = self._struct_size * index
        count = self._struct_size
        return self.STRUCT.parse(self._data[start : start + count], **self.kwds)

    def __setitem__(self, index: int, item: c.Container[Any]) -> None:
        if self._struct_size is None:
            raise ListEventNotParsed

        if index > len(self):
            raise IndexError(index)

        start = self._struct_size * index
        count = self._struct_size
        self._data = (  # pylint: disable=attribute-defined-outside-init
            self._data[:start]
            + self.STRUCT.build(item, **self.kwds)
            + self._data[start + count :]
        )

    def __iter__(self) -> Iterator[c.Container[Any]]:
        for i in range(len(self)):
            yield self[i]

    def __repr__(self) -> str:
        return "{}(id={}, size={}, {} items)".format(
            type(self).__name__, self.id, len(self._data), len(self)
        )


class UnknownDataEvent(DataEventBase):
    """Used for events whose structure is unknown as of yet."""

    @property
    def value(self) -> bytes:
        return self._data

    @value.setter
    def value(self, value: bytes) -> None:
        self._data = value


@dataclass(order=True)
class IndexedEvent:
    r: int
    """Root index of occurence of :attr:`e`."""

    e: AnyEvent = field(compare=False)
    """The indexed event."""


def yields_child(func: Callable[Concatenate[EventTree, P], Iterator[EventTree]]):
    """Adds an :class:`EventTree` to its parent's list of children and yields it."""

    def wrapper(self: EventTree, *args: P.args, **kwds: P.kwargs):
        for child in func(self, *args, **kwds):
            self.children.append(child)
            yield child

    return wrapper


class EventTree:
    """Provides mutable "views" which propagate changes back to parents.

    This tree is analogous to the hierarchy used by models.

    Attributes:
        parent: Immediate ancestor / parent. Defaults to self.
        root: Parent of all parent trees.
        children: List of children.
    """

    def __init__(
        self,
        parent: EventTree | None = None,
        init: Iterable[IndexedEvent] | None = None,
    ) -> None:
        """Create a new dictionary with an optional :attr:`parent`."""
        self.children: list[EventTree] = []
        self.lst: list[IndexedEvent] = SortedList(init or [])

        self.parent = parent
        if parent is not None:
            parent.children.append(self)

        while parent is not None and parent.parent is not None:
            parent = parent.parent
        self.root = parent or self

    def __contains__(self, id: EventEnum) -> bool:
        """Whether the key :attr:`id` exists in the list."""
        return any(ie.e.id == id for ie in self.lst)

    def __eq__(self, o: object) -> bool:
        """Compares equality of internal lists."""
        if not isinstance(o, EventTree):
            return NotImplemented

        return self.lst == o.lst

    def __iadd__(self, *events: AnyEvent) -> None:
        """Analogous to :meth:`list.extend`."""
        for event in events:
            self.append(event)

    def __iter__(self) -> Iterator[AnyEvent]:
        return (ie.e for ie in self.lst)

    def __len__(self) -> int:
        return len(self.lst)

    def __repr__(self) -> str:
        return f"EventTree({len(self.ids)} IDs, {len(self)} events)"

    def _get_ie(self, *ids: EventEnum) -> Iterator[IndexedEvent]:
        return (ie for ie in self.lst if ie.e.id in ids)

    def _recursive(self, action: Callable[[EventTree], None]) -> None:
        """Recursively performs :attr:`action` on self and all parents."""
        action(self)
        ancestor = self.parent
        while ancestor is not None:
            action(ancestor)
            ancestor = ancestor.parent

    def append(self, event: AnyEvent) -> None:
        """Appends an event at its corresponding key's list's end."""
        self.insert(len(self), event)

    def count(self, id: EventEnum) -> int:
        """Returns the count of the events with :attr:`id`."""
        return len(list(self._get_ie(id)))

    @yields_child
    def divide(self, separator: EventEnum, *ids: EventEnum) -> Iterator[EventTree]:
        """Yields subtrees containing events separated by ``separator`` infinitely."""
        el: list[IndexedEvent] = []
        first = True
        for ie in self.lst:
            if ie.e.id == separator:
                if not first:
                    yield EventTree(self, el)
                    el = []
                else:
                    first = False

            if ie.e.id in ids:
                el.append(ie)
        yield EventTree(self, el)  # Yield the last one

    def first(self, id: EventEnum) -> AnyEvent:
        """Returns the first event with :attr:`id`.

        Raises:
            KeyError: An event with :attr:`id` isn't found.
        """
        try:
            return next(self.get(id))
        except StopIteration as exc:
            raise KeyError(id) from exc

    def get(self, *ids: EventEnum) -> Iterator[AnyEvent]:
        """Yields events whose ID is one of :attr:`ids`."""
        return (e for e in self if e.id in ids)

    @yields_child
    def group(self, *ids: EventEnum) -> Iterator[EventTree]:
        """Yields EventTrees of zip objects of events with matching :attr:`ids`."""
        for iet in zip_longest(*(self._get_ie(id) for id in ids)):  # unpack magic
            yield EventTree(self, [ie for ie in iet if ie])  # filter out None values

    def insert(self, pos: int, e: AnyEvent) -> None:
        """Inserts :attr:`ev` at :attr:`pos` in this and all parent trees."""
        rootidx = sorted(self.indexes)[pos] if len(self) else 0

        # Shift all root indexes after rootidx by +1 to prevent collisions
        # while sorting the entire list by root indexes before serialising.
        for ie in self.root.lst:
            if ie.r >= rootidx:
                ie.r += 1

        self._recursive(lambda et: et.lst.add(IndexedEvent(rootidx, e)))  # type: ignore

    def pop(self, id: EventEnum, pos: int = 0) -> AnyEvent:
        """Pops the event with ``id`` at ``pos`` in ``self`` and all parents."""
        if id not in self.ids:
            raise KeyError(id)

        ie = [ie for ie in self.lst if ie.e.id == id][pos]
        self._recursive(lambda et: et.lst.remove(ie))

        # Shift all root indexes of events after rootidx by -1.
        for root_ie in self.root.lst:
            if root_ie.r >= ie.r:
                root_ie.r -= 1

        return ie.e

    def remove(self, id: EventEnum, pos: int = 0) -> None:
        """Removes the event with ``id`` at ``pos`` in ``self`` and all parents."""
        self.pop(id, pos)

    @yields_child
    def separate(self, id: EventEnum) -> Iterator[EventTree]:
        """Yields a separate ``EventTree`` for every event with matching ``id``."""
        yield from (EventTree(self, [ie]) for ie in self._get_ie(id))

    def subtree(self, select: Callable[[AnyEvent], bool | None]) -> EventTree:
        """Returns a mutable view containing events for which ``select`` was True.

        Caution:
            Always use this function to create a mutable view. Maintaining
            chilren and passing parent to a child are best done here.
        """
        el: list[IndexedEvent] = []
        for ie in self.lst:
            if select(ie.e):
                el.append(ie)
        obj = EventTree(self, el)
        self.children.append(obj)
        return obj

    @yields_child
    def subtrees(
        self, select: Callable[[AnyEvent], bool | None], repeat: int
    ) -> Iterator[EventTree]:
        """Yields mutable views till ``select`` and ``repeat`` are satisfied.

        Args:
            select: Called for every event in this dictionary by iterating over
                a chained, sorted list. Returns True if event must be included.
                Once it returns False, rest of them are ignored and resulting
                EventTree is returned. Return None to skip an event.
            repeat: Use -1 for infinite iterations.
        """
        el: list[IndexedEvent] = []
        for ie in self.lst:
            if not repeat:
                return

            result = select(ie.e)
            if result is False:  # pylint: disable=compare-to-zero
                yield EventTree(self, el)
                el = [ie]  # Don't skip current event
                repeat -= 1
            elif result is not None:
                el.append(ie)

    @property
    def ids(self) -> frozenset[EventEnum]:
        return frozenset(ie.e.id for ie in self.lst)

    @property
    def indexes(self) -> frozenset[int]:
        """Returns root indexes for all events in ``self``."""
        return frozenset(ie.r for ie in self.lst)
