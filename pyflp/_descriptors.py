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
from typing import Any, Protocol, overload, runtime_checkable

from typing_extensions import Self, final

from pyflp._events import AnyEvent, EventEnum, StructEventBase
from pyflp._models import VE, EMT_co, EventModel, ItemModel, ModelBase
from pyflp.exceptions import PropertyCannotBeSet
from pyflp.types import T, T_co


@runtime_checkable
class ROProperty(Protocol[T_co]):
    """Protocol for a read-only descriptor."""

    def __get__(self, ins: Any, owner: Any = None) -> T_co | Self | None:
        ...


@runtime_checkable
class RWProperty(ROProperty[T], Protocol):
    """Protocol for a read-write descriptor."""

    def __set__(self, ins: Any, value: T) -> None:
        ...


class NamedPropMixin:
    def __init__(self, prop: str | None = None) -> None:
        self._prop = prop or ""

    def __set_name__(self, _: Any, name: str) -> None:
        if not self._prop:
            self._prop = name


class PropBase(abc.ABC, RWProperty[T]):
    def __init__(self, *ids: EventEnum, default: T | None = None, readonly: bool = False):
        self._ids = ids
        self._default = default
        self._readonly = readonly

    @overload
    def _get_event(self, ins: ItemModel[VE]) -> ItemModel[VE]:
        ...

    @overload
    def _get_event(self, ins: EventModel) -> AnyEvent | None:
        ...

    def _get_event(self, ins: ItemModel[VE] | EventModel):
        if isinstance(ins, ItemModel):
            return ins

        if not self._ids:
            if len(ins.events) > 1:  # Prevent ambiguous situations
                raise LookupError("Event ID not specified")

            return tuple(ins.events)[0]

        for id in self._ids:
            if id in ins.events:
                return ins.events.first(id)

    @property
    def default(self) -> T | None:  # Configure version based defaults here
        return self._default

    @abc.abstractmethod
    def _get(self, ev_or_ins: Any) -> T | None:
        ...

    @abc.abstractmethod
    def _set(self, ev_or_ins: Any, value: T) -> None:
        ...

    @final
    def __get__(self, ins: Any, owner: Any = None) -> T | Self | None:
        if ins is None:
            return self

        if owner is None:
            return NotImplemented

        event: Any = self._get_event(ins)
        if event is not None:
            return self._get(event)

        return self.default

    @final
    def __set__(self, ins: Any, value: T) -> None:
        if self._readonly:
            raise PropertyCannotBeSet(*self._ids)

        event: Any = self._get_event(ins)
        if event is not None:
            self._set(event, value)
        else:
            raise PropertyCannotBeSet(*self._ids)


class FlagProp(PropBase[bool]):
    """Properties derived from enum flags."""

    def __init__(
        self,
        flag: enum.IntFlag,
        *ids: EventEnum,
        prop: str = "flags",
        inverted: bool = False,
        default: bool | None = None,
    ) -> None:
        """
        Args:
            flag: The flag which is to be checked for.
            id: Event ID (required for MultiEventModel).
            prop: The dict key which contains the flags in a `Struct`.
            inverted: If this is true, property getter and setters
                      invert the value to be set / returned.
        """
        self._flag = flag
        self._flag_type = type(flag)
        self._prop = prop
        self._inverted = inverted
        super().__init__(*ids, default=default)

    def _get(self, ev_or_ins: Any) -> bool | None:
        if isinstance(ev_or_ins, (ItemModel, StructEventBase)):
            flags = ev_or_ins[self._prop]
        else:
            flags = ev_or_ins.value  # type: ignore

        if flags is not None:
            retbool = self._flag in self._flag_type(flags)
            return not retbool if self._inverted else retbool

    def _set(self, ev_or_ins: Any, value: bool) -> None:
        if self._inverted:
            value = not value

        if isinstance(ev_or_ins, (ItemModel, StructEventBase)):
            if value:
                ev_or_ins[self._prop] |= self._flag
            else:
                ev_or_ins[self._prop] &= ~self._flag
        else:
            if value:
                ev_or_ins.value |= self._flag  # type: ignore
            else:
                ev_or_ins.value &= ~self._flag  # type: ignore


class KWProp(NamedPropMixin, RWProperty[T]):
    """Properties derived from non-local event values.

    These values are passed to the class constructor as keyword arguments.
    """

    def __get__(self, ins: ModelBase | None, owner: Any = None) -> T | Self:
        if ins is None:
            return self

        if owner is None:
            return NotImplemented
        return ins._kw[self._prop]

    def __set__(self, ins: ModelBase, value: T) -> None:
        if self._prop not in ins._kw:
            raise KeyError(self._prop)
        ins._kw[self._prop] = value


class EventProp(PropBase[T]):
    """Properties bound directly to one of fixed size or string events."""

    def _get(self, ev_or_ins: AnyEvent) -> T | None:
        return ev_or_ins.value

    def _set(self, ev_or_ins: AnyEvent, value: T) -> None:
        ev_or_ins.value = value


class NestedProp(ROProperty[EMT_co]):
    def __init__(self, type: type[EMT_co], *ids: EventEnum) -> None:
        self._ids = ids
        self._type = type

    def __get__(self, ins: EventModel, owner: Any = None) -> EMT_co:
        if owner is None:
            return NotImplemented

        return self._type(ins.events.subtree(lambda e: e.id in self._ids))


class StructProp(PropBase[T], NamedPropMixin):
    """Properties obtained from a :class:`construct.Struct`."""

    def __init__(self, *ids: EventEnum, prop: str | None = None, **kwds: Any) -> None:
        super().__init__(*ids, **kwds)
        NamedPropMixin.__init__(self, prop)

    def _get(self, ev_or_ins: ItemModel[Any]) -> T | None:
        return ev_or_ins[self._prop]

    def _set(self, ev_or_ins: ItemModel[Any], value: T) -> None:
        ev_or_ins[self._prop] = value
