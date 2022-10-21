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

# pylint: disable=super-init-not-called

"""Contains the descriptor classes used by the model classes."""

from __future__ import annotations

import abc
import enum
import sys
from typing import Any, TypeVar, overload

if sys.version_info >= (3, 8):
    from typing import Protocol, final, runtime_checkable
else:
    from typing_extensions import Protocol, final, runtime_checkable

from ._events import AnyEvent, EventEnum, PODEventBase, StructEventBase
from ._models import EMT_co, EventModel, ItemModel, ModelBase
from .exceptions import PropertyCannotBeSet

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


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


class PropBase(abc.ABC, RWProperty[T]):
    def __init__(
        self, *ids: EventEnum, default: T | None = None, readonly: bool = False
    ):
        self._ids = ids
        self._default = default
        self._readonly = readonly

    @overload
    def _get_event(self, instance: ItemModel) -> ItemModel:
        ...

    @overload
    def _get_event(self, instance: EventModel) -> AnyEvent | None:
        ...

    def _get_event(self, instance: ModelBase):
        if isinstance(instance, ItemModel):
            return instance

        if isinstance(instance, EventModel):
            if not self._ids:
                return tuple(instance.events.all())[0]

            for id in self._ids:
                if id in instance.events:
                    return instance.events.first(id)

    @property
    def default(self) -> T | None:  # Configure version based defaults here
        return self._default

    @abc.abstractmethod
    def _get(self, ev_or_ins: Any) -> T | None:
        ...

    @abc.abstractmethod
    def _set(self, ev_or_ins: Any, value: T):
        ...

    @final
    def __get__(self, instance: Any, owner: Any = None) -> T | None:
        if owner is None:
            return NotImplemented

        event = self._get_event(instance)
        if event is not None:
            return self._get(event)

        return self.default

    @final
    def __set__(self, instance: Any, value: T):
        if self._readonly:
            raise PropertyCannotBeSet(*self._ids)

        event = self._get_event(instance)
        if event is not None:
            self._set(event, value)
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
    ):
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
        if isinstance(ev_or_ins, PODEventBase):
            flags = ev_or_ins.value  # type: ignore
        elif isinstance(ev_or_ins, (ItemModel, StructEventBase)):
            flags = ev_or_ins[self._prop]
        else:
            raise NotImplementedError  # should not happen, basically

        if flags is not None:
            retbool = self._flag in self._flag_type(flags)
            return not retbool if self._inverted else retbool

    def _set(self, ev_or_ins: Any, value: bool):
        if self._inverted:
            value = not value

        if isinstance(ev_or_ins, (ItemModel, StructEventBase)):
            if value:
                ev_or_ins[self._prop] |= self._flag
            else:
                ev_or_ins[self._prop] &= ~self._flag
        elif isinstance(ev_or_ins, PODEventBase):
            if value:
                ev_or_ins.value |= self._flag  # type: ignore
            else:
                ev_or_ins.value &= ~self._flag  # type: ignore


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


class EventProp(PropBase[T]):
    """Properties bound directly to one of fixed size or string events."""

    def _get(self, ev_or_ins: AnyEvent) -> T | None:
        return ev_or_ins.value

    def _set(self, ev_or_ins: AnyEvent, value: T):
        ev_or_ins.value = value


class NestedProp(ROProperty[EMT_co]):
    def __init__(self, type: type[EMT_co], *ids: EventEnum):
        self._ids = ids
        self._type = type

    def __get__(self, ins: EventModel, owner: Any = None) -> EMT_co:
        if owner is None:
            return NotImplemented

        return self._type(ins.events.subdict(lambda e: e.id in self._ids))


class StructProp(PropBase[T], NamedPropMixin):
    """Properties obtained from a :class:`construct.Struct`."""

    def __init__(self, *ids: EventEnum, prop: str | None = None, **kwds: Any):
        super().__init__(*ids, **kwds)
        NamedPropMixin.__init__(self, prop)

    def _get(self, ev_or_ins: Any) -> T | None:
        return ev_or_ins[self._prop]

    def _set(self, ev_or_ins: Any, value: T):
        ev_or_ins[self._prop] = value
