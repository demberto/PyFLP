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

import enum
import warnings
from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Generic, SupportsIndex, TypeVar

import attrs
import construct as c
import construct_typed as ct
from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from _typeshed import SupportsItemAccess

_T = TypeVar("_T")

BYTE = 0
WORD = 64
DWORD = 128
TEXT = 192
DATA = 208
NEW_TEXT_IDS = (
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


class EventEnum(ct.EnumBase, metaclass=_EventEnumMeta):
    """IDs used by events.

    Event values are stored as a tuple of event ID and its designated type.
    The types are used to serialise/deserialise events by the parser.

    All event names prefixed with an underscore (_) are deprecated w.r.t to
    the latest version of FL Studio, *to the best of my knowledge*.
    """

    def __new__(cls, id: int, struct: c.Construct[Any, Any] | None = None):
        obj = int.__new__(cls, id)
        obj._value_ = id
        obj._struct_ = struct  # type: ignore
        return obj


def _check_data_size(event: Any, _: Any, data: bytes) -> None:
    if event.id < TEXT:
        if event.id < WORD:
            expect = 1
        elif event.id < DWORD:
            expect = 2
        else:
            expect = 4

        if len(data) != expect:
            raise ValueError(f"Invalid size of 'data' {len(data)}; expected {expect}")


@attrs.define
class Event(Generic[_T]):
    id: EventEnum = attrs.field(validator=attrs.validators.in_(range(0, 256)))
    data: bytes = attrs.field(validator=_check_data_size, repr=False)
    struct: c.Construct[_T, _T]
    lazy: bool = attrs.field(default=False, kw_only=True)

    def __attrs_post_init__(self) -> None:
        self._cache: Any = None
        if not self.lazy:
            _ = self.value

    def __bytes__(self) -> bytes:
        id = c.Byte.build(self.id)
        data = self.struct.build(self.value)

        if self.id < TEXT:
            return id + data
        return id + c.VarInt.build(len(data)) + data

    @property
    def value(self) -> _T:
        if self._cache is None:
            value = self.struct.parse(self.data)
            if isinstance(value, dict) and isinstance(self.struct, c.Struct):
                self._cache = _ValidatingDict(self.struct, **value)  # type: ignore
            elif isinstance(value, list):
                self._cache = _ValidatingList(self.struct, *value)  # type: ignore
            else:
                self._cache = value
        return self._cache

    @value.setter
    def value(self, value: _T) -> None:
        self.struct.build(value)
        self._cache = value

    @value.deleter
    def value(self) -> None:
        self._cache = None


class _ValidationMixin(SupportsItemAccess[_T, Any] if TYPE_CHECKING else object):
    subcons: SupportsItemAccess[_T, c.Construct[Any, Any]]

    def __getitem__(self, key: _T) -> Any:
        child = super().__getitem__(key)
        childcon = self.subcons[key]

        if TYPE_CHECKING:
            assert isinstance(childcon, c.Struct)

        if isinstance(child, dict):
            return _ValidatingDict(childcon, **child)
        elif isinstance(child, list):
            return _ValidatingList(childcon, *child)
        return child

    def __setitem__(self, key: _T, value: Any) -> None:
        self.subcons[key].build(value)


class _ValidatingDict(Dict[str, Any], _ValidationMixin[str]):
    def __init__(self, struct: c.Struct[Any, Any], **kwds: Any) -> None:
        self.subcons = struct._subcons  # Dict[str, c.Construct[Any, Any]]
        super().__init__(**kwds)

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in self:
            raise KeyError("No new keys allowed")

        if self[key] is None:
            raise AttributeError("Key must already have a value")

        _ValidationMixin[str].__setitem__(self, key, value)
        Dict[str, Any].__setitem__(self, key, value)

    def __delitem__(self, _: str) -> None:
        raise AttributeError("Keys cannot be deleted")


class _ValidatingList(List[Any], _ValidationMixin[SupportsIndex]):
    def __init__(self, struct: c.Struct[Any, Any], *args: Any) -> None:
        self.subcons = struct.subcons  # List[c.Construct[Any, Any]]
        super().__init__(*args)


def make_struct_event(*subcons: c.Construct[Any, Any], optional: bool = True):
    args = [c.Optional(s) for s in subcons] if optional else subcons
    return partial(Event[Dict[str, Any]], struct=c.Struct(*args))


class ListEventBase(Event[c.ListContainer[Any] if TYPE_CHECKING else c.ListContainer]):
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


@attrs.define
class EventProxy:
    parent: EventProxy | None = None
    events: list[AnyEvent] = attrs.field(factory=list)


AnyEvent: TypeAlias = Event[Any]
