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
import warnings
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, ClassVar, Final, Generic, Tuple, cast

import construct as c
from sortedcontainers import SortedList
from typing_extensions import Concatenate, TypeAlias

from pyflp.exceptions import (
    EventIDOutOfRange,
    InvalidEventChunkSize,
    PropertyCannotBeSet,
)
from pyflp.types import RGBA, P, T, AnyContainer, AnyListContainer, AnyList, AnyDict

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


class _EventEnumMeta(enum.EnumMeta):
    def __contains__(self, obj: object) -> bool:
        """Whether ``obj`` is one of the integer values of enum members.

        Args:
            obj: Can be an ``int`` or an ``EventEnum``.
        """
        return obj in tuple(self)


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


class EventBase(Generic[T]):
    """Generic ABC representing an event."""

    STRUCT: c.Construct[T, T]
    ALLOWED_IDS: ClassVar[Sequence[int]] = []

    def __init__(self, id: EventEnum, data: bytes, **kwds: Any) -> None:
        if self.ALLOWED_IDS and id not in self.ALLOWED_IDS:
            raise EventIDOutOfRange(id, *self.ALLOWED_IDS)

        if id < TEXT:
            if id < WORD:
                expected_size = 1
            elif id < DWORD:
                expected_size = 2
            else:
                expected_size = 4

            if len(data) != expected_size:
                raise InvalidEventChunkSize(expected_size, len(data))

        self.id = EventEnum(id)
        self._kwds = kwds
        self.value = self.STRUCT.parse(data, **self._kwds)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, EventBase):
            raise TypeError(f"Cannot find equality of an {type(o)} and {type(self)!r}")
        return self.id == o.id and self.value == cast(EventBase[T], o).value

    def __ne__(self, o: object) -> bool:
        if not isinstance(o, EventBase):
            raise TypeError(f"Cannot find inequality of a {type(o)} and {type(self)!r}")
        return self.id != o.id or self.value != cast(EventBase[T], o).value

    def __bytes__(self) -> bytes:
        id = c.Byte.build(self.id)
        data = self.STRUCT.build(self.value, **self._kwds)

        if self.id < TEXT:
            return id + data

        length = c.VarInt.build(len(data))
        return id + length + data

    def __repr__(self) -> str:
        return f"<{type(self)!r}(id={self.id!r}, value={self.value!r})>"

    @property
    def size(self) -> int:
        """Serialised event size (in bytes)."""

        if self.id >= TEXT:
            return len(bytes(self))
        elif self.id >= DWORD:
            return 5
        elif self.id >= WORD:
            return 3
        else:
            return 2


AnyEvent: TypeAlias = EventBase[Any]


class ByteEventBase(EventBase[T]):
    """Base class of events used for storing 1 byte data."""

    ALLOWED_IDS = range(BYTE, WORD)

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

    STRUCT = c.Flag


class I8Event(ByteEventBase[int]):
    """An event used for storing a 1 byte signed integer."""

    STRUCT = c.Int8sl


class U8Event(ByteEventBase[int]):
    """An event used for storing a 1 byte unsigned integer."""

    STRUCT = c.Int8ul


class WordEventBase(EventBase[int], abc.ABC):
    """Base class of events used for storing 2 byte data."""

    ALLOWED_IDS = range(WORD, DWORD)

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


class I16Event(WordEventBase):
    """An event used for storing a 2 byte signed integer."""

    STRUCT = c.Int16sl


class U16Event(WordEventBase):
    """An event used for storing a 2 byte unsigned integer."""

    STRUCT = c.Int16ul


class DWordEventBase(EventBase[T], abc.ABC):
    """Base class of events used for storing 4 byte data."""

    ALLOWED_IDS = range(DWORD, TEXT)

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

    STRUCT = c.Float32l


class I32Event(DWordEventBase[int]):
    """An event used for storing a 4 byte signed integer."""

    STRUCT = c.Int32sl


class U32Event(DWordEventBase[int]):
    """An event used for storing a 4 byte unsigned integer."""

    STRUCT = c.Int32ul


class U16TupleEvent(DWordEventBase[Tuple[int, int]]):
    """An event used for storing a two-tuple of 2 byte unsigned integers."""

    STRUCT = c.ExprAdapter(
        c.Int16ul[2],
        lambda obj_, *_: tuple(obj_),  # type: ignore
        lambda obj_, *_: list(obj_),  # type: ignore
    )


class ColorEvent(DWordEventBase[RGBA]):
    """A 4 byte event which stores a color."""

    STRUCT = c.ExprAdapter(
        c.Bytes(4),
        lambda obj, *_: RGBA.from_bytes(obj),  # type: ignore
        lambda obj, *_: bytes(obj),  # type: ignore
    )


class StrEventBase(EventBase[str]):
    """Base class of events used for storing strings."""

    ALLOWED_IDS = (*range(TEXT, DATA), *NEW_TEXT_IDS)

    def __init__(self, id: EventEnum, data: bytes) -> None:
        """
        Args:
            id: **192** to **207** or in :attr:`NEW_TEXT_IDS`.
            data: ASCII or UTF16 encoded string data.

        Raises:
            ValueError: When ``id`` is not in 192-207 or in :attr:`NEW_TEXT_IDS`.
        """
        super().__init__(id, data)


class AsciiEvent(StrEventBase):
    if TYPE_CHECKING:
        STRUCT: c.ExprAdapter[str, str, str, str]
    else:
        STRUCT = c.ExprAdapter(
            c.GreedyString("ascii"),
            lambda obj, *_: obj.rstrip("\0"),
            lambda obj, *_: obj + "\0",
        )


class UnicodeEvent(StrEventBase):
    if TYPE_CHECKING:
        STRUCT: c.ExprAdapter[str, str, str, str]
    else:
        STRUCT = c.ExprAdapter(
            c.GreedyString("utf-16-le"),
            lambda obj, *_: obj.rstrip("\0"),
            lambda obj, *_: obj + "\0",
        )


class StructEventBase(EventBase[AnyContainer], AnyDict):
    """Base class for events used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event as well as FL version.
    """

    def __init__(self, id: EventEnum, data: bytes) -> None:
        super().__init__(id, data, len=len(data))
        self.data = self.value  # Akin to UserDict.__init__

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in self:
            raise KeyError

        if self[key] is None:
            raise PropertyCannotBeSet

        self.data[key] = value


class ListEventBase(EventBase[AnyListContainer], AnyList):
    """Base class for events storing an array of structured data.

    Attributes:
        kwds: Keyword args passed to :meth:`STRUCT.parse` & :meth:`STRUCT.build`.
    """

    STRUCT: c.Subconstruct[Any, Any, Any, Any]
    SIZES: ClassVar[list[int]] = []
    """Manual :meth:`STRUCT.sizeof` override(s)."""

    def __init__(self, id: EventEnum, data: bytes, **kwds: Any) -> None:
        super().__init__(id, data, **kwds)
        self._struct_size: int | None = None

        if not self.SIZES:
            self._struct_size = self.STRUCT.subcon.sizeof()

        for size in self.SIZES:
            if not len(data) % size:
                self._struct_size = size
                break

        if self._struct_size is None:  # pragma: no cover
            warnings.warn(
                f"Cannot parse event {id} as event size {len(data)} "
                f"is not a multiple of struct size(s) {self.SIZES}"
            )
        else:
            self.data = self.value  # Akin to UserList.__init__


class UnknownDataEvent(EventBase[bytes]):
    """Used for events whose structure is unknown as of yet."""

    STRUCT = c.GreedyBytes


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
        self.lst: list[IndexedEvent] = SortedList(init or [])  # type: ignore

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
            if result is False:
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
