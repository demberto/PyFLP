from __future__ import annotations

from typing import TypeVar

from pyflp.plugin import (
    AnyPlugin,
    BooBass,
    FruitKick,
    FruityBalance,
    FruityBloodOverdrive,
    FruityCenter,
    FruityFastDist,
    FruitySend,
    FruitySoftClipper,
    FruityStereoEnhancer,
    Plucked,
    PluginID,
    Soundgoodizer,
    VSTPlugin,
    WrapperPage,
)

from .conftest import get_model

T = TypeVar("T", bound=AnyPlugin)


def get_plugin(preset_file: str, type: type[T]):
    return get_model(f"plugins/{preset_file}", type, PluginID.Data, PluginID.Wrapper)


def test_boobass():
    boobass = get_plugin("boobass.fst", BooBass)
    assert boobass.bass == boobass.mid == boobass.high == 32767


def test_fruit_kick():
    fruit_kick = get_plugin("fruit-kick.fst", FruitKick)
    assert fruit_kick.max_freq == -876
    assert fruit_kick.min_freq == 75
    assert fruit_kick.freq_decay == 163
    assert fruit_kick.amp_decay == 208
    assert fruit_kick.click == 39
    assert fruit_kick.distortion == 62


def test_fruity_balance():
    fruity_balance = get_plugin("fruity-balance.fst", FruityBalance)
    assert fruity_balance.volume == 256
    assert fruity_balance.pan == 0


def test_fruity_blood_overdrive():
    fruity_blood_overdrive = get_plugin(
        "fruity-blood-overdrive.fst", FruityBloodOverdrive
    )
    assert fruity_blood_overdrive.pre_band == 0
    assert fruity_blood_overdrive.color == 5000
    assert fruity_blood_overdrive.pre_amp == 0
    assert fruity_blood_overdrive.x100 == 0
    assert fruity_blood_overdrive.post_filter == 0


def test_fruity_center():
    fruity_center = get_plugin("fruity-center.fst", FruityCenter)
    assert not fruity_center.enabled


def test_fruity_fast_dist():
    fruity_fast_dist = get_plugin("fruity-fast-dist.fst", FruityFastDist)
    assert fruity_fast_dist.pre == 128
    assert fruity_fast_dist.threshold == 10
    assert fruity_fast_dist.kind == "A"
    assert fruity_fast_dist.mix == 128
    assert fruity_fast_dist.post == 128


def test_fruity_send():
    fruity_send = get_plugin("fruity-send.fst", FruitySend)
    assert fruity_send.dry == 256
    assert fruity_send.send_to == -1
    assert fruity_send.pan == 0
    assert fruity_send.volume == 256


def test_fruity_soft_clipper():
    fruity_soft_clipper = get_plugin("fruity-soft-clipper.fst", FruitySoftClipper)
    assert fruity_soft_clipper.threshold == 100
    assert fruity_soft_clipper.post == 128


def test_fruity_stereo_enhancer():
    fruity_stereo_enhancer = get_plugin(
        "fruity-stereo-enhancer.fst", FruityStereoEnhancer
    )
    assert fruity_stereo_enhancer.stereo_separation == 0
    assert fruity_stereo_enhancer.effect_position == "post"
    assert fruity_stereo_enhancer.phase_offset == 0
    assert fruity_stereo_enhancer.phase_inversion == "none"
    assert fruity_stereo_enhancer.pan == 0
    assert fruity_stereo_enhancer.volume == 256


def test_plucked():
    plucked = get_plugin("plucked.fst", Plucked)
    assert plucked.decay == 176
    assert plucked.color == 56
    assert plucked.normalize
    assert plucked.gate
    assert not plucked.widen


def test_soundgoodizer():
    soundgoodizer = get_plugin("soundgoodizer.fst", Soundgoodizer)
    assert soundgoodizer.amount == 600
    assert soundgoodizer.mode == "A"


def test_vst_plugin():
    djmfilter = get_plugin("xfer-djmfilter.fst", VSTPlugin)
    assert djmfilter.name == "DJMFilter"
    assert djmfilter.vendor == "Xfer Records"
    assert (
        djmfilter.plugin_path
        == r"C:\Program Files\Common Files\VST2\Xfer Records\DJMFilter_x64.dll"
    )


def test_fruity_wrapper():
    wrapper = get_plugin("fruity-wrapper.fst", VSTPlugin)

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
