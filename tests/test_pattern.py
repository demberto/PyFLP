from __future__ import annotations

from itertools import chain

import pytest

from pyflp.pattern import Note, Patterns


def test_patterns(patterns: Patterns):
    assert len(patterns) == 5
    assert patterns.current == patterns[5]
    assert patterns.play_cut_notes


def test_names(patterns: Patterns):
    assert set(pattern.name for pattern in patterns) == set(
        ("Default", "Colored", "MIDI", "Timemarkers", "Selected")
    )


@pytest.fixture(scope="session")
def notes(patterns: Patterns):
    return tuple(patterns[3])


def test_note_fine_pitch(notes: tuple[Note, ...]):
    # fmt: off
    assert [n.fine_pitch for n in filter(lambda n: n.rack_channel == 4, notes)] == [240, 0] * 2
    assert [n.fine_pitch for n in filter(lambda n: n.rack_channel != 4, notes)] == [120] * 44
    # fmt: on


def test_note_length(notes: tuple[Note, ...]):
    assert list(filter(lambda l: l != 0, (n.length for n in notes))) == [24] * 4


def test_note_mod_x(notes: tuple[Note, ...]):
    # fmt: off
    assert [n.mod_x for n in filter(lambda n: n.rack_channel == 9, notes)] == [0, 255] * 2
    assert [n.mod_x for n in filter(lambda n: n.rack_channel != 9, notes)] == [128] * 44
    # fmt: on


def test_note_mod_y(notes: tuple[Note, ...]):
    # fmt: off
    assert [n.mod_y for n in filter(lambda n: n.rack_channel == 10, notes)] == [0, 255] * 2
    assert [n.mod_y for n in filter(lambda n: n.rack_channel != 10, notes)] == [128] * 44
    # fmt: on


def test_note_pan(notes: tuple[Note, ...]):
    # fmt: off
    assert [n.pan for n in filter(lambda n: n.rack_channel == 2, notes)] == [128, 0] * 2
    assert [n.pan for n in filter(lambda n: n.rack_channel != 2, notes)] == [64] * 44
    # fmt: on


def test_note_position(notes: tuple[Note, ...]):
    assert [n.position for n in notes] == [x * 24 for x in range(16) for _ in range(3)]


def test_note_rack_channel(notes: tuple[Note, ...]):
    assert [n.rack_channel for n in notes] == list(
        chain.from_iterable([(x + 8, x + 4, x) for x in range(1, 5) for _ in range(4)])
    )  # [9, 5, 1] * 4 + [10, 6, 2] * 4 + [11, 7, 3] * 4 + [12, 8, 4] * 4


def test_note_release(notes: tuple[Note, ...]):
    # fmt: off
    assert [n.release for n in filter(lambda n: n.rack_channel == 3, notes)] == [128, 0] * 2
    assert [n.release for n in filter(lambda n: n.rack_channel != 3, notes)] == [64] * 44
    # fmt: on


def test_notes(patterns: Patterns):
    for pattern in patterns:
        notes = tuple(pattern)
        if pattern.index == 3:
            assert len(notes) == 48
            assert set(n.key for n in notes) == set([60])
