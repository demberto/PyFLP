from __future__ import annotations

import pathlib
from typing import Any, Callable

import colour
import pytest

from pyflp import Project
from pyflp.channel import (
    Automation,
    Channel,
    ChannelRack,
    DeclickMode,
    Instrument,
    Layer,
    LFOShape,
    ReverbType,
    Sampler,
    StretchMode,
)

from .conftest import ModelFixture

AutomationFixture = Callable[[str], Automation]
ChannelFixture = Callable[[str], Channel]
InstrumentFixture = Callable[[str], Instrument]
LayerFixture = Callable[[str], Layer]
SamplerFixture = Callable[[str], Sampler]


@pytest.fixture
def load_channel(get_model: ModelFixture):
    def wrapper(preset: str, type: type[Channel] = Channel):
        return get_model(f"channels/{preset}", type)

    return wrapper


@pytest.fixture
def load_automation(load_channel: ModelFixture):
    def wrapper(preset: str):
        return load_channel(preset, Automation)

    return wrapper


@pytest.fixture
def load_instrument(load_channel: ModelFixture):
    def wrapper(preset: str):
        return load_channel(preset, Instrument)

    return wrapper


@pytest.fixture
def load_layer(load_channel: Any):
    def wrapper(preset: str):
        return load_channel(preset, Layer)

    return wrapper


@pytest.fixture
def load_sampler(load_channel: Any):
    def wrapper(preset: str):
        return load_channel(preset, Sampler)

    return wrapper


def test_channels(project: Project, rack: ChannelRack):
    assert len(rack) == project.channel_count
    assert rack.fit_to_steps is None
    assert rack.height == 646
    assert [group.name for group in rack.groups] == ["Audio", "Generators", "Unsorted"]
    assert not rack.swing


def test_automation_lfo(load_automation: AutomationFixture):
    lfo = load_automation("automation-lfo.fst").lfo
    assert lfo.amount == 64


def test_automation_points(load_automation: AutomationFixture):
    points = [point for point in load_automation("automation-points.fst")]
    assert [int(p.position or 0) for p in points] == [0, 8, 8, 16, 24, 32]


def test_channel_color(load_channel: ChannelFixture):
    assert load_channel("colored.fst").color == colour.Color("#1414FF")


def test_channel_enabled(load_channel: ChannelFixture):
    assert not load_channel("disabled.fst").enabled


def test_channel_icon(load_channel: ChannelFixture):
    assert load_channel("iconified.fst").icon == 116


def test_channel_pan(load_channel: ChannelFixture):
    assert load_channel(r"100%-left.fst").pan == 0
    assert load_channel(r"100%-right.fst").pan == 12800


def test_channel_volume(load_channel: ChannelFixture):
    assert load_channel("full-volume.fst").volume == 12800
    assert not load_channel("zero-volume.fst").volume


def test_channel_zipped(rack: ChannelRack):
    for channel in rack:
        if channel.name == "Zipped":
            assert channel.zipped
        else:
            assert not channel.zipped


def test_instrument_delay(load_instrument: InstrumentFixture):
    delay = load_instrument("delay.fst").delay
    assert delay.feedback == 12800
    assert delay.echoes == 10
    assert delay.fat_mode
    assert delay.mod_x == 0
    assert delay.mod_y == 256
    assert delay.pan == -6400
    assert delay.ping_pong
    assert delay.time == 144


def test_instrument_keyboard(load_instrument: InstrumentFixture):
    keyboard = load_instrument("keyboard.fst").keyboard
    assert keyboard.fine_tune == 100
    assert keyboard.root_note == 60


def test_instrument_polyphony(load_instrument: InstrumentFixture):
    polyphony = load_instrument("polyphony.fst").polyphony
    assert polyphony.mono
    assert polyphony.porta
    assert polyphony.max == 4
    assert polyphony.slide == 820


def test_instrument_routing(load_instrument: InstrumentFixture):
    assert load_instrument("routed.fst").insert == 125


def test_instrument_time(load_instrument: InstrumentFixture):
    time = load_instrument("time.fst").time
    assert time.full_porta
    assert time.gate == 450
    assert time.shift == 1024
    assert time.swing == 64


def test_instrument_tracking(load_instrument: InstrumentFixture):
    tracking = load_instrument("tracking.fst").tracking
    assert tracking and len(tracking) == 2

    key_tracking = tracking["keyboard"]
    assert key_tracking.middle_value == 84
    assert key_tracking.mod_x == -256
    assert key_tracking.mod_y == 256
    assert key_tracking.pan == 256


# ! Apparently, layer children events aren't stored in presets
# def test_layer_children(load_layer: LayerFixture):


def test_layer_crossfade(load_layer: LayerFixture):
    assert load_layer("layer-crossfade.fst").crossfade


def test_layer_random(load_layer: LayerFixture):
    assert load_layer("layer-random.fst").random


def test_sampler_content(load_sampler: SamplerFixture):
    content = load_sampler("sampler-content.fst").content
    assert content.keep_on_disk
    assert content.resample
    assert not content.load_regions
    assert not content.load_slices
    assert content.declick_mode == DeclickMode.Generic


def test_sampler_cut_group(load_sampler: SamplerFixture):
    assert load_sampler("cut-groups.fst").cut_group == (1, 2)


def test_sampler_envelopes(load_sampler: SamplerFixture):
    envelopes = load_sampler("envelope.fst").envelopes
    assert envelopes and len(envelopes) == 5

    volume = envelopes["Volume"]
    assert volume.enabled
    assert volume.predelay == 100
    assert volume.attack == 100
    assert volume.hold == 100
    assert volume.decay == 100
    assert volume.sustain == 0
    assert volume.release == 100
    assert volume.synced
    assert volume.attack_tension == volume.release_tension == volume.decay_tension == 0

    mod_x = envelopes["Mod X"]
    assert mod_x.enabled
    assert mod_x.predelay == 65536
    assert mod_x.attack == 65536
    assert mod_x.hold == 65536
    assert mod_x.decay == 65536
    assert mod_x.sustain == 128
    assert mod_x.release == 65536
    assert mod_x.amount == 128
    assert not mod_x.synced
    assert mod_x.attack_tension == mod_x.release_tension == mod_x.decay_tension == 128


def test_sampler_fx(load_sampler: SamplerFixture):
    fx = load_sampler("sampler-fx.fst").fx
    assert fx.boost == 128
    assert fx.clip
    assert fx.cutoff == 16
    assert fx.crossfade == 0
    assert fx.fade_in == 1024
    assert fx.fade_out == 0
    assert fx.fade_stereo
    assert fx.fix_trim
    assert fx.freq_tilt == 0
    assert fx.length == 1.0
    assert not fx.normalize
    assert fx.pogo == 256
    assert fx.inverted
    assert not fx.remove_dc
    assert fx.resonance == 640
    assert fx.reverb.type == ReverbType.A
    assert fx.reverb.mix == 128
    assert not fx.reverse
    assert fx.ringmod == (64, 192)
    assert fx.start == 0.0
    assert fx.stereo_delay == 4096
    assert fx.swap_stereo
    assert fx.trim == 256


def test_sampler_lfo(load_sampler: SamplerFixture):
    lfos = load_sampler("lfo.fst").lfos
    assert lfos and len(lfos) == 5

    volume = lfos["Volume"]
    assert volume.amount == 128
    assert volume.attack == 65536
    assert volume.predelay == 100
    assert volume.shape == LFOShape.Pulse
    assert volume.speed == 65536
    assert volume.retrig
    assert not volume.synced

    mod_x = lfos["Mod X"]
    assert mod_x.amount == -128
    assert mod_x.attack == 100
    assert mod_x.predelay == 65536
    assert mod_x.shape == LFOShape.Sine
    assert mod_x.speed == 200
    assert not mod_x.retrig
    assert mod_x.synced


def test_sampler_path(load_sampler: SamplerFixture):
    assert load_sampler("sampler-path.fst").sample_path == pathlib.Path(
        r"%FLStudioFactoryData%\Data\Patches\Packs\Drums\Kicks\22in Kick.wav"
    )


def test_sampler_pitch_shift(load_sampler: SamplerFixture):
    assert load_sampler("+4800-cents.fst").pitch_shift == 4800
    assert load_sampler("-4800-cents.fst").pitch_shift == -4800


def test_sampler_playback(load_sampler: SamplerFixture):
    playback = load_sampler("sampler-playback.fst").playback
    assert playback.use_loop_points
    assert playback.ping_pong_loop
    assert playback.start_offset == 1072693248


def test_sampler_stretching(load_sampler: SamplerFixture):
    stretching = load_sampler("sampler-stretching.fst").stretching
    assert stretching.mode == StretchMode.E3Generic
    assert stretching.multiplier == 0.25
    assert stretching.pitch == 1200
    assert stretching.time == (4, 0, 0)
