from __future__ import annotations

import colour

from pyflp.pattern import Pattern, PatternID, Patterns

from .conftest import get_model


def get_notes(score: str):
    return tuple(get_model(f"patterns/{score}", Pattern, *PatternID).notes)


def test_patterns(patterns: Patterns):
    assert len(patterns) == 5
    assert patterns.current == patterns[4]
    assert patterns.play_cut_notes


def test_pattern_color(patterns: Patterns):
    assert patterns[2].color == colour.Color("#00FF00")


def test_pattern_names(patterns: Patterns):
    assert set(pattern.name for pattern in patterns) == set(
        ("Default", "Colored", "MIDI", "Timemarkers", "Selected")
    )


def test_pattern_timemarkers(patterns: Patterns):
    assert len(tuple(patterns["Timemarkers"].timemarkers)) == 5


def test_empty_pattern():
    assert not len(get_notes("empty.fsc"))


def test_note_color():
    assert get_notes("color-9.fsc")[0].midi_channel == 8


def test_note_fine_pitch():
    assert [n.fine_pitch for n in get_notes("fine-pitch-min-max.fsc")] == [0, 240]


def test_note_group():
    assert [n.group for n in get_notes("common-group.fsc")] == [1, 1]


def test_note_length():
    assert get_notes("c5-1bar.fsc")[0].length == 384


def test_note_mod_x():
    assert [n.mod_x for n in get_notes("modx-min-max.fsc")] == [255, 0]


def test_note_mod_y():
    assert [n.mod_y for n in get_notes("mody-min-max.fsc")] == [0, 255]


def test_note_key():
    c_major = ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]
    assert [n.key for n in get_notes("c-major-scale.fsc")] == c_major


def test_note_pan():
    assert [n.pan for n in get_notes("pan-min-max.fsc")] == [128, 0]


def test_note_position():
    notes = get_notes("c-major-scale.fsc")
    assert [n.position for n in notes] == [x * 384 for x in range(8)]


def test_note_rack_channel():
    assert set(n.rack_channel for n in get_notes("multi-channel.flp")) == set((0, 1))


def test_note_release():
    assert [n.release for n in get_notes("release-min-max.fsc")] == [0, 128]


def test_note_slide():
    assert get_notes("slide-note.fsc")[0].slide


def test_note_velocity():
    assert [n.velocity for n in get_notes("velocity-min-max.fsc")] == [0, 128]
