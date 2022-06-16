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

"""Tests classes from `pyflp.event` module."""

import pytest
from colour import Color

from pyflp._event import _DWordEvent
from pyflp.constants import BYTE, DATA, DWORD, TEXT, WORD


def test_equality(byteevent, wordevent):
    assert byteevent(BYTE, b"\x00") == byteevent(BYTE, b"\x00")
    with pytest.raises(TypeError):
        byteevent(BYTE, b"\x00") == wordevent(WORD, b"\x00")


def test_inequality(byteevent, wordevent):
    assert byteevent(BYTE, b"\x00") != byteevent(BYTE, b"\xFF")
    with pytest.raises(TypeError):
        byteevent(BYTE, b"\x00") != wordevent(WORD, b"\xFF")


def test_byte_event(byteevent, wordevent):
    with pytest.raises(ValueError):
        e = byteevent(WORD, b"\x00")
    with pytest.raises(TypeError):
        e = byteevent(BYTE, b"")
    e = byteevent(BYTE, b"\x00")
    assert not e.to_bool()
    assert e.to_int8() == e.to_uint8()
    assert e.size == 2
    assert e == byteevent(BYTE, b"\x00")
    for data in (b"\x01", 1, True):
        e.dump(data)
        assert e.to_bool()
    with pytest.raises(ValueError):
        e.dump(b"")
    for overflow in (-256, 256):
        with pytest.raises(OverflowError):
            e.dump(overflow)
    with pytest.raises(TypeError):
        e.dump("s")
    assert e != byteevent(BYTE, b"\xFF")
    w = wordevent(WORD, b"\x00\x00")
    with pytest.raises(TypeError):
        e == w
    with pytest.raises(TypeError):
        e != w
    e.dump(True)
    assert e.to_bool()


def test_word_event(wordevent):
    with pytest.raises(ValueError):
        e = wordevent(DWORD, b"\x00")
    with pytest.raises(TypeError):
        e = wordevent(WORD, b"")
    e = wordevent(WORD, b"\x00\x00")
    assert e.size == 3
    assert e == wordevent(WORD, b"\x00\x00")
    for data in (b"\x00\x00", 0):
        e.dump(data)
        assert e.to_int16() == e.to_uint16()
    with pytest.raises(ValueError):
        e.dump(b"")
    with pytest.raises(OverflowError):
        e.dump(-65536)
    with pytest.raises(OverflowError):
        e.dump(65536)
    with pytest.raises(TypeError):
        e.dump("s")
    assert e != wordevent(WORD, b"\x00\x01")


def test_dword_event(dwordevent):
    with pytest.raises(ValueError):
        e = dwordevent(TEXT, b"\x00\x00\x00\x00")
    with pytest.raises(TypeError):
        e = dwordevent(DWORD, b"")
    e = dwordevent(DWORD, b"\x00\x00\x00\x00")
    assert e.size == 5
    assert e == dwordevent(DWORD, b"\x00\x00\x00\x00")
    for data in (b"\x00\x00\x00\x00", 0):
        e.dump(data)
        assert e.to_int32() == e.to_uint32()
    with pytest.raises(ValueError):
        e.dump(b"")
    with pytest.raises(OverflowError):
        e.dump(_DWordEvent.INT_MIN - 1)
    with pytest.raises(OverflowError):
        e.dump(_DWordEvent.DWORD_MAX + 1)
    with pytest.raises(TypeError):
        e.dump("s")
    assert e != dwordevent(DWORD, b"\x00\x00\x00\x01")


def test_text_event(textevent):
    with pytest.raises(ValueError):
        e = textevent(DATA, b"t\x00e\x00x\x00t\x00\0", True)
    with pytest.raises(TypeError):
        e = textevent(TEXT, "string")
    e = textevent(TEXT, b"t\x00e\x00x\x00t\x00\0", True)
    s = e.size
    assert s == 11
    assert e.to_str() == "text"
    ascii_event = textevent(TEXT, b"more", False)
    assert ascii_event.size == 6
    with pytest.raises(TypeError):
        ascii_event.dump(0)


def test_data_event(dataevent):
    with pytest.raises(ValueError):
        e = dataevent(BYTE, b"data")
    with pytest.raises(TypeError):
        e = dataevent(DATA, 0)
    e = dataevent(DATA, b"data")
    assert e.size == 6
    e.dump(b"moredata")
    with pytest.raises(TypeError):
        e.dump("s")
    assert e.size == 10


def test_color_event(colorevent):
    e = colorevent(128, b"\x48\x51\x56\x00")
    assert e.to_color() == Color("#485156")
    with pytest.raises(TypeError):
        e.dump(0)
    assert e.size == 5
    e.dump(Color("red"))
