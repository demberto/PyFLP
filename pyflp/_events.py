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
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain, zip_longest
from typing import (
    Any,
    Callable,
    ClassVar,
    DefaultDict,
    Generic,
    Iterable,
    Iterator,
    Tuple,
    TypeVar,
    cast,
)

if sys.version_info >= (3, 8):
    from typing import Final, Literal
else:
    from typing_extensions import Final, Literal

import colour
import construct as c
from sortedcontainers import SortedList, SortedSet

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

    def __init__(self, id: EventEnum, data: bytes):
        self.id: Final = EventEnum(id)
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

    def __init__(self, id: EventEnum, data: bytes):
        if id not in range(*self.ID_RANGE):
            raise EventIDOutOfRange(id, *self.ID_RANGE)

        if len(data) != self.CODEC.sizeof():
            raise InvalidEventChunkSize(self.CODEC.sizeof(), len(data))

        super().__init__(id, data)

    def __bytes__(self):
        return c.Byte.build(self.id) + self._data

    def __repr__(self):
        return f"{type(self).__name__} (id={self.id!r}, value={self.value!r})"

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

    def __init__(self, id: EventEnum, data: bytes):
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

    def __init__(self, id: EventEnum, data: bytes):
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

    def __init__(self, id: EventEnum, data: bytes):
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

    def __init__(self, id: EventEnum, data: bytes):
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

    def __repr__(self):
        return f"{type(self).__name__} (id={self.id!r}, string={self.value!r})"


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
    def __init__(self, id: EventEnum, data: bytes):
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

    def __repr__(self):
        return f"{type(self).__name__} (id={self.id!r}, size={len(self._data)})"


# TODO Due to construct's poor implementation of LazyStruct, this is no longer lazy
class StructEventBase(DataEventBase):
    """Base class for events used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event as well as FL version.
    """

    STRUCT: ClassVar[c.Construct[c.Container[Any], Any]]

    def __init__(self, id: EventEnum, data: bytes):
        super().__init__(id, data)
        self._struct = self.STRUCT.parse(data)

    def __bytes__(self):
        # pylint: disable=access-member-before-definition
        # pylint: disable=attribute-defined-outside-init
        new_data = self.STRUCT.build(self._struct)
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

    def __init__(self, id: EventEnum, data: bytes):
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
        self._data = (  # pylint: disable=attribute-defined-outside-init
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


@dataclass(order=True)
class IndexedEvent:
    r: int
    """Root index of occurence of :attr:`e`."""

    e: AnyEvent = field(compare=False)
    """The indexed event."""


# TODO Insertion / deletion from parent should affect children
class EventTree:
    """Multidict which provides mutable "views" mimicking a tree-like structure.

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
    ):
        """Create a new dictionary with an optional :attr:`parent`."""
        self.children: list[EventTree] = []
        self.dct: DefaultDict[EventEnum, list[IndexedEvent]] = defaultdict(SortedList)
        if init:
            for ie in init:
                self.dct[ie.e.id].add(ie)  # type: ignore

        self.parent = parent
        if parent is not None:
            parent.children.append(self)

        while parent is not None and parent.parent is not None:
            parent = parent.parent
        self.root = parent or self

    def __contains__(self, id: EventEnum):
        """Whether the key :attr:`id` exists in the dictionary."""
        return id in self.dct

    def __delitem__(self, id: EventEnum):
        """Removes all events with matching :attr:`id`."""
        for _ in range(len(self.dct[id])):
            self.remove(id)

    def __eq__(self, o: object) -> bool:
        """Compares equality of internal dictionaries."""
        if not isinstance(o, EventTree):
            return NotImplemented

        return self.dct == o.dct

    def __getitem__(self, id: EventEnum) -> Iterator[AnyEvent]:
        """Yields events with matching :attr:`id`."""
        return (ie.e for ie in self.dct[id])

    def __iadd__(self, *events: AnyEvent) -> None:
        """Analogous to :meth:`list.extend`."""
        for event in events:
            self.append(event)

    def __ior__(self, ed: EventTree) -> None:
        """Merge :attr:`ed` into this dictionary."""
        if self.indexes & ed.indexes:
            raise ValueError("Conflicting root indexes")

        self.dct.update(ed.dct)

    def __iter__(self) -> Iterator[EventEnum]:
        return iter(self.dct)

    def __len__(self) -> int:
        """Number of events of all IDs inside this dictionary."""
        return sum(len(self.dct[id]) for id in self)

    def __repr__(self) -> str:
        return f"EventTree ({len(self.dct)} IDs, {len(self)} events)"

    def __setitem__(self, id: EventEnum, it: Iterator[AnyEvent]) -> None:
        """Modifies events held by an existing :class:`IndexedEvent`.

        Raises:
            IndexError: When the internal dictionary's list for key :attr:`id`
                isn't big enough to hold all events in :attr:`it`.
        """
        for i, e in enumerate(it):
            self.dct[id][i].e = e

    def _recursive(self, action: Callable[[EventTree], None]) -> None:
        """Recursively performs :attr:`action` on self and all parents."""
        action(self)
        ancestor = self.parent
        while ancestor is not None:
            action(ancestor)
            ancestor = ancestor.parent

    def all(self) -> Iterator[AnyEvent]:
        """Yields all events in this dictionary sorted w.r.t to their root indexes."""
        return (ie.e for ie in sorted(ie for id in self for ie in self.dct[id]))

    def append(self, event: AnyEvent) -> None:
        """Appends an event at its corresponding key's list's end."""
        self.insert(-1, event)

    # Wish I could use __getitem__ overload for this, but EventEnum shadows int.
    def at(self, index: int, mode: Literal["local", "root"] = "local") -> AnyEvent:
        """Returns the event at local or root ``index``.

        Args:
            index: A list (+ve or -ve) index or a root (zero-based) index.
            mode: Whether to lookup local (list) index or root (insertion) index.

        Raises:
            IndexError: If an event with ``index`` could not be found.
        """
        it = chain.from_iterable(self.dct.values())

        if mode == "local":
            return sorted(it)[index].e

        for ie in it:
            if ie.r == index:
                return ie.e

        raise IndexError(index)

    def count(self, id: EventEnum) -> int:
        """Returns the count of the events with :attr:`id`."""
        if id not in self.dct:
            raise KeyError(id)
        return len(self.dct[id])

    def divide(self, separator: EventEnum, *ids: EventEnum) -> Iterator[EventTree]:
        """Yields subtrees containing events separated by ``separator`` infinitely."""
        el: list[IndexedEvent] = []
        first = True
        for ie in sorted(chain.from_iterable(self.dct.values())):
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
        if id not in self.dct:
            raise KeyError(id)
        return self.dct[id][0].e

    def get(self, *ids: EventEnum) -> list[AnyEvent]:
        """Returns a sorted list of events whose ID is one of :attr:`ids`."""
        return [t.e for t in sorted(t for i in ids if i in self for t in self.dct[i])]

    def group(self, *ids: EventEnum) -> Iterator[EventTree]:
        """Yields EventTrees of zip objects of events with matching :attr:`ids`.

        Transforms a ``dict`` like this:

            {A: [Event(A, 1), Event(A, 2)], B: [Event(B, 1)]}

        into an ``EventTree`` list like this:

            [EventTree([Event(A, 1), Event(B, 1)]), EventTree([Event(A, 2)])]
        """
        for iel in zip_longest(*(self.dct[id] for id in ids)):  # unpack magic
            obj = EventTree(self, [ie for ie in iel if ie])  # filter out None values
            self.children.append(obj)
            yield obj

    # TODO! First event's rootidx gets pushed to last
    def insert(self, pos: int, e: AnyEvent):
        """Inserts :attr:`ev` at :attr:`pos` in this and all parent trees."""
        rootidx = cast(int, self.indexes[pos]) if len(self) else 0

        # Shift all root indexes after rootidx by +1 to prevent collisions
        # while sorting the entire list by root indexes before serialising.
        for ie in chain.from_iterable(self.root.dct.values()):
            if ie.r >= rootidx:
                ie.r += 1

        self._recursive(lambda ed: ed.dct[e.id].add(IndexedEvent(rootidx, e)))  # type: ignore # noqa

    def items(self) -> Iterator[tuple[EventEnum, Iterator[AnyEvent]]]:
        yield from ((id, self[id]) for id in self)

    def only(self) -> AnyEvent:
        """Same as ``next(self.all())`` but raises ValueError if dict size isn't 1."""
        if len(self) != 1:
            raise ValueError("Dictionary should contain exactly one element.")
        return next(self.all())

    def pop(self, id: EventEnum, pos: int = 0) -> AnyEvent:
        """Pops the event with ``id`` at ``pos`` in ``self`` and all parents."""
        if id not in self.dct:
            raise KeyError(id)

        ie = self.dct[id][pos]
        self._recursive(lambda ed: ed.dct[id].remove(ie))

        # Remove keys with empty lists
        for k in tuple(self.dct.keys()):
            if not self.dct[k]:
                del self.dct[k]

        # Shift all root indexes of events after rootidx by -1.
        # Not really required but ensure consistency of the indexes
        for ielt in (t for lst in self.root.dct.values() for t in lst if t.r >= ie.r):
            ielt.r -= 1

        return ie.e

    def remove(self, id: EventEnum, pos: int = 0) -> None:
        """Removes the event with ``id`` at ``pos`` in ``self`` and all parents."""
        self.pop(id, pos)

    def separate(self, id: EventEnum) -> Iterator[EventTree]:
        """Yields a separate ``EventTree`` for every event with matching ``id``."""
        for ie in self.dct[id]:
            obj = EventTree(self, [ie])
            self.children.append(obj)
            yield obj

    def subdict(self, select: Callable[[AnyEvent], bool | None]) -> EventTree:
        """Returns a mutable view containing events for which ``select`` was True.

        Caution:
            Always use this function to create a mutable view. Maintaining
            chilren and passing parent to a child are best done here.
        """
        el: list[IndexedEvent] = []
        for ie in sorted(chain.from_iterable(self.dct.values())):
            if select(ie.e):
                el.append(ie)
        obj = EventTree(self, el)
        self.children.append(obj)
        return obj

    def subdicts(
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
        for ie in sorted(chain.from_iterable(self.dct.values())):
            if not repeat:
                return

            result = select(ie.e)
            if result is False:  # pylint: disable=compare-to-zero
                obj = EventTree(self, el)
                self.children.append(obj)
                yield obj
                el = [ie]  # Don't skip current event
                repeat -= 1
            elif result is not None:
                el.append(ie)

    @property
    def indexes(self):
        """Returns root indexes for all events in ``self``."""
        return SortedSet(ie.r for lst in self.dct.values() for ie in lst)
