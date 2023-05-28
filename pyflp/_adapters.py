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

import math
import warnings
from typing import Any, List, Tuple

import construct as c
import construct_typed as ct
from typing_extensions import TypeAlias

from pyflp.types import ET, MusicalTime, T, U

SimpleAdapter: TypeAlias = ct.Adapter[T, T, U, U]
"""Duplicates type parameters for `construct.Adapter`."""

FourByteBool: c.ExprAdapter[int, int, bool, int] = c.ExprAdapter(
    c.Int32ul, lambda obj_, *_: bool(obj_), lambda obj_, *_: int(obj_)  # type: ignore
)


class List2Tuple(SimpleAdapter[Any, Tuple[int, int]]):
    def _decode(self, obj: c.ListContainer[int], *_: Any) -> tuple[int, int]:
        _1, _2 = tuple(obj)
        return _1, _2

    def _encode(self, obj: tuple[int, int], *_: Any) -> c.ListContainer[int]:
        return c.ListContainer([*obj])


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


class StdEnum(SimpleAdapter[int, ET]):
    def _encode(self, obj: ET, *_: Any) -> int:
        return obj.value

    def _decode(self, obj: int, *_: Any) -> ET:
        return self.__orig_class__.__args__[0](obj)  # type: ignore
