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

from __future__ import annotations

import enum
import math
import warnings
from typing import Any, List, Union, NamedTuple, Tuple, TypeVar

import construct as c
from construct.core import Construct
import construct_typed as ct
from typing_extensions import TypeAlias

_T = TypeVar("_T")
_U = TypeVar("_U")
_EnumT = TypeVar("_EnumT", bound=Union[ct.EnumBase, enum.IntEnum, enum.IntFlag])

SimpleAdapter: TypeAlias = ct.Adapter[_T, _T, _U, _U]
"""Duplicates type parameters for `construct.Adapter`."""

FourByteBool: c.ExprAdapter[int, int, bool, int] = c.ExprAdapter(
    c.Int32ul, lambda obj_, *_: bool(obj_), lambda obj_, *_: int(obj_)  # type: ignore
)
U16TupleAdapter: SimpleAdapter[tuple[int], list[int]] = c.ExprAdapter(
    c.Int16ul[2],
    lambda obj_, *_: tuple(obj_),  # type: ignore
    lambda obj_, *_: list(obj_),  # type: ignore
)


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


ColorAdapter: SimpleAdapter[bytes, RGBA] = c.ExprAdapter(
    c.Bytes(4),
    lambda obj, *_: RGBA.from_bytes(obj),  # type: ignore
    lambda obj, *_: bytes(obj),  # type: ignore
)


def _make_str_adapter(encoding: str) -> SimpleAdapter[str, str]:
    return c.ExprAdapter(
        c.GreedyString(encoding),
        lambda obj, *_: obj.rstrip("\0"),  # type: ignore
        lambda obj, *_: obj + "\0",  # type: ignore
    )


AsciiAdapter = _make_str_adapter("ascii")
UnicodeAdapter = _make_str_adapter("utf-16-le")


class List2Tuple(SimpleAdapter[Any, Tuple[int, int]]):
    def _decode(self, obj: c.ListContainer[int], *_: Any) -> tuple[int, int]:
        _1, _2 = tuple(obj)
        return _1, _2

    def _encode(self, obj: tuple[int, int], *_: Any) -> c.ListContainer[int]:
        return c.ListContainer([*obj])


class MusicalTime(NamedTuple):
    bars: int
    """1 bar == 16 beats == 768 (internal representation)."""

    beats: int
    """1 beat == 240 ticks == 48 (internal representation)."""

    ticks: int
    """5 ticks == 1 (internal representation)."""


class LinearMusical(SimpleAdapter[int, MusicalTime]):
    def _encode(self, obj: MusicalTime, *_: Any) -> int:
        if obj.ticks % 5:
            warnings.warn("Ticks must be a multiple of 5", UserWarning)

        return (obj.bars * 768) + (obj.beats * 48) + int(obj.ticks * 0.2)

    def _decode(self, obj: int, *_: Any) -> MusicalTime:
        bars, remainder = divmod(obj, 768)
        beats, remainder = divmod(remainder, 48)
        return MusicalTime(bars, beats, ticks=remainder * 5)


class Log2(SimpleAdapter[int, float]):
    def __init__(self, subcon: Any, factor: int) -> None:
        super().__init__(subcon)  # type: ignore[call-arg]
        self.factor = factor

    def _encode(self, obj: float, *_: Any) -> int:
        return int(self.factor * math.log2(obj))

    def _decode(self, obj: int, *_: Any) -> float:
        return 2 ** (obj / self.factor)


# Thanks to @algmyr from Python Discord server for finding out the formulae used
# ! See https://github.com/construct/construct/issues/999
class LogNormal(SimpleAdapter[List[int], float]):
    def __init__(self, subcon: Any, bound: tuple[int, int]) -> None:
        super().__init__(subcon)  # type: ignore[call-arg]
        self.lo, self.hi = bound

    def _encode(self, obj: float, *_: Any) -> list[int]:
        """Clamps the integer representation of ``obj`` and returns it."""
        if not 0.0 <= obj <= 1.0:
            raise ValueError(f"Expected a value between 0.0 to 1.0; got {obj}")

        if not obj:  # log2(0.0) --> -inf ==> 0
            return [0, 0]

        return [min(max(self.lo, int(2**12 * (math.log2(obj) + 15))), self.hi), 63]

    def _decode(self, obj: list[int], *_: Any) -> float:
        """Returns a float representation of ``obj[0]`` between 0.0 to 1.0."""
        if not obj[0]:
            return 0.0

        if obj[1] != 63:
            raise ValueError(f"Not a LogNormal, 2nd int must be 63; not {obj[1]}")

        return max(min(1.0, 2 ** (obj[0] / 2**12) / 2**15), 0.0)


class StdEnum(SimpleAdapter[int, _EnumT]):
    def __init__(self, enumcls: type[_EnumT], subcon: Construct[int, int]) -> None:
        self._enum_cls = enumcls
        super().__init__(subcon)

    def _encode(self, obj: _EnumT, *_: Any) -> int:
        return obj.value

    def _decode(self, obj: int, *_: Any) -> _EnumT:
        return self._enum_cls(obj)
