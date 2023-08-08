from __future__ import annotations

import pytest

from pyflp._events import AsciiAdapter, EventEnum, EventTree, U8Event, WORD


def test_id_out_of_range():
    with pytest.raises(ValueError, match=str(tuple(range(0, WORD)))):
        U8Event(EventEnum(128), b"\x00")

    with pytest.raises(ValueError):
        AsciiAdapter(EventEnum(0), b"1234-decode-me-baby")


def test_invalid_chunk_size():
    with pytest.raises(BufferError, match="1"):
        U8Event(EventEnum(0), b"12")


def test_event_tree():
    root = EventTree()
    child = EventTree(root)
    assert child in root.children
    event = U8Event(EventEnum(0), b"\x01")
    child.append(event)
    assert root.first(EventEnum(0)) == event
    child.remove(EventEnum(0))
    assert not root
