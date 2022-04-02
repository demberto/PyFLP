"""Tests classes from `pyflp.event` module."""

import pytest
from colour import Color

from pyflp._event import (
    _ByteEvent,
    _ColorEvent,
    _DataEvent,
    _DWordEvent,
    _TextEvent,
    _WordEvent,
)
from pyflp.constants import BYTE, DATA, DWORD, TEXT, WORD


def test_equality():
    assert _ByteEvent(BYTE, b"\x00") == _ByteEvent(BYTE, b"\x00")
    with pytest.raises(TypeError):
        _ByteEvent(BYTE, b"\x00") == _WordEvent(WORD, b"\x00")


def test_inequality():
    assert _ByteEvent(BYTE, b"\x00") != _ByteEvent(BYTE, b"\xFF")
    with pytest.raises(TypeError):
        _ByteEvent(BYTE, b"\x00") != _WordEvent(WORD, b"\xFF")


def test_byte_event():
    with pytest.raises(ValueError):
        e = _ByteEvent(WORD, b"\x00")
    with pytest.raises(TypeError):
        e = _ByteEvent(BYTE, b"")
    e = _ByteEvent(BYTE, b"\x00")
    assert not e.to_bool()
    assert e.to_int8() == e.to_uint8()
    assert e.size == 2
    assert e == _ByteEvent(BYTE, b"\x00")
    for data in (b"\x01", 1, True):
        e.dump(data)
        assert e.to_bool()
    with pytest.raises(ValueError):
        e.dump(b"")
    with pytest.raises(OverflowError):
        e.dump(-256)
    with pytest.raises(OverflowError):
        e.dump(256)
    with pytest.raises(TypeError):
        e.dump("s")
    assert e != _ByteEvent(BYTE, b"\xFF")
    w = _WordEvent(WORD, b"\x00\x00")
    with pytest.raises(TypeError):
        e == w
    with pytest.raises(TypeError):
        e != w


def test_word_event():
    with pytest.raises(ValueError):
        e = _WordEvent(DWORD, b"\x00")
    with pytest.raises(TypeError):
        e = _WordEvent(WORD, b"")
    e = _WordEvent(WORD, b"\x00\x00")
    assert e.size == 3
    assert e == _WordEvent(WORD, b"\x00\x00")
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
    assert e != _WordEvent(WORD, b"\x00\x01")


def test_dword_event():
    with pytest.raises(ValueError):
        e = _DWordEvent(TEXT, b"\x00\x00\x00\x00")
    with pytest.raises(TypeError):
        e = _DWordEvent(DWORD, b"")
    e = _DWordEvent(DWORD, b"\x00\x00\x00\x00")
    assert e.size == 5
    assert e == _DWordEvent(DWORD, b"\x00\x00\x00\x00")
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
    assert e != _DWordEvent(DWORD, b"\x00\x00\x00\x01")


def test_text_event():
    with pytest.raises(ValueError):
        e = _TextEvent(DATA, b"t\x00e\x00x\x00t\x00\0")
    with pytest.raises(TypeError):
        e = _TextEvent(TEXT, "string")
    e = _TextEvent(TEXT, b"t\x00e\x00x\x00t\x00\0")
    s = e.size
    assert s == 11
    assert e.to_str() == "text"
    _TextEvent.uses_unicode = False
    e.dump("more")
    assert e.size == 7
    with pytest.raises(TypeError):
        e.dump(0)

    # ! All future tests fail without this
    _TextEvent.uses_unicode = True


def test_data_event():
    with pytest.raises(ValueError):
        e = _DataEvent(BYTE, b"data")
    with pytest.raises(TypeError):
        e = _DataEvent(DATA, 0)
    e = _DataEvent(DATA, b"data")
    assert e.size == 6
    e.dump(b"moredata")
    with pytest.raises(TypeError):
        e.dump("s")
    assert e.size == 10


def test_color_event():
    e = _ColorEvent(128, b"\x48\x51\x56\x00")
    assert e.to_color() == Color("#485156")
    with pytest.raises(TypeError):
        e.dump(0)
    assert e.size == 5
    e.dump(Color("red"))
