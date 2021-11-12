import pytest
from colour import Color

from pyflp.constants import BYTE, DATA, DWORD, TEXT, WORD
from pyflp.event import (
    ByteEvent,
    ColorEvent,
    DataEvent,
    DWordEvent,
    TextEvent,
    WordEvent,
)


def test_equality():
    assert ByteEvent(BYTE, b"\x00") == ByteEvent(BYTE, b"\x00")
    with pytest.raises(TypeError):
        ByteEvent(BYTE, b"\x00") == WordEvent(WORD, b"\x00")


def test_inequality():
    assert ByteEvent(BYTE, b"\x00") != ByteEvent(BYTE, b"\xFF")
    with pytest.raises(TypeError):
        ByteEvent(BYTE, b"\x00") != WordEvent(WORD, b"\xFF")


def test_byte_event():
    with pytest.raises(ValueError):
        e = ByteEvent(WORD, b"\x00")
    with pytest.raises(TypeError):
        e = ByteEvent(BYTE, b"")
    e = ByteEvent(BYTE, b"\x00")
    assert not e.to_bool()
    assert e.to_int8() == e.to_uint8()
    assert e.size == 2
    assert e == ByteEvent(BYTE, b"\x00")
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
    assert e != ByteEvent(BYTE, b"\xFF")
    w = WordEvent(WORD, b"\x00\x00")
    with pytest.raises(TypeError):
        e == w
    with pytest.raises(TypeError):
        e != w


def test_word_event():
    with pytest.raises(ValueError):
        e = WordEvent(DWORD, b"\x00")
    with pytest.raises(TypeError):
        e = WordEvent(WORD, b"")
    e = WordEvent(WORD, b"\x00\x00")
    assert e.size == 3
    assert e == WordEvent(WORD, b"\x00\x00")
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
    assert e != WordEvent(WORD, b"\x00\x01")


def test_dword_event():
    with pytest.raises(ValueError):
        e = DWordEvent(TEXT, b"\x00\x00\x00\x00")
    with pytest.raises(TypeError):
        e = DWordEvent(DWORD, b"")
    e = DWordEvent(DWORD, b"\x00\x00\x00\x00")
    assert e.size == 5
    assert e == DWordEvent(DWORD, b"\x00\x00\x00\x00")
    for data in (b"\x00\x00\x00\x00", 0):
        e.dump(data)
        assert e.to_int32() == e.to_uint32()
    with pytest.raises(ValueError):
        e.dump(b"")
    with pytest.raises(OverflowError):
        e.dump(DWordEvent.INT_MIN - 1)
    with pytest.raises(OverflowError):
        e.dump(DWordEvent.DWORD_MAX + 1)
    with pytest.raises(TypeError):
        e.dump("s")
    assert e != DWordEvent(DWORD, b"\x00\x00\x00\x01")


def test_text_event():
    with pytest.raises(ValueError):
        e = TextEvent(DATA, b"t\x00e\x00x\x00t\x00\0")
    with pytest.raises(TypeError):
        e = TextEvent(TEXT, "string")
    e = TextEvent(TEXT, b"t\x00e\x00x\x00t\x00\0")
    s = e.size
    assert s == 11
    assert e.to_str() == "text"
    TextEvent.uses_unicode = False
    e.dump("more")
    assert e.size == 7
    with pytest.raises(TypeError):
        e.dump(0)

    # ! All future tests fail without this
    TextEvent.uses_unicode = True


def test_data_event():
    with pytest.raises(ValueError):
        e = DataEvent(BYTE, b"data")
    with pytest.raises(TypeError):
        e = DataEvent(DATA, 0)
    e = DataEvent(DATA, b"data")
    assert e.size == 6
    e.dump(b"moredata")
    with pytest.raises(TypeError):
        e.dump("s")
    assert e.size == 10


def test_color_event():
    e = ColorEvent(128, b"\x48\x51\x56\x00")
    assert e.to_color() == Color("#485156")
    with pytest.raises(TypeError):
        e.dump(0)
    assert e.size == 5
    e.dump(Color("red"))
