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

"""Contains the descriptor and adaptor classes used by models and events."""

from __future__ import annotations

import abc
import enum
from collections.abc import Iterable
from typing import Any, Generic, TypeVar, overload

import attrs
import construct as c
from typing_extensions import Self, final

from pyflp._events import AnyEvent, EventEnum, EventProxy

_T = TypeVar("_T")
_EPT = TypeVar("_EPT", bound=EventProxy)


@attrs.define
class NamedPropMixin:
    prop: str = ""

    def __set_name__(self, _: Any, name: str) -> None:
        if not self.prop:
            self.prop = name


@attrs.define(kw_only=True)
class PropBase(abc.ABC, Generic[_T]):
    ids: Iterable[EventEnum]
    default: _T | None = None

    def _get_event(self, ins: EventProxy) -> AnyEvent | None:
        # if not self._ids:
        #     if len(ins.events) > 1:  # Prevent ambiguous situations
        #         raise LookupError("Event ID not specified")

        #     return tuple(ins.events)[0]
        return next((e for e in ins.events if e.id in self.ids), None)

    @abc.abstractmethod
    def _get(self, event: AnyEvent) -> _T | None:
        ...

    @abc.abstractmethod
    def _set(self, event: AnyEvent, value: _T) -> None:
        ...

    @overload
    def __get__(self, obj: None, objtype: Any = None) -> Self:
        ...

    @overload
    def __get__(self, obj: EventProxy, objtype: Any = None) -> _T | None:
        ...

    @final
    def __get__(self, obj: EventProxy | None, objtype: Any = None) -> _T | Self | None:
        if obj is None:
            return self

        event = self._get_event(obj)
        if event is not None:
            return self._get(event)

        return self.default

    @final
    def __set__(self, obj: EventProxy, value: _T) -> None:
        # if self.readonly:
        #     raise AttributeError("Cannot set the value of a read-only property")
        event = self._get_event(obj)
        if event is not None:
            self._set(event, value)
        else:
            raise LookupError(f"No matching event from {self.ids!r} found")


@attrs.define(kw_only=True)
class FlagProp(PropBase[bool]):
    """Properties derived from enum bitflags.

    Args:
        flag: The flag which is to be checked for.
        prop: The dict key which contains the flags in a `Struct`.
        inverted: If this is true, property getter and setters
                    invert the value to be set / returned.
    """

    flag: enum.IntFlag
    prop: str = "flags"
    inverted: bool = False

    def _get(self, event: AnyEvent) -> bool | None:
        if isinstance(event.struct, c.Struct):
            flags = event.value[self.prop]
        else:
            flags = event.value

        if flags is not None:
            type_ = type(self.flag)
            retbool = self.flag in type_(flags)
            return not retbool if self.inverted else retbool

    def _set(self, event: AnyEvent, value: bool) -> None:
        if self.inverted:
            value = not value

        if isinstance(event.struct, c.Struct):
            if value:
                event.value[self.prop] |= self.flag
            else:
                event.value[self.prop] &= ~self.flag
        else:
            if value:
                event.value |= self.flag
            else:
                event.value &= ~self.flag


@attrs.define(kw_only=True)
class EventProp(PropBase[_T]):
    """Properties bound directly to one of fixed size or string events."""

    def _get(self, event: AnyEvent) -> _T | None:
        return event.value

    def _set(self, event: AnyEvent, value: _T) -> None:
        event.value = value


@attrs.define(kw_only=True)
class StructProp(PropBase[_T], NamedPropMixin):
    """Properties obtained from a :class:`construct.Struct`."""

    prop: str = ""

    def __attrs_pre_init__(self) -> None:
        NamedPropMixin.__init__(self, self.prop)

    def _get(self, event: AnyEvent) -> _T | None:
        return event.value[self.prop]

    def _set(self, event: AnyEvent, value: _T) -> None:
        event.value[self.prop] = value


@attrs.define
class NestedProp(Generic[_EPT]):
    cls: type[_EPT]
    ids: Iterable[EventEnum] = attrs.field(kw_only=True)

    @overload
    def __get__(self, obj: None, objtype: Any = None) -> Self:
        ...

    @overload
    def __get__(self, obj: EventProxy, objtype: Any = None) -> _EPT | None:
        ...

    @final
    def __get__(self, obj: EventProxy | None, objtype: Any = None) -> _EPT | Self | None:
        if obj is None:
            return self

        events = [e for e in obj.events if e.id in self.ids]
        return self.cls(obj, events)
