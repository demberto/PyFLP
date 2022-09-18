from __future__ import annotations

from pyflp.pattern import Patterns


def test_patterns(patterns: Patterns):
    assert len(patterns) == 5
    assert patterns.current == patterns[5]
    assert patterns.play_cut_notes


def test_names(patterns: Patterns):
    assert set(pattern.name for pattern in patterns) == set(
        ("Default", "Colored", "MIDI", "Timemarkers", "Selected")
    )


def test_notes(patterns: Patterns):
    for pattern in patterns:
        notes = tuple(pattern.notes)
        assert len(notes) == 32 if pattern.index == 3 else not notes
