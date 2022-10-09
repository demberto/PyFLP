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

"""Contains the ABCs used by model classes."""

from __future__ import annotations

import abc
import collections
import dataclasses
from collections.abc import Hashable
from typing import Any, DefaultDict, TypeVar

from ._events import AnyEvent


class ModelBase(abc.ABC):
    def __init__(self, **kw: Any):
        self._kw = kw


class ItemModel(ModelBase):
    """Base class for event-less models."""

    def __init__(self, item: dict[str, Any], **kw: Any):
        self._item = item
        super().__init__(**kw)

    def __getitem__(self, prop: str):
        return self._item[prop]

    def __setitem__(self, prop: str, value: Any):
        self._item[prop] = value


class SingleEventModel(ModelBase):
    """Base class for models whose properties are derived from a single event."""

    def __init__(self, event: AnyEvent, **kw: Any):
        super().__init__(**kw)
        self._event = event

    def __eq__(self, o: object):
        if not isinstance(o, type(self)):
            raise TypeError(f"Cannot compare {type(o)!r} with {type(self)!r}")

        return o.event() == self.event()

    def event(self) -> AnyEvent:
        """Returns the underlying event used by the model.

        Tip:
            You almost never need to use this method and it is only provided
            to calm type checkers from complaining about protected access.
        """
        return self._event


class MultiEventModel(ModelBase):
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

    def events_astuple(self):
        """Returns a tuple of events used by the model in their original order."""
        return self._events_tuple

    def events_asdict(self):
        """Returns a dictionary of event ID to a list of events."""
        return self._events


class ModelReprMixin:
    """I am too lazy to make one `__repr__()` for every model."""

    def __repr__(self):
        mapping: dict[str, Any] = {}
        cls = type(self)
        # pylint: disable-next=bad-builtin
        for var in filter(lambda var: not var.startswith("_"), vars(cls)):
            # ! cannot import ROProperty due to circular import
            if hasattr(getattr(cls, var), "__get__"):
                mapping[var] = getattr(self, var, None)

        params = ", ".join([f"{k}={v!r}" for k, v in mapping.items()])
        return f"{cls.__name__} ({params})"


MT_co = TypeVar("MT_co", bound=ModelBase, covariant=True)
SEMT_co = TypeVar("SEMT_co", bound=SingleEventModel, covariant=True)


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
