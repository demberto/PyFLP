# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""Tests `pyflp.parser.Parser` class and property getters."""

import math

import pytest
from colour import Color

from pyflp import Project
from pyflp.channel.arp import ChannelArp
from pyflp.channel.channel import Channel
from pyflp.channel.delay import ChannelDelay
from pyflp.channel.level_offsets import ChannelLevelOffsets
from pyflp.channel.polyphony import ChannelPolyphony
from pyflp.channel.tracking import ChannelTracking
from pyflp.controllers import RemoteController
from pyflp.insert.parameters import InsertFlags
from pyflp.plugin.effects.balance import FBalance
from pyflp.plugin.effects.fast_dist import FFastDist
from pyflp.plugin.effects.notebook2 import FNoteBook2
from pyflp.plugin.effects.send import FSend
from pyflp.plugin.effects.soft_clipper import FSoftClipper
from pyflp.plugin.effects.soundgoodizer import Soundgoodizer
from pyflp.plugin.synths.boobass import BooBass
from pyflp.plugin.vst import VSTPlugin


def test_misc(proj: Project):
    """Tests `pyflp.misc.Misc` class."""
    misc = proj.misc
    assert misc.version == "20.8.3.2304"
    assert misc.version_build == 2304
    assert misc.channel_count == 6
    assert misc.artists == "demberto"
    assert misc.comment == "A test FLP created for PyFLP."
    assert misc.genre == "Christian Gangsta Rap"
    assert misc.tempo == 69.420
    assert misc.title == "Test"
    assert misc.url == "https://github.com/demberto/PyFLP"
    assert misc.cur_filter == -1
    assert misc.cur_pattern == 4
    assert misc.shuffle == 64
    assert misc.ppq == 96
    assert misc.format == 0
    assert misc.registered


def test_filters(proj: Project):
    filters = proj.filters
    assert set(flt.name for flt in filters) == set(
        ("Audio", "Automation", "Instrument", "Layer", "Sampler", "Unsorted")
    )


@pytest.mark.parametrize(
    "index, kind, enabled, locked, volume, pan, color, cut_group, name",
    [
        (0, Channel.Kind.Layer, True, True, 10000, 6400, Color("#141414"), (), "Layer"),
        (
            1,
            Channel.Kind.Native,
            False,
            True,
            0,
            6400,
            Color("#FFFFFF"),
            (1, 1),
            "BoobAss",
        ),
        (
            2,
            Channel.Kind.Instrument,
            True,
            False,
            10000,
            12800,
            Color("#14FF14"),
            (2, 3),
            "",  # ! Idk why, this should have been "Audio Clip"
        ),
        (
            3,
            Channel.Kind.Sampler,
            False,
            False,
            12800,
            0,
            Color("#FF1414"),
            (3, 2),
            "Min Size",
        ),
        (
            4,
            Channel.Kind.Automation,
            True,
            False,
            0,
            12800,
            Color("#1414FF"),
            (0, 0),
            "Automation Clip",
        ),
    ],
)
def test_channel(
    proj: Project, index, kind, enabled, locked, volume, pan, color, cut_group, name
):
    """Tests `pyflp.channel.channel.Channel` class."""
    ch = proj.channels[index]
    assert ch.index == index
    assert ch.kind == kind
    assert ch.enabled == enabled
    assert ch.locked == locked
    assert ch.volume == volume
    assert ch.pan == pan
    assert ch.color == color
    assert ch.cut_group == cut_group
    assert not ch.zipped
    assert isinstance(ch.delay, ChannelDelay)
    assert isinstance(ch.polyphony, ChannelPolyphony)
    assert isinstance(ch.tracking_key, ChannelTracking)
    assert isinstance(ch.level_offsets, ChannelLevelOffsets)
    assert isinstance(ch.arp, ChannelArp)
    assert len(ch.env_lfos) == 5
    assert ch.get_name() == name

    # Channel specific
    if index == 0:
        assert set(ch.children) == set((1, 2, 3))
    elif index == 1:
        bb: BooBass = ch.plugin
        assert bb.bass == bb.mid == bb.high == 32767
    elif index == 2:
        assert ch.sample_path is None


@pytest.mark.parametrize(
    "index, name, color",
    [
        (1, "Red", Color("red")),
        (2, "Green", Color("lime")),
        (3, "Blue", Color("blue")),
        (4, None, None),
    ],
)
def test_pattern(proj: Project, index, name, color):
    """Tests `pyflp.pattern.pattern.Pattern` class."""
    pat = proj.patterns[index - 1]
    assert pat.index == index
    assert pat.name == name
    assert pat.color == color

    # Pattern specific
    if index == 4:
        # Notes
        assert len(pat.notes) == 2
        green, yellow = pat.notes
        assert green.velocity == 128
        assert green.midi_channel == 0
        assert yellow.velocity == 0
        assert yellow.midi_channel == 12

        # Controller
        assert len(pat.controllers) == 768


@pytest.mark.parametrize(
    "index, name, enabled, locked, volume, pan, color, stereo_separation",
    [
        (-1, "Master", True, False, 12800, 0, Color("#141414"), 0),
        (0, "Enabled", True, False, 12800, -6400, Color("#FF1414"), 64),
        (1, "Disabled", False, False, 12800, 6400, Color("#14FF14"), -64),
        (2, "Locked + Enabled", True, True, 16000, 0, Color("#1414FF"), 0),
        (3, "Locked + Disabled", False, True, 0, 0, None, 0),
        (4, "Max Size", True, False, 12800, 0, Color("#5F7581"), 0),
        (5, "Min Size", True, False, 12800, 0, Color("#FF1414"), 0),
    ],
)
def test_insert(
    proj: Project, index, name, enabled, locked, volume, pan, color, stereo_separation
):
    """Tests `pyflp.insert.Insert` and `pyflp.insert.` class."""
    ins = proj.inserts[index + 1]
    assert ins.index == index
    assert ins.name == name
    assert ins.enabled == enabled
    assert ins.locked == locked
    assert ins.volume == volume
    assert ins.pan == pan
    assert ins.color == color
    assert ins.stereo_separation == stereo_separation

    # Insert specific
    if index == -1:
        # Test stock plugin implementations
        for i, slot in enumerate(ins.slots[:7]):
            assert slot.index == i
            assert slot.is_used()
            p = slot.plugin
            if i == 0:
                assert isinstance(p, FNoteBook2)
                assert p.active_page == 100
                assert not p.editable
                assert len(p.pages) == 3
            elif i == 1:
                assert isinstance(p, Soundgoodizer)
                assert p.mode == Soundgoodizer.Mode.A
                assert p.amount == 600
            elif i == 2:
                assert isinstance(p, FSend)
                assert p.send_to == -1
                assert p.dry == 256
                assert p.pan == 0
                assert p.volume == 256
            elif i == 3:
                assert isinstance(p, FSoftClipper)
                assert p.threshold == 100
                assert p.post == 128
            elif i == 4:
                assert isinstance(p, FBalance)
                assert p.volume == 256
                assert p.pan == 0
            elif i == 5:
                assert isinstance(p, FFastDist)
                assert p.post == 128
                assert p.threshold == 10
                assert p.pre == 128
                assert p.mix == 128
                assert p.kind == FFastDist.Kind.A
            else:
                assert isinstance(p, VSTPlugin)
                assert p.name == "OTT"
                assert p.fourcc == "TTfX"
                assert p.vendor == "Xfer Records"
                assert p.vst_number is None
    elif index == 4:
        assert InsertFlags.ReversePolarity in ins.flags
        eq = ins.eq
        assert eq.high_freq == 65536
        assert eq.band_freq == 33145
        assert eq.low_freq == 0
        assert eq.high_q == 65536
        assert eq.band_q == 17500
        assert eq.low_q == 0
        assert eq.high_level == eq.band_level == eq.low_level == 1800
    elif index == 5:
        assert InsertFlags.SwapLeftRight in ins.flags
        eq = ins.eq
        assert eq.high_freq == 0
        assert eq.band_freq == 33145
        assert eq.low_freq == 65536
        assert eq.high_q == 0
        assert eq.band_q == 17500
        assert eq.low_q == 65536
        assert eq.high_level == eq.band_level == eq.low_level == -1800


@pytest.mark.parametrize(
    "arr, number, name, enabled, locked, grouped_with_above, height",
    [
        (0, 1, "Disabled", False, False, False, 0.5),
        (0, 2, "Enabled", True, False, False, 1.5),
        (0, 3, "Locked + Enabled", True, True, True, 0.5),
        (0, 4, "Locked + Disabled", False, True, False, 2.0),
        (1, 1, "Max Size", True, False, False, 18.4),
        (1, 2, "Min Size", True, False, False, 0.0),
    ],
)
def test_tracks(
    proj: Project, arr, number, name, enabled, locked, grouped_with_above, height
):
    tr = proj.arrangements[arr].tracks[number - 1]
    assert tr.number == number
    assert tr.name == name
    assert tr.enabled == enabled
    assert tr.locked == locked
    assert tr.grouped == grouped_with_above
    assert math.isclose(tr.height, height, rel_tol=0.001)


@pytest.mark.parametrize(
    "index, name", [(0, "1st arrangement"), (1, "2nd arrangement")]
)
def test_arrangement(proj: Project, index, name):
    arr = proj.arrangements[index]
    assert arr.index == index
    assert arr.name == name


@pytest.mark.parametrize(
    "arr, index, position, name, numerator, denominator",
    [
        (0, 0, 768, "TimeMarker 1", 4, 4),
        (1, 0, 0, "Begin", 2, 8),
        (1, 1, 384, "Middle", 4, 4),
        (1, 2, 768, "3/4", 3, 4),
    ],
)
def test_timemarker(proj: Project, arr, index, position, name, numerator, denominator):
    tm = proj.arrangements[arr].timemarkers[index]
    assert tm.position == position
    assert tm.name == name
    assert tm.numerator == numerator
    assert tm.denominator == denominator


def test_controller(proj: Project):
    ctrl = proj.controllers[0]
    assert isinstance(ctrl, RemoteController)
    assert ctrl.kind == RemoteController.Kind.Channel
    assert ctrl.param == 0
    assert not ctrl.is_vst_param
