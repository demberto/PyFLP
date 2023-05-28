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

"""Contains the types used by channels and the channel rack."""

from __future__ import annotations

import enum
import pathlib
from typing import Any, Iterator, Literal, Tuple, cast

import construct as c
import construct_typed as ct

from pyflp._adapters import LinearMusical, List2Tuple, Log2, LogNormal, StdEnum
from pyflp._descriptors import EventProp, FlagProp, NestedProp, StructProp
from pyflp._events import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    BoolEvent,
    EventEnum,
    F32Event,
    I8Event,
    I32Event,
    StructEventBase,
    U8Event,
    U16Event,
    U16TupleEvent,
    U32Event,
)
from pyflp._models import EventModel, ItemModel, ModelCollection, ModelReprMixin, supports_slice
from pyflp.exceptions import ModelNotFound, NoModelsFound, PropertyCannotBeSet
from pyflp.plugin import BooBass, FruitKick, Plucked, PluginID, PluginProp, VSTPlugin
from pyflp.types import RGBA, MusicalTime

__all__ = [
    "ArpDirection",
    "Automation",
    "AutomationPoint",
    "Channel",
    "Instrument",
    "Layer",
    "ChannelRack",
    "ChannelNotFound",
    "DeclickMode",
    "LFOShape",
    "ReverbType",
    "FX",
    "Reverb",
    "Delay",
    "Envelope",
    "SamplerLFO",
    "Tracking",
    "Keyboard",
    "LevelAdjusts",
    "StretchMode",
    "Time",
    "TimeStretching",
    "Polyphony",
    "Playback",
    "ChannelType",
]

EnvelopeName = Literal["Panning", "Volume", "Mod X", "Mod Y", "Pitch"]
LFOName = EnvelopeName


class ChannelNotFound(ModelNotFound, KeyError):
    pass


class AutomationEvent(StructEventBase):
    @staticmethod
    def _get_position(stream: c.StreamType, index: int) -> float:
        cur = stream.tell()
        position = 0.0
        for i in range(index + 1):
            stream.seek(21 + (i * 24))
            position += c.Float64l.parse_stream(stream)
        stream.seek(cur)
        return position

    STRUCT = c.Struct(
        "_u1" / c.Bytes(4),  # 4  # ? Always 1
        "lfo.amount" / c.Int32sl,
        "_u2" / c.Bytes(1),  # 9
        "_u3" / c.Bytes(2),  # 11
        "_u4" / c.Bytes(2),  # 13  # ? Always 0
        "_u5" / c.Bytes(4),  # 17
        "points"
        / c.PrefixedArray(
            c.Int32ul,  # 21
            c.Struct(
                "_offset" / c.Float64l * "Change in X-axis w.r.t last point",
                "position"  # TODO Implement a setter
                / c.IfThenElse(
                    lambda ctx: ctx._index > 0,
                    c.Computed(lambda ctx: AutomationEvent._get_position(ctx._io, ctx._index)),
                    c.Computed(lambda ctx: ctx["_offset"]),
                ),
                "value" / c.Float64l,
                "tension" / c.Float32l,
                "_u1" / c.Bytes(4),  # Linked to tension
            ),  # 24 per struct
        ),
        "_u6" / c.GreedyBytes,  # TODO Upto a whooping 112 bytes
    )


class DelayEvent(StructEventBase):
    STRUCT = c.Struct(
        "feedback" / c.Optional(c.Int32ul),
        "pan" / c.Optional(c.Int32sl),
        "pitch_shift" / c.Optional(c.Int32sl),
        "echoes" / c.Optional(c.Int32ul),
        "time" / c.Optional(c.Int32ul),
    ).compile()


@enum.unique
class _EnvLFOFlags(enum.IntFlag):
    EnvelopeTempoSync = 1 << 0
    Unknown = 1 << 2  # Occurs for volume envlope only. Likely a bug in FL's serialiser
    LFOTempoSync = 1 << 1
    LFOPhaseRetrig = 1 << 5


@enum.unique
class LFOShape(ct.EnumBase):
    """Used by :attr:`LFO.shape`."""

    Sine = 0
    Triangle = 1
    Pulse = 2


# FL Studio 2.5.0+
class EnvelopeLFOEvent(StructEventBase):
    STRUCT = c.Struct(
        "flags" / c.Optional(StdEnum[_EnvLFOFlags](c.Int32sl)),  # 4
        "envelope.enabled" / c.Optional(c.Int32sl),  # 8
        "envelope.predelay" / c.Optional(c.Int32sl),  # 12
        "envelope.attack" / c.Optional(c.Int32sl),  # 16
        "envelope.hold" / c.Optional(c.Int32sl),  # 20
        "envelope.decay" / c.Optional(c.Int32sl),  # 24
        "envelope.sustain" / c.Optional(c.Int32sl),  # 28
        "envelope.release" / c.Optional(c.Int32sl),  # 32
        "envelope.amount" / c.Optional(c.Int32sl),  # 36
        "lfo.predelay" / c.Optional(c.Int32ul),  # 40
        "lfo.attack" / c.Optional(c.Int32ul),  # 44
        "lfo.amount" / c.Optional(c.Int32sl),  # 48
        "lfo.speed" / c.Optional(c.Int32ul),  # 52
        "lfo.shape" / c.Optional(StdEnum[LFOShape](c.Int32sl)),  # 56
        "envelope.attack_tension" / c.Optional(c.Int32sl),  # 60
        "envelope.decay_tension" / c.Optional(c.Int32sl),  # 64
        "envelope.release_tension" / c.Optional(c.Int32sl),  # 68
    ).compile()


class LevelAdjustsEvent(StructEventBase):
    STRUCT = c.Struct(
        "pan" / c.Optional(c.Int32sl),  # 4
        "volume" / c.Optional(c.Int32ul),  # 8
        "_u1" / c.Optional(c.Int32ul),  # 12
        "mod_x" / c.Optional(c.Int32sl),  # 16
        "mod_y" / c.Optional(c.Int32sl),  # 20
    ).compile()


class FilterType(ct.EnumBase):
    FastLP = 0
    LP = 1
    BP = 2
    HP = 3
    BS = 4
    LPx2 = 5
    SVFLP = 6
    SVFLPx2 = 7


class LevelsEvent(StructEventBase):
    STRUCT = c.Struct(
        "pan" / c.Optional(c.Int32sl),  # 4
        "volume" / c.Optional(c.Int32ul),  # 8
        "pitch_shift" / c.Optional(c.Int32sl),  # 12
        "filter.mod_x" / c.Optional(c.Int32ul),  # 16
        "filter.mod_y" / c.Optional(c.Int32ul),  # 20
        "filter.type" / c.Optional(StdEnum[FilterType](c.Int32ul)),  # 24
    ).compile()


@enum.unique
class ArpDirection(ct.EnumBase):
    """Used by :attr:`Arp.direction`."""

    Off = 0
    Up = 1
    Down = 2
    UpDownBounce = 3
    UpDownSticky = 4
    Random = 5


@enum.unique
class DeclickMode(ct.EnumBase):
    OutOnly = 0
    TransientNoBleeding = 1
    Transient = 2
    Generic = 3
    Smooth = 4
    Crossfade = 5


@enum.unique
class _DelayFlags(enum.IntFlag):
    PingPong = 1 << 1
    FatMode = 1 << 2


@enum.unique
class StretchMode(ct.EnumBase):
    Stretch = -1
    Resample = 0
    E3Generic = 1
    E3Mono = 2
    SliceStretch = 3
    SliceMap = 4
    Auto = 5
    E2Generic = 6
    E2Transient = 7
    E2Mono = 8
    E2Speech = 9


class ParametersEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Optional(c.Bytes(9)),  # 9
        "fx.remove_dc" / c.Optional(c.Flag),  # 10
        "delay.flags" / c.Optional(StdEnum[_DelayFlags](c.Int8ul)),  # 11
        "keyboard.main_pitch" / c.Optional(c.Flag),  # 12
        "_u2" / c.Optional(c.Bytes(28)),  # 40
        "arp.direction" / c.Optional(StdEnum[ArpDirection](c.Int32ul)),  # 44
        "arp.range" / c.Optional(c.Int32ul),  # 48
        "arp.chord" / c.Optional(c.Int32ul),  # 52
        "arp.time" / c.Optional(c.Float32l),  # 56
        "arp.gate" / c.Optional(c.Float32l),  # 60
        "arp.slide" / c.Optional(c.Flag),  # 61
        "_u3" / c.Optional(c.Bytes(1)),  # 62
        "time.full_porta" / c.Optional(c.Flag),  # 63
        "keyboard.add_root" / c.Optional(c.Flag),  # 64
        "time.gate" / c.Optional(c.Int16ul),  # 66
        "_u4" / c.Optional(c.Bytes(2)),  # 68
        "keyboard.key_region" / c.Optional(List2Tuple(c.Int32ul[2])),  # 76
        "_u5" / c.Optional(c.Bytes(4)),  # 80
        "fx.normalize" / c.Optional(c.Flag),  # 81
        "fx.inverted" / c.Optional(c.Flag),  # 82
        "_u6" / c.Optional(c.Bytes(1)),  # 83
        "content.declick_mode" / c.Optional(StdEnum[DeclickMode](c.Int8ul)),  # 84
        "fx.crossfade" / c.Optional(c.Int32ul),  # 88
        "fx.trim" / c.Optional(c.Int32ul),  # 92
        "arp.repeat" / c.Optional(c.Int32ul),  # 96; FL 4.5.2+
        "stretching.time" / c.Optional(LinearMusical(c.Int32ul)),  # 100
        "stretching.pitch" / c.Optional(c.Int32sl),  # 104
        "stretching.multiplier" / c.Optional(Log2(c.Int32sl, 10000)),  # 108
        "stretching.mode" / c.Optional(StdEnum[StretchMode](c.Int32sl)),  # 112
        "_u7" / c.Optional(c.Bytes(21)),  # 133
        "fx.start" / c.Optional(LogNormal(c.Int16ul[2], (0, 61440))),  # 137
        "_u8" / c.Optional(c.Bytes(4)),  # 141
        "fx.length" / c.Optional(LogNormal(c.Int16ul[2], (0, 61440))),  # 145
        "_u9" / c.Optional(c.Bytes(3)),  # 148
        "playback.start_offset" / c.Optional(c.Int32ul),  # 152
        "_u10" / c.Optional(c.Bytes(5)),  # 157
        "fx.fix_trim" / c.Optional(c.Flag),  # 158 (FL 20.8.4 max)
        "_extra" / c.GreedyBytes,  # * 168 as of 20.9.1
    )


@enum.unique
class _PolyphonyFlags(enum.IntFlag):
    None_ = 0
    Mono = 1 << 0
    Porta = 1 << 1


class PolyphonyEvent(StructEventBase):
    STRUCT = c.Struct(
        "max" / c.Optional(c.Int32ul),  # 4
        "slide" / c.Optional(c.Int32ul),  # 8
        "flags" / c.Optional(StdEnum[_PolyphonyFlags](c.Byte)),  # 9
    ).compile()


class TrackingEvent(StructEventBase):
    STRUCT = c.Struct(
        "middle_value" / c.Optional(c.Int32ul),  # 4
        "pan" / c.Optional(c.Int32sl),  # 8
        "mod_x" / c.Optional(c.Int32sl),  # 12
        "mod_y" / c.Optional(c.Int32sl),  # 16
    ).compile()


@enum.unique
class ChannelID(EventEnum):
    IsEnabled = (0, BoolEvent)
    _VolByte = (2, U8Event)
    _PanByte = (3, U8Event)
    Zipped = (15, BoolEvent)
    # _19 = (19, BoolEvent)
    PingPongLoop = (20, BoolEvent)
    Type = (21, U8Event)
    RoutedTo = (22, I8Event)
    # FXProperties = 27
    IsLocked = (32, BoolEvent)  #: 12.3+
    New = (WORD, U16Event)
    FreqTilt = (WORD + 5, U16Event)
    FXFlags = (WORD + 6, U16Event)
    Cutoff = (WORD + 7, U16Event)
    _VolWord = (WORD + 8, U16Event)
    _PanWord = (WORD + 9, U16Event)
    Preamp = (WORD + 10, U16Event)  #: 1.2.12+
    FadeOut = (WORD + 11, U16Event)  #: 1.7.6+
    FadeIn = (WORD + 12, U16Event)
    # _DotNote = WORD + 13
    # _DotPitch = WORD + 14
    # _DotMix = WORD + 15
    Resonance = (WORD + 19, U16Event)
    # _LoopBar = WORD + 20
    StereoDelay = (WORD + 21, U16Event)  #: 1.3.56+
    Pogo = (WORD + 22, U16Event)
    # _DotReso = WORD + 23
    # _DotCutOff = WORD + 24
    TimeShift = (WORD + 25, U16Event)
    # _Dot = WORD + 27
    # _DotRel = WORD + 32
    # _DotShift = WORD + 28
    Children = (WORD + 30, U16Event)  #: 3.4.0+
    Swing = (WORD + 33, U16Event)
    # Echo = DWORD + 2
    RingMod = (DWORD + 3, U16TupleEvent)
    CutGroup = (DWORD + 4, U16TupleEvent)
    RootNote = (DWORD + 7, U32Event)
    # _MainResoCutOff = DWORD + 9
    DelayModXY = (DWORD + 10, U16TupleEvent)
    Reverb = (DWORD + 11, U32Event)  #: 1.4.0+
    _StretchTime = (DWORD + 12, F32Event)  #: 5.0+
    FineTune = (DWORD + 14, I32Event)
    SamplerFlags = (DWORD + 15, U32Event)
    LayerFlags = (DWORD + 16, U32Event)
    GroupNum = (DWORD + 17, I32Event)
    AUSampleRate = (DWORD + 25, U32Event)
    _Name = TEXT
    SamplePath = TEXT + 4
    Delay = (DATA + 1, DelayEvent)
    Parameters = (DATA + 7, ParametersEvent)
    EnvelopeLFO = (DATA + 10, EnvelopeLFOEvent)
    Levels = (DATA + 11, LevelsEvent)
    # _Filter = DATA + 12
    Polyphony = (DATA + 13, PolyphonyEvent)
    # _LegacyAutomation = DATA + 15
    Tracking = (DATA + 20, TrackingEvent)
    LevelAdjusts = (DATA + 21, LevelAdjustsEvent)
    Automation = (DATA + 26, AutomationEvent)


@enum.unique
class DisplayGroupID(EventEnum):
    Name = TEXT + 39  #: 3.4.0+


@enum.unique
class RackID(EventEnum):
    Swing = (11, U8Event)
    _FitToSteps = (13, U8Event)
    WindowHeight = (DWORD + 5, U32Event)


@enum.unique
class ReverbType(enum.IntEnum):
    """Used by :attr:`Reverb.type`."""

    A = 0
    B = 65536


# The type of a channel may decide how a certain event is interpreted. An
# example of this is `ChannelID.Levels` event, which is used for storing
# volume, pan and pich bend range of any channel other than automations. In
# automations it is used for **Min** and **Max** knobs.
@enum.unique
class ChannelType(ct.EnumBase):  # cuz Type would be a super generic name
    """An internal marker used to indicate the type of a channel."""

    Sampler = 0
    """Used exclusively for the inbuilt Sampler."""

    Native = 2
    """Used by audio clips and other native FL Studio synths."""

    Layer = 3  # 3.4.0+
    Instrument = 4
    Automation = 5  # 5.0+


class _FXFlags(enum.IntFlag):
    FadeStereo = 1 << 0
    Reverse = 1 << 1
    Clip = 1 << 2
    SwapStereo = 1 << 8


class _LayerFlags(enum.IntFlag):
    Random = 1 << 0
    Crossfade = 1 << 1


class _SamplerFlags(enum.IntFlag):
    Resample = 1 << 0
    LoadRegions = 1 << 1
    LoadSliceMarkers = 1 << 2
    UsesLoopPoints = 1 << 3
    KeepOnDisk = 1 << 8


class DisplayGroup(EventModel, ModelReprMixin):
    def __str__(self) -> str:
        if self.name is None:
            return "Unnamed display group"
        return f"Display group {self.name}"

    name = EventProp[str](DisplayGroupID.Name)


class Arp(EventModel, ModelReprMixin):
    """Used by :class:`Sampler`: and :class:`Instrument`.

    ![](https://bit.ly/3Lbk7Yi)
    """

    chord = StructProp[int]()
    """Index of the selected arpeggio chord."""

    direction = StructProp[ArpDirection]()
    gate = StructProp[float]()
    """Delay between two successive notes played."""

    range = StructProp[int]()
    """Range (in octaves)."""

    repeat = StructProp[int]()
    """Number of times a note is repeated.

    *New in FL Studio v4.5.2*.
    """

    slide = StructProp[bool]()
    """Whether arpeggio will slide between notes."""

    time = StructProp[float]()
    """Delay between two successive notes played."""


class Delay(EventModel, ModelReprMixin):
    """Echo delay / fat mode section.

    Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3RyzbBD)
    """

    echoes = StructProp[int](ChannelID.Delay)
    """Number of echoes generated for each note. Min = 1. Max = 10."""

    fat_mode = FlagProp(_DelayFlags.FatMode, ChannelID.Parameters, prop="delay.flags")
    """*New in FL Studio v3.4.0*."""

    feedback = StructProp[int](ChannelID.Delay)
    """Factor with which the volume of every next echo is multiplied.

    Defaults to minimum value.

    | Type | Value | Representation |
    |------|-------|----------------|
    | Min  | 0     | 0%             |
    | Max  | 25600 | 200%           |
    """

    @property
    def mod_x(self) -> int:
        """Min = 0. Max = 256. Default = 128."""
        return self.events.first(ChannelID.DelayModXY).value[0]

    @mod_x.setter
    def mod_x(self, value: int) -> None:
        event = self.events.first(ChannelID.DelayModXY)
        event.value = (value, event.value[1])

    @property
    def mod_y(self) -> int:
        """Min = 0. Max = 256. Default = 128."""
        return self.events.first(ChannelID.DelayModXY).value[1]

    @mod_y.setter
    def mod_y(self, value: int) -> None:
        event = self.events.first(ChannelID.DelayModXY)
        event.value = (event.value[0], value)

    pan = StructProp[int](ChannelID.Delay)
    """
    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -6400 | 100% left      |
    | Max     | 6400  | 100% right     |
    | Default | 0     | Centred        |
    """

    ping_pong = FlagProp(
        _DelayFlags.PingPong,
        ChannelID.Parameters,
        prop="delay.flags",
    )
    """*New in FL Studio v1.7.6*."""

    pitch_shift = StructProp[int](ChannelID.Delay)
    """Pitch shift (in cents).

    | Min   | Max   | Default |
    |-------|-------|---------|
    | -1200 | 1200  | 0       |
    """

    time = StructProp[int](ChannelID.Delay)
    """Tempo-synced delay time. PPQ dependant.

    | Type    | Value     | Representation |
    |---------|-----------|----------------|
    | Min     | 0         | 0:00           |
    | Max     | PPQ * 4   | 8:00           |
    | Default | PPQ * 3/2 | 3:00           |
    """


class Filter(EventModel, ModelReprMixin):
    """Used by :class:`Sampler`.

    ![](https://bit.ly/3zT5tAH)
    """

    mod_x = StructProp[int](ChannelID.Levels, prop="filter.mod_x")
    """Filter cutoff. Min = 0. Max = 256. Defaults to maximum."""

    mod_y = StructProp[int](ChannelID.Levels, prop="filter.mod_y")
    """Filter resonance. Min = 0. Max = 256. Defaults to minimum."""

    type = StructProp[FilterType](ChannelID.Levels, prop="filter.type")
    """Defaults to :attr:`FilterType.FastLP`."""


class LevelAdjusts(EventModel, ModelReprMixin):
    """Used by :class:`Layer`, :class:`Instrument` and :class:`Sampler`.

    ![](https://bit.ly/3xkKeGn)

    *New in FL Studio v3.3.0*.
    """

    mod_x = StructProp[int]()
    mod_y = StructProp[int]()
    pan = StructProp[int]()
    volume = StructProp[int]()


class Time(EventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3xjxUGG)
    """

    swing = EventProp[int](ChannelID.Swing)
    """Percentage of the ``ChannelRack.swing`` that affects this channel.

    Linear. Min = 0. Max = 128. Defaults to maximum.
    """

    gate = StructProp[int](ChannelID.Parameters, prop="time.gate")
    """Logarithmic. Defaults to disabled state.

    | Type     | Value | Representation |
    |----------|-------|----------------|
    | Min      | 450   | 0:03           |
    | Max      | 1446  | 4:00           |
    | Disabled | 1447  | Off            |
    """

    shift = EventProp[int](ChannelID.TimeShift)
    """Fine time shift. Nonlinear. Defaults to minimum.

    | Type | Value | Representation |
    |------|-------|----------------|
    | Min  | 0     | 0:00           |
    | Max  | 1024  | 1:00           |
    """

    full_porta = StructProp[bool](ChannelID.Parameters, prop="time.full_porta")
    """Whether :attr:`gate` is bypassed when :attr:`Polyphony.porta` is on."""


class Reverb(EventModel, ModelReprMixin):
    """Precalculated reverb used by :class:`Sampler`.

    *New in FL Studio v1.4.0*.
    """

    @property
    def type(self) -> ReverbType | None:
        if ChannelID.Reverb in self.events.ids:
            event = self.events.first(ChannelID.Reverb)
            return ReverbType.B if event.value >= ReverbType.B else ReverbType.A

    @type.setter
    def type(self, value: ReverbType) -> None:
        if self.mix is None:
            raise PropertyCannotBeSet(ChannelID.Reverb)

        self.events.first(ChannelID.Reverb).value = value.value + self.mix

    @property
    def mix(self) -> int | None:
        """Mix % (wet). Defaults to minimum value.

        | Min | Max |
        |-----|-----|
        | 0   | 256 |
        """
        if ChannelID.Reverb in self.events.ids:
            return self.events.first(ChannelID.Reverb).value - self.type

    @mix.setter
    def mix(self, value: int) -> None:
        if ChannelID.Reverb not in self.events.ids:
            raise PropertyCannotBeSet(ChannelID.Reverb)

        self.events.first(ChannelID.Reverb).value += value


class FX(EventModel, ModelReprMixin):
    """Pre-computed effects used by :class:`Sampler`.

    ![](https://bit.ly/3U3Ys8l)
    ![](https://bit.ly/3qvdBSN)

    See Also:
        :attr:`Sampler.fx`, :attr:`Reverb`
    """

    boost = EventProp[int](ChannelID.Preamp)
    """Pre-amp gain. Defaults to minimum value.

    | Min | Max |
    |-----|-----|
    | 0   | 256 |

    *New in FL Studio v1.2.12*.
    """

    clip = FlagProp(_FXFlags.Clip, ChannelID.FXFlags)
    """Whether output is clipped at 0dB for :attr:`boost`."""

    crossfade = StructProp[int](ChannelID.Parameters, prop="fx.crossfade")
    """Linear. Defaults to minimum value

    | Type | Value | Representation |
    |------|-------|----------------|
    | Min  | 0     | 0%             |
    | Max  | 256   | 100%           |
    """

    cutoff = EventProp[int](ChannelID.Cutoff)
    """Filter Mod X. Defaults to maximum value. Min = 16. Max = 1024."""

    fade_in = EventProp[int](ChannelID.FadeIn)
    """Quick fade-in. Defaults to minimum value. Min = 0. Max = 1024."""

    fade_out = EventProp[int](ChannelID.FadeOut)
    """Quick fade-out. Defaults to minimum value. Min = 0. Max = 1024.

    *New in FL Studio v1.7.6*.
    """

    fade_stereo = FlagProp(_FXFlags.FadeStereo, ChannelID.FXFlags)
    fix_trim = StructProp[bool](ChannelID.Parameters, prop="fx.fix_trim")
    """:menuselection:`Trim --> Fix legacy precomputed length`.

    Has no effect on the value of :attr:`trim`.
    """

    freq_tilt = EventProp[int](ChannelID.FreqTilt)
    """Shifts the frequency balance. Bipolar.

    | Min | Max | Default |
    |-----|-----|---------|
    | 0   | 256 | 128     |
    """

    inverted = StructProp[bool](ChannelID.Parameters, prop="fx.inverted")
    """Named :guilabel:`Reverse polarity` in FL's interface."""

    length = StructProp[float](ChannelID.Parameters, prop="fx.length")
    """Min = 0.0, Max = 1.0. Defaults to minimum value.

    Named :guilabel:`SMP START` in FL's interface.
    """

    normalize = StructProp[bool](ChannelID.Parameters, prop="fx.normalize")
    """Maximizes volume without clipping by normalizing peaks to 0dB."""

    pogo = EventProp[int](ChannelID.Pogo)
    """Pitch bend effect. Bipolar.

    | Min | Max | Default |
    |-----|-----|---------|
    | 0   | 512 | 256     |
    """

    remove_dc = StructProp[bool](ChannelID.Parameters, prop="fx.remove_dc")
    """Whether DC offset (if present) is removed.

    *New in FL Studio v2.5.0*.
    """

    resonance = EventProp[int](ChannelID.Resonance)
    """Filter Mod Y. Min = 0. Max = 640. Defaults to minimum value."""

    reverb = NestedProp[Reverb](Reverb, ChannelID.Reverb)
    reverse = FlagProp(_FXFlags.Reverse, ChannelID.FXFlags)
    """Whether sample is reversed or not."""

    ringmod = EventProp[Tuple[int, int]](ChannelID.RingMod)
    """Ring modulation returned as a tuple of ``(mix, frequency)``.

    Limits for both:

    | Min | Max | Default |
    |-----|-----|---------|
    | 0   | 256 | 128     |
    """

    start = StructProp[float](ChannelID.Parameters, prop="fx.start")
    """Min = 0.0, Max = 1.0. Defaults to minimum value.

    Always set to 0.0 irrespective of the knob position unless a sample is loaded.
    """

    stereo_delay = EventProp[int](ChannelID.StereoDelay)
    """Linear. Bipolar.

    | Min | Max  | Default |
    |-----|------|---------|
    | 0   | 4096 | 2048    |

    *New in FL Studio v1.3.56*.
    """

    swap_stereo = FlagProp(_FXFlags.SwapStereo, ChannelID.FXFlags)
    """Whether left and right channels are swapped or not."""

    trim = StructProp[int](ChannelID.Parameters, prop="fx.trim")
    """Silence trimming threshold. Defaults to minimum. Linear.

    | Type | Value | Representation |
    |------|-------|----------------|
    | Min  | 0     | 0%             |
    | Max  | 256   | 100%           |
    """


class Envelope(EventModel, ModelReprMixin):
    """A PAHDSR envelope for various :class:`Sampler` paramters.

    ![](https://bit.ly/3d9WCCh)

    See Also:
        :attr:`Sampler.envelopes`

    *New in FL Studio v2.5.0*.
    """

    enabled = StructProp[bool](prop="envelope.enabled")
    """Whether envelope section is enabled."""

    predelay = StructProp[int](prop="envelope.predelay")
    """Linear. Defaults to minimum value.

    | Type | Value | Representation |
    |------|-------|----------------|
    | Min  | 100   | 0%             |
    | Max  | 65536 | 100%           |
    """

    amount = StructProp[int](prop="envelope.amount")
    """Linear. Bipolar.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | -100%          |
    | Max     | 128   | 100%           |
    | Default | 0     | 0%             |
    """

    attack = StructProp[int](prop="envelope.attack")
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 100   | 0%             |
    | Max     | 65536 | 100%           |
    | Default | 20000 | 31%            |
    """

    hold = StructProp[int](prop="envelope.hold")
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 100   | 0%             |
    | Max     | 65536 | 100%           |
    | Default | 20000 | 31%            |
    """

    decay = StructProp[int](prop="envelope.decay")
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 100   | 0%             |
    | Max     | 65536 | 100%           |
    | Default | 30000 | 46%            |
    """

    sustain = StructProp[int](prop="envelope.sustain")
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0%             |
    | Max     | 128   | 100%           |
    | Default | 50    | 39%            |
    """

    release = StructProp[int](prop="envelope.release")
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 100   | 0%             |
    | Max     | 65536 | 100%           |
    | Default | 20000 | 31%            |
    """

    synced = FlagProp(_EnvLFOFlags.EnvelopeTempoSync)
    """Whether envelope is synced to tempo or not."""

    attack_tension = StructProp[int](prop="envelope.attack_tension")
    """Linear. Bipolar.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | -100%          |
    | Max     | 128   | 100%           |
    | Default | 0     | 0%             |

    *New in FL Studio v3.5.4*.
    """

    decay_tension = StructProp[int](prop="envelope.decay_tension")
    """Linear. Bipolar.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | -128  | -100%     |
    | Max     | 128   | 100%      |
    | Default | 0     | 0%        |

    *New in FL Studio v3.5.4*.
    """

    release_tension = StructProp[int](prop="envelope.release_tension")
    """Linear. Bipolar.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | -128  | -100%     |
    | Max     | 128   | 100%      |
    | Default | -101  | -79%      |

    *New in FL Studio v3.5.4*.
    """


class SamplerLFO(EventModel, ModelReprMixin):
    """A basic LFO for certain :class:`Sampler` parameters.

    ![](https://bit.ly/3RG5Jtw)

    See Also:
        :attr:`Sampler.lfos`

    *New in FL Studio v2.5.0*.
    """

    amount = StructProp[int](prop="lfo.amount")
    """Linear. Bipolar.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | -100%          |
    | Max     | 128   | 100%           |
    | Default | 0     | 0%             |
    """

    attack = StructProp[int](prop="lfo.attack")
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 100   | 0%             |
    | Max     | 65536 | 100%           |
    | Default | 20000 | 31%            |
    """

    predelay = StructProp[int](prop="lfo.predelay")
    """Linear. Defaults to minimum value.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 100   | 0%             |
    | Max     | 65536 | 100%           |
    """

    speed = StructProp[int](prop="lfo.speed")
    """Logarithmic. Provides tempo synced options.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 200   | 0%             |
    | Max     | 65536 | 100%           |
    | Default | 32950 | 50% (16 steps) |
    """

    synced = FlagProp(_EnvLFOFlags.LFOTempoSync)
    """Whether LFO is synced with tempo."""

    retrig = FlagProp(_EnvLFOFlags.LFOPhaseRetrig)
    """Whether LFO phase is in global / retriggered mode."""

    shape = StructProp[LFOShape](prop="lfo.shape")
    """Sine, triangle or pulse. Default: Sine."""


class Polyphony(EventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3DlvWcl)
    """

    mono = FlagProp(_PolyphonyFlags.Mono)
    """Whether monophonic mode is enabled or not."""

    porta = FlagProp(_PolyphonyFlags.Porta)
    """*New in FL Studio v3.3.0*."""

    max = StructProp[int]()
    """Max number of voices."""

    slide = StructProp[int]()
    """Portamento time. Nonlinear.

    | Type    | Value | Representation  |
    |---------|-------|-----------------|
    | Min     | 0     | 0:00            |
    | Max     | 1660  | 8:00 (8 steps)  |
    | Default | 820   | 0:12 (1/2 step) |

    *New in FL Studio v3.3.0*.
    """


class Tracking(EventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3DmveM8)

    *New in FL Studio v3.3.0*.
    """

    middle_value = StructProp[int]()
    """Note index. Min: C0 (0), Max: B10 (131)."""

    mod_x = StructProp[int]()
    """Bipolar.

    | Min  | Max | Default |
    |------|-----|---------|
    | -256 | 256 | 0       |
    """

    mod_y = StructProp[int]()
    """Bipolar.

    | Min  | Max | Default |
    |------|-----|---------|
    | -256 | 256 | 0       |
    """

    pan = StructProp[int]()
    """Linear. Bipolar.

    | Min  | Max | Default |
    |------|-----|---------|
    | -256 | 256 | 0       |
    """


class Keyboard(EventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3qwIK8r)

    *New in FL Studio v1.3.56*.
    """

    fine_tune = EventProp[int](ChannelID.FineTune)
    """-100 to +100 cents."""

    # TODO Return this as a note name, like `Note.key`
    root_note = EventProp[int](ChannelID.RootNote, default=60)
    """Min - 0 (C0), Max - 131 (B10)."""

    main_pitch = StructProp[bool](ChannelID.Parameters, prop="keyboard.main_pitch")
    """Whether triggered note is affected by changes to :attr:`Project.main_pitch`."""

    add_root = StructProp[bool](ChannelID.Parameters, prop="keyboard.add_root")
    """Whether to add root note (instead of pitch) to triggered note.

    Named as :guilabel:`Add to key`. Defaults to ``False``.

    *New in FL Studio v3.4.0*.
    """

    key_region = StructProp[Tuple[int, int]](ChannelID.Parameters, prop="keyboard.key_region")
    """A `(start_note, end_note)` tuple representing the playable range."""


class Playback(EventModel, ModelReprMixin):
    """Used by :class:`Sampler`.

    ![](https://bit.ly/3xjSypY)
    """

    ping_pong_loop = EventProp[bool](ChannelID.PingPongLoop)
    start_offset = StructProp[int](ChannelID.Parameters, prop="playback.start_offset")
    """Linear. Defaults to minimum value.

    | Type | Value      | Representation |
    |------|------------|----------------|
    | Min  | 0          | 0%             |
    | Max  | 1072693248 | 100%           |
    """

    use_loop_points = FlagProp(_SamplerFlags.UsesLoopPoints, ChannelID.SamplerFlags)


class TimeStretching(EventModel, ModelReprMixin):
    """Used by :class:`Sampler`.

    ![](https://bit.ly/3eIAjnG)

    *New in FL Studio v5.0*.
    """

    mode = StructProp[StretchMode](ChannelID.Parameters, prop="stretching.mode")
    multiplier = StructProp[float](ChannelID.Parameters, prop="stretching.multiplier")
    """Logarithmic. Bipolar.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0.25  | 25%            |
    | Max     | 4.0   | 400%           |
    | Default | 0     | 100%           |
    """

    pitch = StructProp[int](ChannelID.Parameters, prop="stretching.pitch")
    """Pitch shift (in cents). Min = -1200. Max = 1200. Defaults to 0."""

    time = StructProp[MusicalTime](ChannelID.Parameters, prop="stretching.time")
    """Returns a tuple of ``(bars, beats, ticks)``."""


class Content(EventModel, ModelReprMixin):
    """Used by :class:`Sampler`.

    ![](https://bit.ly/3TCXFKI)
    """

    declick_mode = StructProp[DeclickMode](ChannelID.Parameters, prop="content.declick_mode")
    """Defaults to ``DeclickMode.OutOnly``.

    *New in FL Studio v9.0.0*.
    """

    keep_on_disk = FlagProp(_SamplerFlags.KeepOnDisk, ChannelID.SamplerFlags)
    """Whether a sample is streamed from disk or kept in RAM, defaults to ``False``.

    *New in FL Studio v2.5.0*.
    """

    load_regions = FlagProp(_SamplerFlags.LoadRegions, ChannelID.SamplerFlags)
    """Load regions found in the sample, if any, defaults to ``True``."""

    load_slices = FlagProp(_SamplerFlags.LoadSliceMarkers, ChannelID.SamplerFlags)
    """Defaults to ``False``."""

    resample = FlagProp(_SamplerFlags.Resample, ChannelID.SamplerFlags)
    """Defaults to ``False``.

    *New in FL Studio v2.5.0*.
    """


class AutomationLFO(EventModel, ModelReprMixin):
    amount = StructProp[int](ChannelID.Automation, prop="lfo.amount")
    """Linear. Bipolar.

    | Type    | Value      | Representation |
    |---------|------------|----------------|
    | Min     | -128       | -100%          |
    | Max     | 128        | 100%           |
    | Default | 64 or 0    | 50% or 0%      |
    """


class AutomationPoint(ItemModel[AutomationEvent], ModelReprMixin):
    def __setitem__(self, prop: str, value: Any) -> None:
        self._item[prop] = value
        self._parent["points"][self._index] = self._item

    position = StructProp[int](readonly=True)
    """PPQ dependant. Position on X-axis.

    This property cannot be set as of yet.
    """

    tension = StructProp[float]()
    """A value in the range of 0 to 1.0."""

    value = StructProp[float]()
    """Position on Y-axis in the range of 0 to 1.0."""


class Channel(EventModel):
    """Represents a channel in the channel rack."""

    def __repr__(self) -> str:
        return f"{type(self).__name__} (name={self.display_name!r}, iid={self.iid})"

    color = EventProp[RGBA](PluginID.Color)
    """Defaults to #5C656A (granite gray).

    ![](https://bit.ly/3SllDsG)

    Values below 20 for any color component (R, G or B) are ignored by FL.
    """

    # TODO controllers = KWProp[List[RemoteController]]()
    internal_name = EventProp[str](PluginID.InternalName)
    """Internal name of the channel.

    The value of this depends on the type of `plugin`:

    * Native (stock) plugin: Empty *afaik*.
    * VST instruments: "Fruity Wrapper".

    See Also:
        :attr:`name`
    """

    enabled = EventProp[bool](ChannelID.IsEnabled)
    """![](https://bit.ly/3sbN8KU)"""

    @property
    def group(self) -> DisplayGroup:  # TODO Setter
        """Display group / filter under which this channel is grouped."""
        return self._kw["group"]

    icon = EventProp[int](PluginID.Icon)
    """Internal ID of the icon shown beside the ``display_name``.

    ![](https://bit.ly/3zjK2sf)
    """

    iid = EventProp[int](ChannelID.New)
    keyboard = NestedProp(Keyboard, ChannelID.FineTune, ChannelID.RootNote, ChannelID.Parameters)
    """Located at the bottom of :menuselection:`Miscellaneous functions (page)`."""

    locked = EventProp[bool](ChannelID.IsLocked)
    """Whether in a locked state or not; mute / solo acts differently when ``True``.

    ![](https://bit.ly/3BOBc7j)
    """

    name = EventProp[str](PluginID.Name, ChannelID._Name)
    """The name associated with a channel.

    It's value depends on the type of plugin:

    * Native (stock): User-given name, None if not given one.
    * VST instrument: The name obtained from the VST or the user-given name.

    See Also:
        :attr:`internal_name` and :attr:`display_name`.
    """

    @property
    def pan(self) -> int | None:
        """Linear. Bipolar.

        | Min | Max   | Default |
        |-----|-------|---------|
        | 0   | 12800 | 6400    |
        """
        if ChannelID.Levels in self.events.ids:
            return cast(LevelsEvent, self.events.first(ChannelID.Levels))["pan"]

        for id in (ChannelID._PanWord, ChannelID._PanByte):
            if id in self.events.ids:
                return self.events.first(id).value

    @pan.setter
    def pan(self, value: int) -> None:
        if self.pan is None:
            raise PropertyCannotBeSet

        if ChannelID.Levels in self.events.ids:
            cast(LevelsEvent, self.events.first(ChannelID.Levels))["pan"] = value
            return

        for id in (ChannelID._PanWord, ChannelID._PanByte):
            if id in self.events.ids:
                self.events.first(id).value = value

    @property
    def volume(self) -> int | None:
        """Nonlinear.

        | Min | Max   | Default |
        |-----|-------|---------|
        | 0   | 12800 | 10000   |
        """
        if ChannelID.Levels in self.events.ids:
            return cast(LevelsEvent, self.events.first(ChannelID.Levels))["volume"]

        for id in (ChannelID._VolWord, ChannelID._VolByte):
            if id in self.events.ids:
                return self.events.first(id).value

    @volume.setter
    def volume(self, value: int) -> None:
        if self.volume is None:
            raise PropertyCannotBeSet

        if ChannelID.Levels in self.events.ids:
            cast(LevelsEvent, self.events.first(ChannelID.Levels))["volume"] = value
            return

        for id in (ChannelID._VolWord, ChannelID._VolByte):
            if id in self.events.ids:
                self.events.first(id).value = value

    # If the channel is not zipped, underlying event is not stored.
    @property
    def zipped(self) -> bool:
        """Whether the channel is zipped / minimized.

        ![](https://bit.ly/3S2imib)
        """
        if ChannelID.Zipped in self.events.ids:
            return self.events.first(ChannelID.Zipped).value
        return False

    @property
    def display_name(self) -> str | None:
        """The name of the channel that will be displayed in FL Studio."""
        return self.name or self.internal_name  # type: ignore


class Automation(Channel, ModelCollection[AutomationPoint]):
    """Represents an automation clip present in the channel rack.

    Iterate to get the :attr:`points` inside the clip.

        >>> repr([point for point in automation])
        AutomationPoint(position=0.0, value=1.0, tension=0.5), ...

    ![](https://bit.ly/3RXQhIN)
    """

    @supports_slice  # type: ignore
    def __getitem__(self, i: int | slice) -> AutomationPoint:
        for idx, p in enumerate(self):
            if idx == i:
                return p
        raise ModelNotFound(i)

    def __iter__(self) -> Iterator[AutomationPoint]:
        """Iterator over the automation points inside the automation clip."""
        if ChannelID.Automation in self.events.ids:
            event = cast(AutomationEvent, self.events.first(ChannelID.Automation))
            for i, point in enumerate(event["points"]):
                yield AutomationPoint(point, i, event)

    lfo = NestedProp(AutomationLFO, ChannelID.Automation)  # TODO Add image


class Layer(Channel, ModelCollection[Channel]):
    """Represents a layer channel present in the channel rack.

    ![](https://bit.ly/3S2MLgf)

    *New in FL Studio v3.4.0*.
    """

    @supports_slice  # type: ignore
    def __getitem__(self, i: int | str | slice) -> Channel:
        """Returns a child :class:`Channel` with an IID of :attr:`Channel.iid`.

        Args:
            i: IID or 0-based index of the child(ren).

        Raises:
            ChannelNotFound: Child(ren) with the specific index or IID couldn't
                be found. This exception derives from ``KeyError`` as well.
        """
        for child in self:
            if i == child.iid:
                return child
        raise ChannelNotFound(i)

    def __iter__(self) -> Iterator[Channel]:
        if ChannelID.Children in self.events.ids:
            for event in self.events.get(ChannelID.Children):
                yield self._kw["channels"][event.value]

    def __len__(self) -> int:
        """Returns the number of channels whose parent this layer is."""
        try:
            return self.events.count(ChannelID.Children)
        except KeyError:
            return 0

    def __repr__(self) -> str:
        return f"{super().__repr__()[:-1]}, {len(self)} children)"

    crossfade = FlagProp(_LayerFlags.Crossfade, ChannelID.LayerFlags)
    """:menuselection:`Miscellaneous functions --> Layering`"""

    random = FlagProp(_LayerFlags.Random, ChannelID.LayerFlags)
    """:menuselection:`Miscellaneous functions --> Layering`"""


class _SamplerInstrument(Channel):
    arp = NestedProp(Arp, ChannelID.Parameters)
    """:menuselection:`Miscellaneous functions -> Arpeggiator`"""

    cut_group = EventProp[Tuple[int, int]](ChannelID.CutGroup)
    """Cut group in the form of (Cut self, cut by).

    :menuselection:`Miscellaneous functions --> Group`

    Hint:
        To cut itself when retriggered, set the same value for both.
    """

    delay = NestedProp(Delay, ChannelID.Delay, ChannelID.DelayModXY, ChannelID.Parameters)
    """:menuselection:`Miscellaneous functions -> Echo delay / fat mode`"""

    insert = EventProp[int](ChannelID.RoutedTo)
    """The index of the :class:`Insert` the channel is routed to according to FL.

    "Current" insert = -1, Master = 0 and so on... till :attr:`Mixer.max_inserts`.
    """

    level_adjusts = NestedProp(LevelAdjusts, ChannelID.LevelAdjusts)
    """:menuselection:`Miscellaneous functions -> Level adjustments`"""

    @property
    def pitch_shift(self) -> int | None:
        """-4800 to +4800 (cents).

        Raises:
            PropertyCannotBeSet: When a `ChannelID.Levels` event is not found.
        """
        if ChannelID.Levels in self.events.ids:
            return cast(LevelsEvent, self.events.first(ChannelID.Levels))["pitch_shift"]

    @pitch_shift.setter
    def pitch_shift(self, value: int) -> None:
        try:
            event = self.events.first(ChannelID.Levels)
        except KeyError as exc:
            raise PropertyCannotBeSet(ChannelID.Levels) from exc
        else:
            cast(LevelsEvent, event)["pitch_shift"] = value

    polyphony = NestedProp(Polyphony, ChannelID.Polyphony)
    """:menuselection:`Miscellaneous functions -> Polyphony`"""

    time = NestedProp(Time, ChannelID.Swing, ChannelID.TimeShift, ChannelID.Parameters)
    """:menuselection:`Miscellaneous functions -> Time`"""

    @property
    def tracking(self) -> dict[str, Tracking] | None:
        """A :class:`Tracking` each for Volume & Keyboard.

        :menuselection:`Miscellaneous functions -> Tracking`
        """
        if ChannelID.Tracking in self.events.ids:
            tracking = [Tracking(e) for e in self.events.separate(ChannelID.Tracking)]
            return dict(zip(("volume", "keyboard"), tracking))


class Instrument(_SamplerInstrument):
    """Represents a native or a 3rd party plugin loaded in a channel."""

    plugin = PluginProp(VSTPlugin, BooBass, FruitKick, Plucked)
    """The plugin loaded into the channel."""


# TODO New in FL Studio v1.4.0 & v1.5.23: Sampler spectrum views
class Sampler(_SamplerInstrument):
    """Represents the native Sampler, either as a clip or a channel.

    ![](https://bit.ly/3DlHPiI)
    """

    def __repr__(self) -> str:
        return f"{super().__repr__()[:-1]}, sample_path={self.sample_path!r})"

    au_sample_rate = EventProp[int](ChannelID.AUSampleRate)
    """AU-format sample specific."""

    content = NestedProp(Content, ChannelID.SamplerFlags, ChannelID.Parameters)
    """:menuselection:`Sample settings --> Content`"""

    # FL's interface doesn't have an envelope for panning, but still stores
    # the default values in event data.
    @property
    def envelopes(self) -> dict[EnvelopeName, Envelope] | None:
        """An :class:`Envelope` each for Volume, Panning, Mod X, Mod Y and Pitch.

        :menuselection:`Envelope / instruement settings`
        """
        if ChannelID.EnvelopeLFO in self.events.ids:
            envs = [Envelope(e) for e in self.events.separate(ChannelID.EnvelopeLFO)]
            return dict(zip(EnvelopeName.__args__, envs))  # type: ignore

    filter = NestedProp(Filter, ChannelID.Levels)

    fx = NestedProp(
        FX,
        ChannelID.Cutoff,
        ChannelID.FadeIn,
        ChannelID.FadeOut,
        ChannelID.FreqTilt,
        ChannelID.Parameters,
        ChannelID.Pogo,
        ChannelID.Preamp,
        ChannelID.Resonance,
        ChannelID.Reverb,
        ChannelID.RingMod,
        ChannelID.StereoDelay,
        ChannelID.FXFlags,
    )
    """:menuselection:`Sample settings (page) --> Precomputed effects`"""

    @property
    def lfos(self) -> dict[LFOName, SamplerLFO] | None:
        """An :class:`LFO` each for Volume, Panning, Mod X, Mod Y and Pitch.

        :menuselection:`Envelope / instruement settings (page)`
        """
        if ChannelID.EnvelopeLFO in self.events.ids:
            lfos = [SamplerLFO(e) for e in self.events.separate(ChannelID.EnvelopeLFO)]
            return dict(zip(LFOName.__args__, lfos))  # type: ignore

    playback = NestedProp(
        Playback, ChannelID.SamplerFlags, ChannelID.PingPongLoop, ChannelID.Parameters
    )
    """:menuselection:`Sample settings (page) --> Playback`"""

    @property
    def sample_path(self) -> pathlib.Path | None:
        """Absolute path of a sample file on the disk.

        :menuselection:`Sample settings (page) --> File`

        Contains the string ``%FLStudioFactoryData%`` for stock samples.
        """
        if ChannelID.SamplePath in self.events.ids:
            return pathlib.Path(self.events.first(ChannelID.SamplePath).value)

    @sample_path.setter
    def sample_path(self, value: pathlib.Path) -> None:
        if self.sample_path is None:
            raise PropertyCannotBeSet(ChannelID.SamplePath)

        path = "" if str(value) == "." else str(value)
        self.events.first(ChannelID.SamplePath).value = path

    # TODO Find whether ChannelID._StretchTime was really used for attr ``time``.
    stretching = NestedProp(TimeStretching, ChannelID.Parameters)
    """:menuselection:`Sample settings (page) --> Time stretching`"""


class ChannelRack(EventModel, ModelCollection[Channel]):
    """Represents the channel rack, contains all :class:`Channel` instances.

    ![](https://bit.ly/3RXR50h)
    """

    def __repr__(self) -> str:
        return f"ChannelRack - {len(self)} channels"

    @supports_slice  # type: ignore
    def __getitem__(self, i: str | int | slice) -> Channel:
        """Gets a channel from the rack based on its IID or name.

        Args:
            i: Compared with :attr:`Channel.iid` if an int or
               slice or with the :attr:`Channel.display_name`.

        Raises:
            ChannelNotFound: A channel with the specified IID or name isn't found.
        """
        for ch in self:
            if (isinstance(i, int) and i == ch.iid) or (i == ch.display_name):
                return ch
        raise ChannelNotFound(i)

    def __iter__(self) -> Iterator[Channel]:
        """Yields all the channels found in the project."""
        ch_dict: dict[int, Channel] = {}
        groups = [DisplayGroup(et) for et in self.events.separate(DisplayGroupID.Name)]

        for et in self.events.divide(ChannelID.New, *ChannelID, *PluginID):
            iid = et.first(ChannelID.New).value
            typ = et.first(ChannelID.Type).value
            groupnum = et.first(ChannelID.GroupNum).value

            ct = Channel  # prevent type error and logic failure below
            if typ == ChannelType.Automation:
                ct = Automation
            elif typ == ChannelType.Layer:
                ct = Layer
            elif typ == ChannelType.Sampler:
                ct = Sampler
            elif typ in (ChannelType.Instrument, ChannelType.Native):
                ct = Instrument

            # Audio clips are stored as Instrument until a sample is loaded in them
            if all(id in et for id in (ChannelID.SamplePath, PluginID.InternalName)):
                if not et.first(PluginID.InternalName).value and ct == Instrument:
                    ct = Sampler

            if iid is not None:
                cur_ch = ch_dict[iid] = ct(et, channels=ch_dict, group=groups[groupnum])
                yield cur_ch

    def __len__(self) -> int:
        """Returns the number of channels found in the project.

        Raises:
            NoModelsFound: No channels could be found in the project.
        """
        if ChannelID.New not in self.events.ids:
            raise NoModelsFound
        return self.events.count(ChannelID.New)

    @property
    def automations(self) -> Iterator[Automation]:
        """Yields automation clips in the project."""
        yield from (ch for ch in self if isinstance(ch, Automation))

    # TODO Find out what this meant
    fit_to_steps = EventProp[int](RackID._FitToSteps)

    @property
    def groups(self) -> Iterator[DisplayGroup]:
        for ed in self.events.separate(DisplayGroupID.Name):
            yield DisplayGroup(ed)

    height = EventProp[int](RackID.WindowHeight)
    """Window height of the channel rack in the interface (in pixels)."""

    @property
    def instruments(self) -> Iterator[Instrument]:
        """Yields native and 3rd-party synth channels in the project."""
        yield from (ch for ch in self if isinstance(ch, Instrument))

    @property
    def layers(self) -> Iterator[Layer]:
        """Yields ``Layer`` channels in the project."""
        yield from (ch for ch in self if isinstance(ch, Layer))

    @property
    def samplers(self) -> Iterator[Sampler]:
        """Yields samplers and audio clips in the project."""
        yield from (ch for ch in self if isinstance(ch, Sampler))

    swing = EventProp[int](RackID.Swing)
    """Global channel swing mix. Linear. Defaults to minimum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """
