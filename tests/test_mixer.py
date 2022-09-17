from __future__ import annotations

import colour
import pytest

from pyflp.mixer import Insert, InsertDock, Mixer


def test_mixer(mixer: Mixer):
    assert len(mixer) == 127
    assert mixer.apdc
    assert mixer.max_inserts == 127
    assert mixer.max_slots == 10


@pytest.fixture(scope="session")
def inserts(mixer: Mixer):
    return tuple(mixer)[:25]


def test_insert_bypassed(inserts: tuple[Insert]):
    for insert in inserts:
        assert insert.bypassed if insert.name == "Bypassed" else not insert.bypassed


def test_insert_channels_swapped(inserts: tuple[Insert]):
    for insert in inserts:
        assert (
            insert.channels_swapped
            if insert.name == "Swap LR"
            else not insert.channels_swapped
        )


def test_insert_color(inserts: tuple[Insert]):
    for insert in inserts:
        if insert.name == "Colored":
            assert insert.color == colour.Color("#FF1414")
        elif insert.name in ("Audio track", "Instrument track"):
            assert insert.color == colour.Color("#485156")
        else:
            assert not insert.color


def test_insert_dock(inserts: tuple[Insert]):
    for insert in inserts:
        if insert.name in ("Docked left", "Master"):
            assert insert.dock == InsertDock.Left
        # fmt: off
        elif (
            insert.name == "Docked right" or
            insert.__index__() in (101, 102, 103, 104)
        ):
            # fmt: on
            assert insert.dock == InsertDock.Right
        else:
            assert insert.dock == InsertDock.Middle


def test_insert_name(inserts: tuple[Insert]):
    assert [insert.name for insert in inserts] == [
        "Master",
        "Audio track",
        "Instrument track",
        "Colored",
        "Zero Volume",
        "No routes",
        "100% L",
        "100% R",
        "Separator",
        "Locked",
        "Disabled",
        "Iconified",
        "100% mono",
        r"100% separated",
        "Swap LR",
        "Invert Polarity",
        "Docked left",
        "Docked right",
        "Bypassed",
        "Plugin Test",
        "Slot Check",
        "50ms track latency",
        "Armed",
        "Post EQ check",
        "50ms input latency",
    ]
