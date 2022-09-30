from __future__ import annotations

import pytest

from pyflp._events import AsciiEvent, DataEventBase, U8Event
from pyflp.exceptions import EventIDOutOfRange, InvalidEventChunkSize


def test_id_out_of_range():
    with pytest.raises(EventIDOutOfRange, match="0-63"):
        U8Event(128, b"\x00")

    with pytest.raises(ValueError):
        AsciiEvent(0, b"1234-decode-me-baby")

    with pytest.raises(EventIDOutOfRange, match="208-255"):
        DataEventBase(0, b"")


def test_invalid_chunk_size():
    with pytest.raises(InvalidEventChunkSize, match="1"):
        U8Event(0, b"12")
