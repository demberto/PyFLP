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

import abc
import enum
from typing import Any, Iterable, Optional, TypeVar

import colour

from pyflp._utils import isascii


class _Validator(abc.ABC):
    """Base class of all validator classes."""

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"

    @abc.abstractmethod
    def validate(self, value: Any):
        pass


_ValidatorType = TypeVar("_ValidatorType", bound=_Validator)


class _OneOfValidator(_Validator):
    """Validates whether a value exists in a given set of options."""

    def __init__(self, options: Iterable[Any]):
        self.__options = options

    def __repr__(self) -> str:
        return f"<{type(self).__name__} options={self.__options!r}>"

    def validate(self, value: Any):
        if value not in self.__options:
            raise ValueError(f"Expected {value!r} to be one of {self.__options!r}")


class _BoolValidator(_OneOfValidator):
    """Validates whether a value equals `True` or `False`."""

    def __init__(self) -> None:
        super().__init__((True, False))

    def __repr__(self) -> str:
        return "<BoolValidator>"

    def validate(self, value: Any) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"Expected {value!r} to be a bool")


class _EnumValidator(_OneOfValidator):
    """Validates whether a value exists in a particular `enum` class."""

    _Enum = TypeVar("_Enum", bound=enum.Enum)

    def __init__(self, enum: _Enum) -> None:
        self.__enum = enum
        super().__init__(tuple(enum))

    def __repr__(self) -> str:
        return f'<EnumValidator enum="{self.__enum.__name__}>"'

    def validate(self, value: Any) -> None:
        if issubclass(self.__enum, (enum.IntEnum, enum.IntFlag)):
            if not isinstance(value, int):
                raise TypeError(f"Expected {value!r} to be an int")
        return super().validate(value)


class _IntFloatValidatorBase(_Validator, abc.ABC):
    """Base class for `_IntValidator` and `_FloatValidator`."""

    def __init__(self, min_, max_) -> None:  # pragma: no cover
        self.__min = min_
        self.__max = max_

    def __repr__(self) -> str:
        return f"<{type(self).__name__} min={self.__min}, max={self.__max}>"


class _IntValidator(_IntFloatValidatorBase):
    """Validates whether value is an `int` and lies in a range, optionally."""

    def __init__(self, min_: Optional[int] = None, max_: Optional[int] = None):
        self.__min = min_
        self.__max = max_

    def validate(self, value: Any):
        if type(value) is not int:  # https://stackoverflow.com/a/37888668
            raise TypeError(f"Expected {value!r} to be an int")
        if self.__min is not None and value < self.__min:
            raise ValueError(f"Expected {value!r} to be at least {self.__min!r}")
        if self.__max is not None and value > self.__max:
            raise ValueError(f"Expected {value!r} to be no more than {self.__max!r}")


class _UIntValidator(_IntValidator):
    """A specialization of `_IntValidator` for validating positive integers."""

    def __init__(self, max_: Optional[int] = None) -> None:
        super().__init__(min_=0, max_=max_)


class _FloatValidator(_IntFloatValidatorBase):
    """Validates whether value is an `float` and lies in a range, optionally."""

    def __init__(
        self, min_: Optional[float] = None, max_: Optional[float] = None
    ) -> None:
        self.__min = min_
        self.__max = max_

    def validate(self, value: Any):
        if type(value) is not float:
            raise TypeError(f"Expected {value!r} to be a float")
        if self.__min is not None and value < self.__min:
            raise ValueError(f"Expected {value!r} to be at least {self.__min!r}")
        if self.__max is not None and value > self.__max:
            raise ValueError(f"Expected {value!r} to be no more than {self.__max!r}")


class _BytesStrValidatorBase(_Validator, abc.ABC):
    """Base class for `_BytesValidator` and `_StrValidator`."""

    def __init__(
        self, minsize: Optional[int] = None, maxsize: Optional[int] = None
    ) -> None:
        self.__minsize = minsize
        self.__maxsize = maxsize

    def __repr__(self) -> str:
        return f"<{type(self).__name__} min={self.__minsize}, max={self.__maxsize}>"

    def validate(self, value: Any):
        if self.__minsize is not None and len(value) < self.__minsize:
            raise ValueError(
                f"Expected {value!r} to be no smaller than {self.__minsize!r}"
            )
        if self.__maxsize is not None and len(value) > self.__maxsize:
            raise ValueError(
                f"Expected {value!r} to be no bigger than {self.__maxsize!r}"
            )


class _BytesValidator(_BytesStrValidatorBase):
    """Validates the type and size of a `bytes` object."""

    def validate(self, value: Any) -> None:
        if not isinstance(value, bytes):
            raise TypeError(f"Expected {value!r} to be a bytes object")
        super().validate(value)


class _StrValidator(_BytesStrValidatorBase):
    """Validates the type and size of an `str` object."""

    def __init__(
        self,
        minsize: Optional[int] = None,
        maxsize: Optional[int] = None,
        mustascii: bool = False,
    ) -> None:
        super().__init__(minsize, maxsize)
        self.__mustascii = mustascii

    def validate(self, value: Any):
        if not isinstance(value, str):
            raise TypeError(f"Expected {value!r} to be an str")
        if self.__mustascii and not isascii(value):
            raise TypeError(f"Expected {value!r} to be an ASCII string")
        super().validate(value)


class _ColorValidator(_Validator):
    """Validates whether the type of value is `colour.Color`."""

    def validate(self, value: Any) -> None:
        if not isinstance(value, colour.Color):
            raise TypeError(f"Expected {value!r} to be a 'colour.Color' object")
