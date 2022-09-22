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

"""Contains the types used by the channels and channel rack."""

from __future__ import annotations

import collections
import enum
import pathlib
import sys
from typing import DefaultDict, List, Tuple, cast

if sys.version_info >= (3, 8):
    from typing import Final, SupportsIndex
else:
    from typing_extensions import Final, SupportsIndex

if sys.version_info >= (3, 9):
    from collections.abc import Iterator, Sequence
else:
    from typing import Sequence, Iterator

import colour

from ._descriptors import EventProp, FlagProp, KWProp, NestedProp, StructProp
from ._events import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    BoolEvent,
    EventEnum,
    F32Event,
    I8Event,
    I32Event,
    StructBase,
    StructEventBase,
    U8Event,
    U16Event,
    U16TupleEvent,
    U32Event,
)
from ._models import ModelReprMixin, MultiEventModel, SingleEventModel
from .controller import RemoteController
from .exceptions import ModelNotFound, NoModelsFound, PropertyCannotBeSet
from .plugin import (
    BooBass,
    BooBassEvent,
    PluginID,
    PluginProp,
    VSTPlugin,
    VSTPluginEvent,
)

__all__ = [
    "ArpDirection",
    "Automation",
    "Channel",
    "Instrument",
    "Layer",
    "ChannelRack",
    "ChannelNotFound",
    "LFOShape",
    "ReverbType",
    "FX",
    "Reverb",
    "Delay",
    "Envelope",
    "LFO",
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


class ChannelNotFound(ModelNotFound, KeyError):
    pass


class _DelayStruct(StructBase):
    PROPS = dict.fromkeys(("feedback", "pan", "pitch_shift", "echoes", "time"), "I")


class _EnvelopeLFOStruct(StructBase):  # 2.5.0+
    PROPS = {
        "flags": "i",  # 4
        "envelope.enabled": "i",  # 8
        "envelope.predelay": "i",  # 12
        "envelope.attack": "i",  # 16
        "envelope.hold": "i",  # 20
        "envelope.decay": "i",  # 24
        "envelope.sustain": "i",  # 28
        "envelope.release": "i",  # 32
        "_u20": 20,  # 52
        "lfo.shape": "i",  # 56
        "envelope.attack_tension": "i",  # 60
        "envelope.sustain_tension": "i",  # 64
        "envelope.release_tension": "i",  # 68
    }


class _LevelAdjustsStruct(StructBase):
    PROPS = {"pan": "I", "volume": "I", "_u4": 4, "mod_x": "I", "mod_y": "I"}


class _LevelsStruct(StructBase):
    PROPS = {"pan": "I", "volume": "I", "pitch_shift": "I", "_u12": 12}


class _ParametersStruct(StructBase):
    PROPS = {
        "_u40": 40,  # 40
        "arp.direction": "I",  # 44
        "arp.range": "I",  # 48
        "arp.chord": "I",  # 52
        "arp.time": "f",  # 56
        "arp.gate": "f",  # 60
        "arp.slide": "bool",  # 61
        "_u31": 31,  # 92
        "arp.repeat": "I",  # 96 4.5.2+
        "_u12": 12,  # 108
        "stretching.mode": "i",  # 112
        "_u46": 46,  # 158
    }


class _PolyphonyStruct(StructBase):
    PROPS = {"max": "I", "slide": "I", "flags": "B"}


class _TrackingStruct(StructBase):
    PROPS = {"middle_value": "i", "pan": "i", "mod_x": "i", "mod_y": "i"}


class DelayEvent(StructEventBase):
    STRUCT = _DelayStruct


class EnvelopeLFOEvent(StructEventBase):
    STRUCT = _EnvelopeLFOStruct


class LevelAdjustsEvent(StructEventBase):
    STRUCT = _LevelAdjustsStruct


class LevelsEvent(StructEventBase):
    STRUCT = _LevelsStruct


class ParametersEvent(StructEventBase):
    STRUCT = _ParametersStruct


class PolyphonyEvent(StructEventBase):
    STRUCT = _PolyphonyStruct


class TrackingEvent(StructEventBase):
    STRUCT = _TrackingStruct


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
    # Fx = WORD + 5
    FXFlags = (WORD + 6, U16Event)
    Cutoff = (WORD + 7, U16Event)
    _VolWord = (WORD + 8, U16Event)
    _PanWord = (WORD + 9, U16Event)
    Preamp = (WORD + 10, U16Event)  #: 1.2.12+
    FadeOut = (WORD + 11, U16Event)  #: 1.7.6+
    FadeIn = (WORD + 12, U16Event)
    # DotNote = WORD + 13
    # DotPitch = WORD + 14
    # DotMix = WORD + 15
    Resonance = (WORD + 19, U16Event)
    # _LoopBar = WORD + 20
    StereoDelay = (WORD + 21, U16Event)  #: 1.3.56+
    # Fx3 = WORD + 22
    # DotReso = WORD + 23
    # DotCutOff = WORD + 24
    # ShiftDelay = WORD + 25
    # Dot = WORD + 27
    # DotRel = WORD + 32
    # DotShift = WORD + 28
    Children = (WORD + 30, U16Event)  #: 3.4.0+
    Swing = (WORD + 33, U16Event)
    # Echo = DWORD + 2
    # FxSine = DWORD + 3
    CutGroup = (DWORD + 4, U16TupleEvent)
    RootNote = (DWORD + 7, U32Event)
    # _MainResoCutOff = DWORD + 9
    # DelayModXY = DWORD + 10
    Reverb = (DWORD + 11, U32Event)  #: 1.4.0+
    StretchTime = (DWORD + 12, F32Event)  #: 5.0+
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
    Tracking = (DATA + 20, TrackingEvent)
    LevelAdjusts = (DATA + 21, LevelAdjustsEvent)


@enum.unique
class DisplayGroupID(EventEnum):
    Name = TEXT + 39  #: 3.4.0+


@enum.unique
class RackID(EventEnum):
    Swing = (11, U8Event)
    _FitToSteps = (13, U8Event)
    WindowHeight = (DWORD + 5, U32Event)


@enum.unique
class ArpDirection(enum.IntEnum):
    """Used by :attr:`Arp.direction`."""

    Off = 0
    Up = 1
    Down = 2
    UpDownBounce = 3
    UpDownSticky = 4
    Random = 5


@enum.unique
class _LFOFlags(enum.IntFlag):
    TempoSync = 1 << 1
    Unknown = 1 << 2  # Occurs for volume envlope only.
    Retrig = 1 << 5


@enum.unique
class LFOShape(enum.IntEnum):
    """Used by :attr:`LFO.shape`."""

    Sine = 0
    Triangle = 1
    Pulse = 2


@enum.unique
class _PolyphonyFlags(enum.IntFlag):
    None_ = 0
    Mono = 1 << 0
    Porta = 1 << 1

    # Unknown
    U1 = 1 << 2
    U2 = 1 << 3
    U3 = 1 << 4
    U4 = 1 << 5
    U5 = 1 << 6
    U6 = 1 << 7


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
class ChannelType(enum.IntEnum):  # cuz Type would be a super generic name
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


class StretchMode(enum.IntEnum):
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


class DisplayGroup(MultiEventModel, ModelReprMixin):
    def __repr__(self):
        if self.name is None:
            return "Unnamed display group"
        return f"Display group {self.name}"

    name = EventProp[str](DisplayGroupID.Name)


class Arp(SingleEventModel, ModelReprMixin):
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


class Delay(SingleEventModel, ModelReprMixin):
    """Echo delay / fat mode section.

    Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3RyzbBD)
    """

    # is_fat_mode: Optional[bool] = None    #: 3.4.0+
    # is_ping_pong: Optional[bool] = None   #: 1.7.6+
    # mod_x: Optional[int] = None
    # mod_y: Optional[int] = None

    echoes = StructProp[int]()
    """Number of echoes generated for each note."""

    feedback = StructProp[int]()
    """Factor with which the volume of every next echo is multiplied."""

    pan = StructProp[int]()
    pitch_shift = StructProp[int]()
    time = StructProp[int]()


class LevelAdjusts(SingleEventModel, ModelReprMixin):
    """Used by :class:`Layer`, :class:`Instrument` and :class:`Sampler`.

    ![](https://bit.ly/3xkKeGn)

    *New in FL Studio v3.3.0*.
    """

    mod_x = StructProp[int]()
    mod_y = StructProp[int]()
    pan = StructProp[int]()
    volume = StructProp[int]()


class Time(MultiEventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3xjxUGG)
    """

    swing = EventProp[int](ChannelID.Swing)
    # gate: int
    # shift: int
    # is_full_porta: bool


class Reverb(SingleEventModel, ModelReprMixin):
    """Precalculated reverb used by :class:`Sampler`.

    ![](https://bit.ly/3L9N4nj)

    *New in FL Studio v1.4.0*.
    """

    @property
    def type(self) -> ReverbType | None:
        if self._event:
            return ReverbType.B if self._event.value >= ReverbType.B else ReverbType.A

    @type.setter
    def type(self, value: ReverbType):
        if self.mix is None:
            raise PropertyCannotBeSet(ChannelID.Reverb)

        self._event.value = value.value + self.mix

    @property
    def mix(self) -> int | None:
        """Mix % (wet). Defaults to minimum value.

        | Min | Max |
        |-----|-----|
        | 0   | 256 |
        """
        if self._event:
            return self._event.value - self.type

    @mix.setter
    def mix(self, value: int):
        if self._event is None:
            raise PropertyCannotBeSet(ChannelID.Reverb)

        self._event.value += value


class FX(MultiEventModel, ModelReprMixin):
    """Pre-calculated effects used by :class:`Sampler`.

    ![](https://bit.ly/3U3Ys8l)
    ![](https://bit.ly/3qvdBSN)

    See Also:
        :attr:`Sampler.fx`
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

    cutoff = EventProp[int](ChannelID.Cutoff)
    """Filter Mod X. Defaults to maximum value.

    | Min | Max  |
    |-----|------|
    | 0   | 1024 |
    """

    fade_in = EventProp[int](ChannelID.FadeIn)
    """Quick fade-in. Defaults to minimum value.

    | Min | Max  |
    |-----|------|
    | 0   | 1024 |
    """

    fade_out = EventProp[int](ChannelID.FadeOut)
    """Quick fade-out. Defaults to minimum value.

    | Min | Max  |
    |-----|------|
    | 0   | 1024 |

    *New in FL Studio v1.7.6*.
    """

    fade_stereo = FlagProp(_FXFlags.FadeStereo, ChannelID.FXFlags)
    resonance = EventProp[int](ChannelID.Resonance)
    """Filter Mod Y. Defaults to minimum value.

    | Min | Max  |
    |-----|------|
    | 0   | 1024 |
    """

    reverb = NestedProp[Reverb](Reverb, ChannelID.Reverb)
    reverse = FlagProp(_FXFlags.Reverse, ChannelID.FXFlags)
    """Whether sample is reversed or not."""

    stereo_delay = EventProp[int](ChannelID.StereoDelay)
    """*New in FL Studio v1.3.56*."""

    swap_stereo = FlagProp(_FXFlags.SwapStereo, ChannelID.FXFlags)
    """Whether left and right channels are swapped or not."""


class Envelope(SingleEventModel, ModelReprMixin):
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

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 100   | 0%        |
    | Max  | 65536 | 100%      |
    """

    attack = StructProp[int](prop="envelope.attack")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 100   | 0%        |
    | Max     | 65536 | 100%      |
    | Default | 20000 | 31%       |
    """

    hold = StructProp[int](prop="envelope.hold")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 100   | 0%        |
    | Max     | 65536 | 100%      |
    | Default | 20000 | 31%       |
    """

    decay = StructProp[int](prop="envelope.decay")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 100   | 0%        |
    | Max     | 65536 | 100%      |
    | Default | 30000 | 46%       |
    """

    sustain = StructProp[int](prop="envelope.sustain")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 0     | 0%        |
    | Max     | 128   | 100%      |
    | Default | 50    | 39%       |
    """

    release = StructProp[int](prop="envelope.release")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 100   | 0%        |
    | Max     | 65536 | 100%      |
    | Default | 20000 | 31%       |
    """

    attack_tension = StructProp[int](prop="envelope.attack_tension")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | -128  | -100%     |
    | Max     | 128   | 100%      |
    | Default | 0     | 0%        |

    *New in FL Studio v3.5.4*.
    """

    sustain_tension = StructProp[int](prop="envelope.sustain_tension")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | -128  | -100%     |
    | Max     | 128   | 100%      |
    | Default | 0     | 0%        |

    *New in FL Studio v3.5.4*.
    """

    release_tension = StructProp[int](prop="envelope.release_tension")
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | -128  | -100%     |
    | Max     | 128   | 100%      |
    | Default | -101  | -79%      |

    *New in FL Studio v3.5.4*.
    """


class LFO(SingleEventModel, ModelReprMixin):
    """A basic LFO for certain :class:`Sampler` parameters.

    ![](https://bit.ly/3RG5Jtw)

    See Also:
        :attr:`Sampler.lfos`

    *New in FL Studio v2.5.0*.
    """

    # amount: Optional[int] = None
    # attack: Optional[int] = None
    # predelay: Optional[int] = None
    # speed: Optional[int] = None

    is_synced = FlagProp(_LFOFlags.TempoSync)
    """Whether LFO is synced with tempo."""

    is_retrig = FlagProp(_LFOFlags.Retrig)
    """Whether LFO phase is in global / retriggered mode."""

    shape = StructProp[LFOShape](prop="lfo.shape")
    """Sine, triangle or pulse. Default: Sine."""


class Polyphony(SingleEventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3DlvWcl)
    """

    is_mono = FlagProp(_PolyphonyFlags.Mono)
    is_porta = FlagProp(_PolyphonyFlags.Porta)
    """*New in FL Studio v3.3.0*."""

    max = StructProp[int]()
    slide = StructProp[int]()
    """*New in FL Studio v3.3.0*."""


class Tracking(SingleEventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3DmveM8)

    *New in FL Studio v3.3.0*.
    """

    middle_value = StructProp[int]()
    mod_x = StructProp[int]()
    mod_y = StructProp[int]()
    pan = StructProp[int]()


class Keyboard(MultiEventModel, ModelReprMixin):
    """Used by :class:`Sampler` and :class:`Instrument`.

    ![](https://bit.ly/3qwIK8r)

    *New in FL Studio v1.3.56*.
    """

    fine_tune = EventProp[int](ChannelID.FineTune)
    """-100 to +100 cents."""

    root_note = EventProp[int](ChannelID.RootNote)
    """Min - 0 (C0), Max - 131 (B10)."""

    # main_pitch_enabled = StructProp[bool](ChannelID.Parameters)
    # """Whether triggered note is affected by changes to `project.main_pitch`."""

    # added_to_key = StructProp[bool](ChannelID.Parameters)
    # """Whether root note should be added to triggered note instead of pitch.
    #
    # *New in FL Studio v3.4.0*.
    # """

    # note_range: tuple[int] - Should be a 2-short or 2-byte tuple


class Playback(MultiEventModel, ModelReprMixin):
    """Used by :class:`Sampler`.

    ![](https://bit.ly/3xjSypY)
    """

    ping_pong_loop = EventProp[bool](ChannelID.PingPongLoop)
    # start_offset: int
    use_loop_points = FlagProp(_SamplerFlags.UsesLoopPoints, ChannelID.SamplerFlags)


class TimeStretching(MultiEventModel, ModelReprMixin):
    """Used by :class:`Sampler`.

    ![](https://bit.ly/3eIAjnG)

    *New in FL Studio v5.0*.
    """

    mode = StructProp[StretchMode](ChannelID.Parameters, prop="stretching.mode")
    # multiplier: Optional[int] = None
    # pitch: Optional[int] = None
    time = EventProp[float](ChannelID.StretchTime)


class Content(MultiEventModel, ModelReprMixin):
    """Used by :class:`Sampler`."""

    # declick_mode: enum
    keep_on_disk = FlagProp(_SamplerFlags.KeepOnDisk, ChannelID.SamplerFlags)
    load_regions = FlagProp(_SamplerFlags.LoadRegions, ChannelID.SamplerFlags)
    load_slices = FlagProp(_SamplerFlags.LoadSliceMarkers, ChannelID.SamplerFlags)
    resample = FlagProp(_SamplerFlags.Resample, ChannelID.SamplerFlags)


class Channel(MultiEventModel, SupportsIndex):
    """Represents a channel in the channel rack."""

    def __repr__(self):
        if self.display_name is None:
            return f"Unnamed {type(self).__name__.lower()} #{self.iid}"
        return f"{type(self).__name__} {self.display_name!r} #{self.iid}"

    def __index__(self):
        return cast(int, self.iid)

    color = EventProp[colour.Color](PluginID.Color)
    """Defaults to #5C656A (granite gray).

    Values below 20 for any color component (R, G or B) are ignored by FL.
    """

    controllers = KWProp[List[RemoteController]]()
    internal_name = EventProp[str](PluginID.InternalName)
    """Internal name of the channel.

    The value of this depends on the type of `plugin`:

    * Native (stock) plugin: Empty *afaik*.
    * VST instruments: "Fruity Wrapper".

    See Also:
        :attr:`name`
    """

    # TODO Add link to GIF from docs once Bitly quota is available again.
    enabled = EventProp[bool](ChannelID.IsEnabled)
    group = KWProp[DisplayGroup]()
    """Display group / filter under which this channel is grouped."""

    icon = EventProp[int](PluginID.Icon)
    iid = EventProp[int](ChannelID.New)
    keyboard = NestedProp(Keyboard, ChannelID.FineTune, ChannelID.RootNote)
    locked = EventProp[bool](ChannelID.IsLocked)
    """![](https://bit.ly/3BOBc7j)"""

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
        """
        | Min | Max   | Default |
        |-----|-------|---------|
        | 0   | 12800 | 10000   |
        """  # noqa
        if ChannelID.Levels in self._events:
            return cast(LevelsEvent, self._events[ChannelID.Levels][0])["pan"]

        for id in (ChannelID._PanWord, ChannelID._PanByte):
            events = self._events.get(id)
            if events is not None:
                return events[0].value

    @pan.setter
    def pan(self, value: int) -> None:
        if self.pan is None:
            raise AttributeError

        events = self._events.get(ChannelID.Levels)
        if events is not None:
            cast(LevelsEvent, events[0])["pan"] = value
            return

        for id in (ChannelID._PanWord, ChannelID._PanByte):
            events = self._events.get(id)
            if events is not None:
                events[0].value = value

    @property
    def volume(self) -> int | None:
        """
        | Min | Max   | Default |
        |-----|-------|---------|
        | 0   | 12800 | 10000   |
        """  # noqa
        if ChannelID.Levels in self._events:
            return cast(LevelsEvent, self._events[ChannelID.Levels][0])["volume"]

        for id in (ChannelID._VolWord, ChannelID._VolByte):
            events = self._events.get(id)
            if events is not None:
                return events[0].value

    @volume.setter
    def volume(self, value: int) -> None:
        if self.volume is None:
            raise AttributeError

        events = self._events.get(ChannelID.Levels)
        if events is not None:
            cast(LevelsEvent, events[0])["volume"] = value

        for id in (ChannelID._VolWord, ChannelID._VolByte):
            events = self._events.get(id)
            if events is not None:
                events[0].value = value

    # If the channel is not zipped, underlying event is not stored.
    @property
    def zipped(self) -> bool:
        """Whether the channel is in zipped state.

        ![](https://bit.ly/3S2imib)
        """
        if ChannelID.Zipped in self._events:
            return self._events[ChannelID.Zipped][0].value
        return False

    @property
    def display_name(self) -> str | None:
        """The name of the channel that will be displayed in FL Studio."""
        return self.name or self.internal_name


class Automation(Channel):
    """Represents an automation clip present in the channel rack.

    ![](https://bit.ly/3RXQhIN)
    """


class Layer(Channel, Sequence[Channel]):
    """Represents a layer channel present in the channel rack.

    ![](https://bit.ly/3S2MLgf)

    *New in FL Studio v3.4.0*.
    """

    def __getitem__(self, index: str | SupportsIndex):
        """Returns a child channel with an IID / index of :attr:`~Channel.iid`.

        Args:
            index (str | SupportsIndex): An IID or a zero based index of the child
                channel.

        Raises:
            ChannelNotFound: A child channel with the specific index or IID
                couldn't be found. This exception derives from `KeyError` as well.
        """
        for idx, child in enumerate(self):
            if index in (idx, child.iid):
                return child
        raise ChannelNotFound(index)

    def __iter__(self) -> Iterator[Channel]:
        if ChannelID.Children in self._events:
            for event in self._events[ChannelID.Children]:
                yield self._kw["channels"][event.value]

    def __len__(self):
        """Returns the number of channels whose parent this layer is."""
        return len(self._events.get(ChannelID.Children, []))

    crossfade = FlagProp(_LayerFlags.Crossfade, ChannelID.LayerFlags)
    random = FlagProp(_LayerFlags.Random, ChannelID.LayerFlags)


class _SamplerInstrument(Channel):
    arp = NestedProp(Arp, ChannelID.Parameters)
    delay = NestedProp(Delay, ChannelID.Delay)
    insert = EventProp[int](ChannelID.RoutedTo)
    """The index of the :class:`Insert` the channel is routed to. Min = -1."""

    level_adjusts = NestedProp(LevelAdjusts, ChannelID.LevelAdjusts)
    polyphony = NestedProp(Polyphony, ChannelID.Polyphony)
    time = NestedProp(Time, ChannelID.Swing)

    @property
    def tracking(self) -> dict[str, Tracking] | None:
        """A :class:`Tracking` each for Volume & Keyboard."""
        events = self._events.get(ChannelID.Tracking)
        if events is not None:
            tracking = [Tracking(e) for e in events]
            return dict(zip(("volume", "keyboard"), tracking))


class Instrument(_SamplerInstrument):
    """Represents a native or a 3rd party plugin loaded in a channel."""

    plugin = PluginProp({VSTPluginEvent: VSTPlugin, BooBassEvent: BooBass})
    """The plugin loaded into the channel."""


# TODO New in FL Studio v1.4.0 & v1.5.23: Sampler spectrum views
class Sampler(_SamplerInstrument):
    """Represents the native Sampler, either as a clip or a channel.

    ![](https://bit.ly/3DlHPiI)
    """

    _ENVLFO_NAMES: Final = ("Panning", "Volume", "Mod X", "Mod Y", "Pitch")

    def __repr__(self):
        return f"{super().__repr__()} has {repr(self.sample_path) or 'Empty'}"

    au_sample_rate = EventProp[int](ChannelID.AUSampleRate)
    """AU-format sample specific."""

    content = NestedProp(Content, ChannelID.SamplerFlags)
    cut_group = EventProp[Tuple[int, int]](ChannelID.CutGroup)
    """Cut group in the form of (Cut self, cut by)."""

    # FL's interface doesn't have an envelope for panning, but still stores
    # the default values in event data.
    @property
    def envelopes(self) -> dict[str, Envelope] | None:
        """An :class:`Envelope` each for Volume, Panning, Mod X, Mod Y and Pitch."""
        events = self._events.get(ChannelID.EnvelopeLFO)
        if events is not None:
            envelopes = [Envelope(e) for e in events]
            return dict(zip(self._ENVLFO_NAMES, envelopes))

    fx = NestedProp(
        FX,
        ChannelID.Cutoff,
        ChannelID.FadeIn,
        ChannelID.FadeOut,
        ChannelID.Preamp,
        ChannelID.Resonance,
        ChannelID.StereoDelay,
        ChannelID.FXFlags,
    )

    @property
    def lfos(self) -> dict[str, LFO] | None:
        """An :class:`LFO` each for Volume, Panning, Mod X, Mod Y and Pitch."""
        events = self._events.get(ChannelID.EnvelopeLFO)
        if events is not None:
            return dict(zip(self._ENVLFO_NAMES, [LFO(e) for e in events]))

    @property
    def pitch_shift(self) -> int | None:
        """-4800 to +4800 cents.

        Raises:
            PropertyCannotBeSet: When a `ChannelID.Levels` event is not found.
        """
        if ChannelID.Levels in self._events:
            return cast(LevelsEvent, self._events[ChannelID.Levels][0])["pitch_shift"]

    @pitch_shift.setter
    def pitch_shift(self, value: int):
        try:
            event = self._events[ChannelID.Levels][0]
        except KeyError as exc:
            raise PropertyCannotBeSet(ChannelID.Levels) from exc
        else:
            cast(LevelsEvent, event)["pitch_shift"] = value

    playback = NestedProp(Playback, ChannelID.SamplerFlags, ChannelID.PingPongLoop)

    @property
    def sample_path(self) -> pathlib.Path | None:
        """Absolute path of a sample file on the disk.

        Contains the string `%FLStudioFactoryData%` for stock samples.
        """
        events = self._events.get(ChannelID.SamplePath)
        if events is not None:
            return pathlib.Path(events[0].value)

    @sample_path.setter
    def sample_path(self, value: pathlib.Path):
        if self.sample_path is None:
            raise PropertyCannotBeSet(ChannelID.SamplePath)

        path = "" if str(value) == "." else str(value)
        self._events[ChannelID.SamplePath][0].value = path

    stretching = NestedProp(
        TimeStretching,
        ChannelID.StretchTime,
        ChannelID.Parameters,
    )


class ChannelRack(MultiEventModel, Sequence[Channel]):
    """Represents the channel rack, contains all :class:`Channel` instances.

    ![](https://bit.ly/3RXR50h)
    """

    def __repr__(self) -> str:
        return f"ChannelRack - {len(self)} channels"

    def __getitem__(self, index: str | SupportsIndex):
        """Gets a channel from the rack based on its IID or index.

        Args:
            index (str | SupportsIndex): Compared with :attr:`Channel.iid` if
                a string or the index of the order in which channels are found.

        Raises:
            ChannelNotFound: A :class:`Channel` with an IID or index of
                :attr:`index` isn't found.
        """
        for idx, channel in enumerate(self):
            if (isinstance(index, str) and int(index) == channel.iid) or (index == idx):
                return channel
        raise ChannelNotFound(index)

    def __iter__(self):  # pylint: disable=too-complex
        ch_dict: dict[int, Channel] = {}
        events: DefaultDict[int, list[AnyEvent]] = collections.defaultdict(list)
        cur_ch_events = []
        for event in self._events_tuple:
            if event.id == ChannelID.New:
                cur_ch_events = events[event.value]

            if event.id not in RackID:
                cur_ch_events.append(event)

        for iid, ch_events in events.items():
            ct = Channel  # In case an older version doesn't have ChannelID.Type
            for event in ch_events:
                if event.id == ChannelID.Type:
                    if event.value == ChannelType.Automation:
                        ct = Automation
                    elif event.value == ChannelType.Layer:
                        ct = Layer
                    elif event.value == ChannelType.Sampler:
                        ct = Sampler
                    elif event.value in (ChannelType.Instrument, ChannelType.Native):
                        ct = Instrument
                elif (
                    event.id == ChannelID.SamplePath
                    or (event.id == PluginID.InternalName and not event.value)
                    and ct == Instrument
                ):
                    ct = Sampler  # see #40

            if ct is not None:
                cur_ch = ch_dict[iid] = ct(*ch_events, channels=ch_dict)
                yield cur_ch

    def __len__(self):
        """Returns the number of channels found in the project.

        Raises:
            NoModelsFound: No channels could be found in the project.
        """
        if ChannelID.New not in self._events:
            raise NoModelsFound
        return len(self._events[ChannelID.New])

    @property
    def automations(self) -> Iterator[Automation]:
        for channel in self:
            if isinstance(channel, Automation):
                yield channel

    fit_to_steps = EventProp[int](RackID._FitToSteps)

    @property
    def groups(self) -> Iterator[DisplayGroup]:
        if DisplayGroupID.Name in self._events:
            for event in self._events[DisplayGroupID.Name]:
                yield DisplayGroup(event)

    height = EventProp[int](RackID.WindowHeight)
    """Window height of the channel rack in the interface (in pixels)."""

    @property
    def instruments(self) -> Iterator[Instrument]:
        for channel in self:
            if isinstance(channel, Instrument):
                yield channel

    @property
    def layers(self) -> Iterator[Layer]:
        for channel in self:
            if isinstance(channel, Layer):
                yield channel

    @property
    def samplers(self) -> Iterator[Sampler]:
        for channel in self:
            if isinstance(channel, Sampler):
                yield channel

    swing = EventProp[int](RackID.Swing)
    """Global channel swing mix. Linear. Defaults to minimum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """
