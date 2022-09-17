from __future__ import annotations

from pyflp.mixer import Mixer


def test_mixer(mixer: Mixer):
    assert len(mixer) == 127
    assert mixer.apdc
    assert mixer.max_inserts == 127
    assert mixer.max_slots == 10
