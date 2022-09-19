from __future__ import annotations

from typing import cast

import pytest

from pyflp.mixer import Insert
from pyflp.plugin import (
    AnyPlugin,
    FruityBalance,
    FruityFastDist,
    FruityFastDistKind,
    FruitySend,
    FruitySoftClipper,
    FruityStereoEnhancer,
    Soundgoodizer,
    SoundgoodizerMode,
    StereoEnhancerEffectPosition,
    StereoEnhancerPhaseInversion,
    VSTPlugin,
)


@pytest.fixture(scope="session")
def plugins(inserts: tuple[Insert, ...]):
    return [slot.plugin for slot in inserts[19]][:7]


def test_plugin_types(plugins: tuple[AnyPlugin, ...]):
    assert [type(plugin) for plugin in plugins] == [
        FruityBalance,
        FruityFastDist,
        FruitySend,
        FruitySoftClipper,
        FruityStereoEnhancer,
        Soundgoodizer,
        VSTPlugin,
    ]


def test_fruity_balance(plugins: tuple[AnyPlugin, ...]):
    fruity_balance = cast(FruityBalance, plugins[0])
    assert fruity_balance.volume == 256
    assert fruity_balance.pan == 0


def test_fruity_fast_dist(plugins: tuple[AnyPlugin, ...]):
    fruity_fast_dist = cast(FruityFastDist, plugins[1])
    assert fruity_fast_dist.pre == 128
    assert fruity_fast_dist.threshold == 10
    assert fruity_fast_dist.kind == FruityFastDistKind.A
    assert fruity_fast_dist.mix == 128
    assert fruity_fast_dist.post == 128


def test_fruity_send(plugins: tuple[AnyPlugin, ...]):
    fruity_send = cast(FruitySend, plugins[2])
    assert fruity_send.dry == 256
    assert fruity_send.send_to == -1
    assert fruity_send.pan == 0
    assert fruity_send.volume == 256


def test_fruity_soft_clipper(plugins: tuple[AnyPlugin, ...]):
    fruity_soft_clipper = cast(FruitySoftClipper, plugins[3])
    assert fruity_soft_clipper.threshold == 100
    assert fruity_soft_clipper.post == 128


def test_fruity_stereo_enhancer(plugins: tuple[AnyPlugin, ...]):
    fruity_stereo_enhancer = cast(FruityStereoEnhancer, plugins[4])
    assert fruity_stereo_enhancer.stereo_separation == 0
    assert fruity_stereo_enhancer.effect_position == StereoEnhancerEffectPosition.Post
    assert fruity_stereo_enhancer.phase_offset == 0
    assert fruity_stereo_enhancer.phase_inversion == StereoEnhancerPhaseInversion.None_
    assert fruity_stereo_enhancer.pan == 0
    assert fruity_stereo_enhancer.volume == 256


def test_soundgoodizer(plugins: tuple[AnyPlugin, ...]):
    soundgoodizer = cast(Soundgoodizer, plugins[5])
    assert soundgoodizer.amount == 600
    assert soundgoodizer.mode == SoundgoodizerMode.A


def test_vst_plugin(plugins: tuple[AnyPlugin, ...]):
    ott = cast(VSTPlugin, plugins[6])
    assert ott.name == "OTT"
    assert ott.vendor == "Xfer Records"
    assert ott.plugin_path == r"C:\Program Files\Common Files\VST3\OTT.vst3"

    with pytest.raises(KeyError):
        ott.fourcc
