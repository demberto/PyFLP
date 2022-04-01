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
