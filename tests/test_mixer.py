from __future__ import annotations

from typing import cast

import colour

from pyflp.mixer import Insert, InsertDock, Mixer, MixerID, MixerParamsEvent

from .conftest import get_model


def get_insert(preset: str):
    # Parse as Mixer to get events, because an Insert cannot parse
    # MixerID.Params which holds most of its information.
    mixer = get_model(f"inserts/{preset}", Mixer)

    # A preset stores items only for a single insert, currently thats 32 per
    # insert. Pass these to Insert's constructor. This mimics Mixer's normal
    # behaviour, however that depends on InsertID.Output as a marker to indicate
    # the end of an Insert, which surprisingly isn't a part of presets.
    params = cast(MixerParamsEvent, mixer.events.first(MixerID.Params))
    items = tuple(params.items.values())[0]
    return Insert(mixer.events, iid=0, max_slots=10, params=items)


def test_insert_bypassed():
    assert get_insert("effects-bypassed.fst").bypassed


def test_insert_channels_swapped():
    assert get_insert("channels-swapped.fst").channels_swapped


def test_insert_color():
    assert get_insert("colored.fst").color == colour.Color("#FF1414")


def test_insert_dock(inserts: tuple[Insert, ...]):
    sends = (101, 102, 103, 104)
    for insert in inserts:
        if insert.name in ("Docked left", "Master"):
            assert insert.dock == InsertDock.Left
        elif insert.name == "Docked right" or insert.iid in sends:
            assert insert.dock == InsertDock.Right
        else:
            assert insert.dock == InsertDock.Middle


def test_insert_enabled():
    assert not get_insert("disabled.fst").enabled


def test_insert_locked():
    assert get_insert("locked.fst").locked


def test_insert_pan():
    assert get_insert(r"100%-left.fst").pan == -6400
    assert get_insert(r"100%-right.fst").pan == 6400


def test_insert_polarity_reversed():
    assert get_insert("polarity-reversed.fst").polarity_reversed


def test_insert_routes(inserts: tuple[Insert, ...]):
    assert not tuple(inserts[5].routes)


def test_insert_stereo_separation():
    assert get_insert(r"100%-merged.fst").stereo_separation == 64
    assert get_insert(r"100%-separated.fst").stereo_separation == -64


def test_insert_eq():
    eq = get_insert("post-eq.fst").eq
    assert eq.low.freq == 0
    assert eq.low.gain == 1800
    assert eq.low.reso == 0
    assert eq.mid.freq == 33145
    assert eq.mid.gain == 0
    assert eq.mid.reso == 17500
    assert eq.high.freq == 65536
    assert eq.high.gain == -1800
    assert eq.high.reso == 65536


def test_mixer(mixer: Mixer):
    assert mixer.apdc
    assert len(mixer) == mixer.max_inserts == 127
    assert mixer.max_slots == 10
