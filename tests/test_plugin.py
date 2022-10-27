from __future__ import annotations

from typing import Callable, Type, TypeVar

import pytest

from pyflp.plugin import (
    AnyPlugin,
    FruityBalance,
    FruityCenter,
    FruityFastDist,
    FruitySend,
    FruitySoftClipper,
    FruityStereoEnhancer,
    PluginID,
    Soundgoodizer,
    VSTPlugin,
    WrapperPage,
)

from .conftest import ModelFixture

T = TypeVar("T", bound=AnyPlugin)
PluginFixture = Callable[[str, Type[T]], T]


@pytest.fixture
def plugin(get_model: ModelFixture):
    def wrapper(preset_file: str, type: type[T]):
        suffix = f"plugins/{preset_file}"
        return get_model(suffix, type, PluginID.Data, PluginID.Wrapper)

    return wrapper


def test_fruity_balance(plugin: PluginFixture[FruityBalance]):
    fruity_balance = plugin("fruity-balance.fst", FruityBalance)
    assert fruity_balance.volume == 256
    assert fruity_balance.pan == 0


def test_fruity_center(plugin: PluginFixture[FruityCenter]):
    fruity_center = plugin("fruity-center.fst", FruityCenter)
    assert not fruity_center.enabled


def test_fruity_fast_dist(plugin: PluginFixture[FruityFastDist]):
    fruity_fast_dist = plugin("fruity-fast-dist.fst", FruityFastDist)
    assert fruity_fast_dist.pre == 128
    assert fruity_fast_dist.threshold == 10
    assert fruity_fast_dist.kind == "A"
    assert fruity_fast_dist.mix == 128
    assert fruity_fast_dist.post == 128


def test_fruity_send(plugin: PluginFixture[FruitySend]):
    fruity_send = plugin("fruity-send.fst", FruitySend)
    assert fruity_send.dry == 256
    assert fruity_send.send_to == -1
    assert fruity_send.pan == 0
    assert fruity_send.volume == 256


def test_fruity_soft_clipper(plugin: PluginFixture[FruitySoftClipper]):
    fruity_soft_clipper = plugin("fruity-soft-clipper.fst", FruitySoftClipper)
    assert fruity_soft_clipper.threshold == 100
    assert fruity_soft_clipper.post == 128


def test_fruity_stereo_enhancer(plugin: PluginFixture[FruityStereoEnhancer]):
    fruity_stereo_enhancer = plugin("fruity-stereo-enhancer.fst", FruityStereoEnhancer)
    assert fruity_stereo_enhancer.stereo_separation == 0
    assert fruity_stereo_enhancer.effect_position == "post"
    assert fruity_stereo_enhancer.phase_offset == 0
    assert fruity_stereo_enhancer.phase_inversion == "none"
    assert fruity_stereo_enhancer.pan == 0
    assert fruity_stereo_enhancer.volume == 256


def test_soundgoodizer(plugin: PluginFixture[Soundgoodizer]):
    soundgoodizer = plugin("soundgoodizer.fst", Soundgoodizer)
    assert soundgoodizer.amount == 600
    assert soundgoodizer.mode == "A"


def test_vst_plugin(plugin: PluginFixture[VSTPlugin]):
    djmfilter = plugin("xfer-djmfilter.fst", VSTPlugin)
    assert djmfilter.name == "DJMFilter"
    assert djmfilter.vendor == "Xfer Records"
    assert (
        djmfilter.plugin_path
        == r"C:\Program Files\Common Files\VST2\Xfer Records\DJMFilter_x64.dll"
    )


def test_fruity_wrapper(plugin: PluginFixture[VSTPlugin]):
    wrapper = plugin("fruity-wrapper.fst", VSTPlugin)

    # WrapperEvent properties
    assert not wrapper.compact
    assert not wrapper.demo_mode
    assert not wrapper.detached
    assert not wrapper.directx
    assert not wrapper.disabled
    assert wrapper.generator
    assert wrapper.height == 410
    assert not wrapper.minimized
    assert wrapper.multithreaded
    assert wrapper.page == WrapperPage.Settings
    assert not wrapper.smart_disable
    assert wrapper.visible
    assert wrapper.width == 561

    # VSTPluginEvent properties
    assert wrapper.automation.notify_changes
    assert wrapper.compatibility.buffers_maxsize
    assert wrapper.compatibility.fast_idle
    assert not wrapper.compatibility.fixed_buffers
    assert wrapper.compatibility.process_maximum
    assert wrapper.compatibility.reset_on_transport
    assert wrapper.compatibility.send_loop
    assert not wrapper.compatibility.use_time_offset
    assert wrapper.midi.input == 6
    assert wrapper.midi.output == 9
    assert wrapper.midi.pb_range == 36
    assert not wrapper.midi.send_modx
    assert not wrapper.midi.send_pb
    assert wrapper.midi.send_release
    assert wrapper.processing.allow_sd
    assert not wrapper.processing.bridged
    assert wrapper.processing.keep_state
    assert wrapper.processing.multithreaded
    assert wrapper.processing.notify_render
    assert wrapper.ui.accept_drop
    assert not wrapper.ui.always_update
    assert wrapper.ui.dpi_aware
    assert not wrapper.ui.scale_editor
