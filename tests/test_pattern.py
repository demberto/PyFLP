from __future__ import annotations

from typing import Callable, Tuple

import colour
import pytest

from pyflp.pattern import Note, Pattern, PatternID, Patterns

from .conftest import ModelFixture

NotesFixture = Callable[[str], Tuple[Note, ...]]


def test_patterns(patterns: Patterns):
    assert len(patterns) == 5
    assert patterns.current == patterns[5]
    assert patterns.play_cut_notes


def test_pattern_color(patterns: Patterns):
    assert patterns[2].color == colour.Color("#00FF00")


def test_pattern_names(patterns: Patterns):
    assert set(pattern.name for pattern in patterns) == set(
        ("Default", "Colored", "MIDI", "Timemarkers", "Selected")
    )


@pytest.fixture
def get_notes(get_model: ModelFixture):
    def wrapper(score: str):
        return tuple(get_model(f"patterns/{score}", Pattern, *PatternID))

    return wrapper


def test_empty_pattern(get_notes: NotesFixture):
    assert not len(get_notes("empty.fsc"))


def test_note_color(get_notes: NotesFixture):
    assert get_notes("color-9.fsc")[0].midi_channel == 8


def test_note_fine_pitch(get_notes: NotesFixture):
    assert [n.fine_pitch for n in get_notes("fine-pitch-min-max.fsc")] == [0, 240]


def test_note_group(get_notes: NotesFixture):
    assert [n.group for n in get_notes("common-group.fsc")] == [1, 1]


def test_note_length(get_notes: NotesFixture):
    assert get_notes("c5-1bar.fsc")[0].length == 384


def test_note_mod_x(get_notes: NotesFixture):
    assert [n.mod_x for n in get_notes("modx-min-max.fsc")] == [255, 0]


def test_note_mod_y(get_notes: NotesFixture):
    assert [n.mod_y for n in get_notes("mody-min-max.fsc")] == [0, 255]


def test_note_key(get_notes: NotesFixture):
    c_major = ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]
    assert [n.key for n in get_notes("c-major-scale.fsc")] == c_major


def test_note_pan(get_notes: NotesFixture):
    assert [n.pan for n in get_notes("pan-min-max.fsc")] == [128, 0]


def test_note_position(get_notes: NotesFixture):
    notes = get_notes("c-major-scale.fsc")
    assert [n.position for n in notes] == [x * 384 for x in range(8)]


def test_note_rack_channel(get_notes: NotesFixture):
    assert set(n.rack_channel for n in get_notes("multi-channel.flp")) == set((0, 1))


def test_note_release(get_notes: NotesFixture):
    assert [n.release for n in get_notes("release-min-max.fsc")] == [0, 128]


def test_note_slide(get_notes: NotesFixture):
    assert get_notes("slide-note.fsc")[0].slide


def test_note_velocity(get_notes: NotesFixture):
    assert [n.velocity for n in get_notes("velocity-min-max.fsc")] == [0, 128]
