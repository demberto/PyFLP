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

import enum

import colour
import pytest

from pyflp._validators import (
    _BoolValidator,
    _BytesValidator,
    _ColorValidator,
    _EnumValidator,
    _FloatValidator,
    _StrValidator,
    _UIntValidator,
)


def test_bool_validator():
    v = _BoolValidator()
    for value in ("", 0, 0.0, None):
        with pytest.raises(TypeError):
            v.validate(value)


def test_bytes_validator():
    v = _BytesValidator(minsize=1, maxsize=1)
    for value in (0, None, True, 0.0, ""):
        with pytest.raises(TypeError):
            v.validate(value)
    for value in (b"", b"ab"):
        with pytest.raises(ValueError):
            v.validate(value)


def test_color_validator():
    v = _ColorValidator()
    v.validate(colour.Color())
    for value in (0, None, True, 0.0, ""):
        with pytest.raises(TypeError):
            v.validate(value)


def test_enum_validator():
    class Switch(enum.IntEnum):
        OFF = 0
        ON = 1

    class Alphabet(enum.Enum):
        A = "a"
        B = "b"

    v = _EnumValidator(Switch)
    for value in (None, "", 0.0):
        with pytest.raises(TypeError):
            v.validate(value)
    with pytest.raises(ValueError):
        v.validate(-1)
    a = _EnumValidator(Alphabet)
    with pytest.raises(ValueError):
        a.validate("c")


def test_float_validator():
    v = _FloatValidator(0.0, 1.0)
    for value in (0, "", None, True):
        with pytest.raises(TypeError):
            v.validate(value)
    for value in (2.0, -1.0):
        with pytest.raises(ValueError):
            v.validate(value)


def test_str_validator():
    v = _StrValidator(minsize=1, maxsize=1, mustascii=True)
    for value in (0, True, None, 0.0, "❗"):
        with pytest.raises(TypeError):
            v.validate(value)
    for value in ("", "ab"):
        with pytest.raises(ValueError):
            v.validate(value)


def test_uint_validator():
    v = _UIntValidator(max_=1)
    for value in (0.0, "", None, True):
        with pytest.raises(TypeError):
            v.validate(value)
    for value in (2, -1):
        with pytest.raises(ValueError):
            v.validate(value)
