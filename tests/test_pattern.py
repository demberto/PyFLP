from __future__ import annotations

import pytest

from pyflp.pattern import Pattern, Patterns


def test_patterns(patterns: Patterns):
    assert len(patterns) == 5
    assert patterns.current == patterns[5]
    assert patterns.play_cut_notes


@pytest.fixture(scope="session")
def pat_tuple(patterns: Patterns):
    return tuple(patterns)


def test_names(pat_tuple: tuple[Pattern, ...]):
    assert set(pattern.name for pattern in pat_tuple) == set(
        ("Default", "Colored", "MIDI", "Timemarkers", "Selected")
    )
