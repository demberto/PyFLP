# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2023 demberto
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

from __future__ import annotations

import enum
from collections import UserDict, UserList
from dataclasses import dataclass
from typing import Any, NamedTuple, TypeVar, Union, TYPE_CHECKING

import construct
import construct_typed as ct
from typing_extensions import ParamSpec, TypeAlias

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
ET = TypeVar("ET", bound=Union[ct.EnumBase, enum.IntFlag])
T_co = TypeVar("T_co", covariant=True)


@dataclass(frozen=True, order=True)
class FLVersion:
    major: int
    minor: int = 0
    patch: int = 0
    build: int | None = None

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.build is not None:
            return f"{version}.{self.build}"
        return version


class MusicalTime(NamedTuple):
    bars: int
    """1 bar == 16 beats == 768 (internal representation)."""

    beats: int
    """1 beat == 240 ticks == 48 (internal representation)."""

    ticks: int
    """5 ticks == 1 (internal representation)."""


class RGBA(NamedTuple):
    red: float
    green: float
    blue: float
    alpha: float

    @staticmethod
    def from_bytes(buf: bytes) -> RGBA:
        return RGBA(*(c / 255 for c in buf))

    def __bytes__(self) -> bytes:
        return bytes(round(c * 255) for c in self)


if TYPE_CHECKING:
    AnyContainer: TypeAlias = construct.Container[Any]
    AnyListContainer: TypeAlias = construct.ListContainer[Any]
    AnyDict: TypeAlias = UserDict[str, Any]
    AnyList: TypeAlias = UserList[AnyContainer]
else:
    AnyContainer = construct.Container
    AnyListContainer = construct.ListContainer
    AnyDict = UserDict
    AnyList = UserList
