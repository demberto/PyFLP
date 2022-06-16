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
from typing import TYPE_CHECKING, Generic, NoReturn, Optional, TypeVar

import colour

from pyflp._validators import (
    _BoolValidator,
    _BytesValidator,
    _ColorValidator,
    _EnumValidator,
    _FloatValidator,
    _IntValidator,
    _StrValidator,
    _UIntValidator,
)
from pyflp.exceptions import OperationNotPermittedError

if TYPE_CHECKING:
    from pyflp._flobject import _FLObjectType
    from pyflp._validators import _ValidatorType

_T = TypeVar("_T")


class _Property(abc.ABC, Generic[_T]):
    """Base class for property descriptors used in `FLObject` subclasses.

    https://stackoverflow.com/a/69599069"""

    def __init__(self, validator: "_ValidatorType") -> None:
        self.__validator = validator

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} "
            f'name="{self.__public_name}", '
            f'validator="{repr(self.__validator)}">'
        )

    def __set_name__(self, _, name: str) -> None:
        self.__public_name = name
        self.__private_name = "_" + name

    def __get__(self, obj: "_FLObjectType", _=None) -> Optional[_T]:
        if obj is None:
            return self
        return getattr(obj, self.__private_name, None)

    def __delete__(self, obj) -> NoReturn:
        raise OperationNotPermittedError("Properties cannot be deleted", obj)

    def __set__(self, obj: "_FLObjectType", value) -> None:
        self.__validator.validate(value)
        setattr(obj, self.__private_name, value)

        # This allows for overriding setter logic in _FLObject
        # subclass while still allowing to use these descriptors
        obj._setprop(self.__public_name, value)


class _BoolProperty(_Property[bool]):
    def __init__(self) -> None:
        super().__init__(_BoolValidator())


class _BytesProperty(_Property[bytes]):
    def __init__(self, validator: Optional[_BytesValidator] = None, **kwargs) -> None:
        if validator is None:
            validator = _BytesValidator(**kwargs)
        super().__init__(validator)


class _ColorProperty(_Property[colour.Color]):
    def __init__(self) -> None:
        super().__init__(_ColorValidator())


_Enum = TypeVar("_Enum", bound=enum.Enum)


class _EnumProperty(_Property[_Enum]):
    def __init__(self, enum: _Enum) -> None:
        super().__init__(_EnumValidator(enum))


class _FloatProperty(_Property[float]):
    def __init__(self, validator: Optional[_FloatValidator] = None, **kwargs) -> None:
        if validator is None:
            validator = _FloatValidator(**kwargs)
        super().__init__(validator)


class _IntProperty(_Property[int]):
    def __init__(self, validator: Optional[_IntValidator] = None, **kwargs) -> None:
        if validator is None:
            validator = _IntValidator(**kwargs)
        super().__init__(validator)


class _StrProperty(_Property[str]):
    def __init__(self, validator: Optional[_StrValidator] = None, **kwargs) -> None:
        if validator is None:
            validator = _StrValidator(**kwargs)
        super().__init__(validator)


class _UIntProperty(_Property[int]):
    def __init__(self, validator: Optional[_UIntValidator] = None, **kwargs) -> None:
        if validator is None:
            validator = _UIntValidator(**kwargs)
        super().__init__(validator)
