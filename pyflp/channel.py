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

"""
pyflp.channel
=============

Contains the types used by the channels and channel rack.
"""

import collections
import enum
import sys
from typing import (
    DefaultDict,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sized,
    Tuple,
    cast,
)

if sys.version_info >= (3, 8):
    from typing import final
else:
    from typing_extensions import final

import colour

from ._base import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    BoolEvent,
    EventEnum,
    EventProp,
    F32Event,
    FlagProp,
    I8Event,
    I32Event,
    IterProp,
    KWProp,
    ModelReprMixin,
    MultiEventModel,
    NestedProp,
    SingleEventModel,
    StructBase,
    StructEventBase,
    StructProp,
    U8Event,
    U16Event,
    U16TupleEvent,
    U32Event,
)
from .controller import RemoteController
from .exceptions import PropertyCannotBeSet
from .plugin import IPlugin, PluginID

__all__ = ["Automation", "Channel", "Instrument", "Layer", "Rack"]


class DelayStruct(StructBase):
    PROPS = dict.fromkeys(("feedback", "pan", "pitch_shift", "echoes", "time"), "I")


class EnvelopeLFOStruct(StructBase):
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


class LevelAdjustsStruct(StructBase):
    PROPS = {"pan": "I", "volume": "I", "_u4": 4, "mod_x": "I", "mod_y": "I"}


class LevelsStruct(StructBase):
    PROPS = {"pan": "I", "volume": "I", "pitch_shift": "I", "_u12": 12}


class ParametersStruct(StructBase):
    PROPS = {
        "_u40": 40,  # 40
        "arp.direction": "I",  # 44
        "arp.range": "I",  # 48
        "arp.chord": "I",  # 52
        "arp.time": "f",  # 56
        "arp.gate": "f",  # 60
        "arp.slide": "bool",  # 61
        "_u31": 31,  # 92
        "arp.repeat": "I",  # 96
    }


class PolyphonyStruct(StructBase):
    PROPS = {"max": "I", "slide": "I", "flags": "B"}


class TrackingStruct(StructBase):
    PROPS = {"middle_value": "i", "pan": "i", "mod_x": "i", "mod_y": "i"}


@final
class DelayEvent(StructEventBase):
    STRUCT = DelayStruct


@final
class EnvelopeLFOEvent(StructEventBase):
    STRUCT = EnvelopeLFOStruct


@final
class LevelAdjustsEvent(StructEventBase):
    STRUCT = LevelAdjustsStruct


@final
class LevelsEvent(StructEventBase):
    STRUCT = LevelsStruct


@final
class ParametersEvent(StructEventBase):
    STRUCT = ParametersStruct


@final
class PolyphonyEvent(StructEventBase):
    STRUCT = PolyphonyStruct


@final
class TrackingEvent(StructEventBase):
    STRUCT = TrackingStruct


@enum.unique
class ChannelID(EventEnum):
    IsEnabled = (0, BoolEvent)
    _VolByte = (2, U8Event)
    _PanByte = (3, U8Event)
    Zipped = (15, BoolEvent)
    UsesLoopPoints = (19, BoolEvent)
    Type = (21, U8Event)
    RoutedTo = (22, I8Event)
    # FXProperties = 27
    IsLocked = (32, BoolEvent)  # FL12.3+
    New = (WORD, U16Event)
    # Fx = WORD + 5
    # FadeStereo = WORD + 6
    Cutoff = (WORD + 7, U16Event)
    _VolWord = (WORD + 8, U16Event)
    _PanWord = (WORD + 9, U16Event)
    Preamp = (WORD + 10, U16Event)
    FadeOut = (WORD + 11, U16Event)
    FadeIn = (WORD + 12, U16Event)
    # DotNote = WORD + 13
    # DotPitch = WORD + 14
    # DotMix = WORD + 15
    Resonance = (WORD + 19, U16Event)
    # _LoopBar = WORD + 20
    StereoDelay = (WORD + 21, U16Event)
    # Fx3 = WORD + 22
    # DotReso = WORD + 23
    # DotCutOff = WORD + 24
    # ShiftDelay = WORD + 25
    # Dot = WORD + 27
    # DotRel = WORD + 32
    # DotShift = WORD + 28
    Children = (WORD + 30, U16Event)
    Swing = (WORD + 33, U16Event)
    # Echo = DWORD + 2
    # FxSine = DWORD + 3
    CutGroup = (DWORD + 4, U16TupleEvent)
    RootNote = (DWORD + 7, U32Event)
    # _MainResoCutOff = DWORD + 9
    # DelayModXY = DWORD + 10
    Reverb = (DWORD + 11, U32Event)
    StretchTime = (DWORD + 12, F32Event)
    FineTune = (DWORD + 14, I32Event)
    SamplerFlags = (DWORD + 15, U32Event)
    LayerFlags = (DWORD + 16, U32Event)
    GroupNum = (DWORD + 17, I32Event)
    AUSampleRate = (DWORD + 25, U32Event)
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
    Name = TEXT + 39


@enum.unique
class RackID(EventEnum):
    Swing = (11, U8Event)
    _FitToSteps = (13, U8Event)


@enum.unique
class ArpDirection(enum.IntEnum):
    Off = 0
    Up = 1
    Down = 2
    UpDownBounce = 3
    UpDownSticky = 4
    Random = 5


@enum.unique
class LFOFlags(enum.IntFlag):
    TempoSync = 1 << 1
    Unknown = 1 << 2  # Occurs for volume envlope only.
    Retrig = 1 << 5


@enum.unique
class LFOShape(enum.IntEnum):
    Sine = 0
    Triangle = 1
    Pulse = 2


@enum.unique
class PolyphonyFlags(enum.IntFlag):
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
    A = 0
    B = 65536


@enum.unique
class ChannelType(enum.IntEnum):  # cuz Type would be a super generic name
    """An internal marker used to indicate the type of a channel.

    !!! info "Internal details"
        The type of a channel may decide how a certain event is interpreted.
        An example of this is `ChannelID.Levels` event, which is used for
        storing volume, pan and pich bend range of any channel other than
        automations. In automations it is used for **Min** and **Max** knobs.
    """

    Sampler = 0
    Native = 2  # Used by audio clips and other native FL Studio synths
    Layer = 3
    Instrument = 4
    Automation = 5


class DisplayGroup(MultiEventModel, ModelReprMixin):
    def __repr__(self):
        if self.name is None:
            return "Unnamed display group"
        return f"Display group {self.name}"

    name = EventProp[str](DisplayGroupID.Name)


class Arp(SingleEventModel, ModelReprMixin):
    chord = StructProp[int]()
    """Index of the selected arpeggio chord."""

    direction = StructProp[ArpDirection]()
    gate = StructProp[float]()
    """Delay between two successive notes played."""

    range = StructProp[int]()
    """Range (in octaves)."""

    repeat = StructProp[int]()
    """Number of times a note is repeated."""

    slide = StructProp[bool]()
    """Whether arpeggio will slide between notes."""

    time = StructProp[float]()
    """Delay between two successive notes played."""


class Delay(SingleEventModel, ModelReprMixin):
    # is_fat_mode: Optional[bool] = None
    # is_ping_pong: Optional[bool] = None
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
    mod_x = StructProp[int]()
    mod_y = StructProp[int]()
    pan = StructProp[int]()
    volume = StructProp[int]()


class Time(MultiEventModel, ModelReprMixin):
    swing = EventProp[int](ChannelID.Swing)
    # gate: int
    # shift: int
    # is_full_porta: bool


class Reverb(SingleEventModel, ModelReprMixin):
    @property
    def type(self) -> Optional[ReverbType]:
        ...

    @property
    def mix(self) -> Optional[int]:
        """Reverb mix (dry/wet). Min: 0, Max: 256, Default: 0."""


class FX(MultiEventModel, ModelReprMixin):
    boost = EventProp[int](ChannelID.Preamp)
    """Pre-amp gain (named ==BOOST==).

    | Property | Value |
    | :------- | :---: |
    | Min      | 0     |
    | Max      | 256   |
    | Default  | 0     |
    """

    cutoff = EventProp[int](ChannelID.Cutoff)
    """Filter Mod X (named ==CUT==).

    | Property | Value |
    | :------- | :---: |
    | Min      | 0     |
    | Max      | 1024  |
    | Default  | 1024  |
    """

    fade_in = EventProp[int](ChannelID.FadeIn)
    """Quick fade-in (named ==IN==).

    | Property | Value |
    | :------- | :---: |
    | Min      | 0     |
    | Max      | 1024  |
    | Default  | 0     |
    """

    fade_out = EventProp[int](ChannelID.FadeOut)
    """Quick fade-out (named ==OUT==).

    | Property | Value |
    | :------- | :---: |
    | Min      | 0     |
    | Max      | 1024  |
    | Default  | 0     |
    """

    resonance = EventProp[int](ChannelID.Resonance)
    """Filter Mod Y (named ==RES==).

    | Property | Value |
    | :------- | :---: |
    | Min      | 0     |
    | Max      | 1024  |
    | Default  | 0     |
    """

    reverb = NestedProp[Reverb](Reverb, ChannelID.Reverb)
    stereo_delay = EventProp[int](ChannelID.StereoDelay)


class Envelope(SingleEventModel, ModelReprMixin):
    enabled = StructProp[bool](prop="envelope.enabled")
    """Whether envelope section is enabled."""

    predelay = StructProp[int](prop="envelope.predelay")
    """Min: 100 (0%), Max: 65536 (100%), Default: 100 (0%)."""

    attack = StructProp[int](prop="envelope.attack")
    """Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    hold = StructProp[int](prop="envelope.hold")
    """Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    decay = StructProp[int](prop="envelope.decay")
    """Min: 100 (0%), Max: 65536 (100%), Default: 30000 (46%)."""

    sustain = StructProp[int](prop="envelope.sustain")
    """Min: 0 (0%), Max: 128 (100%), Default: 50 (39%)."""

    release = StructProp[int](prop="envelope.release")
    """Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    attack_tension = StructProp[int](prop="envelope.attack_tension")
    """Min: -128 (-100%), Max: 128 (100%), Default: 0 (0%)."""

    sustain_tension = StructProp[int](prop="envelope.sustain_tension")
    """Min: -128 (-100%), Max: 128 (100%), Default: 0 (0%)."""

    release_tenstion = StructProp[int](prop="envelope.release_tension")
    """Min: -128 (-100%), Max: 128 (100%), Default: -101 / 0 (-79% / 0%)."""


class LFO(SingleEventModel, ModelReprMixin):
    # amount: Optional[int] = None
    # attack: Optional[int] = None
    # predelay: Optional[int] = None
    # speed: Optional[int] = None

    is_synced = FlagProp(LFOFlags.TempoSync)
    """Whether LFO is synced with tempo."""

    is_retrig = FlagProp(LFOFlags.Retrig)
    """Whether LFO phase is in global / retriggered mode."""

    shape = StructProp[LFOShape](prop="lfo.shape")
    """Sine, triangle or pulse. Default: Sine."""


class Polyphony(SingleEventModel, ModelReprMixin):
    is_mono = FlagProp(PolyphonyFlags.Mono)
    is_porta = FlagProp(PolyphonyFlags.Porta)
    max = StructProp[int]()
    slide = StructProp[int]()


class Tracking(SingleEventModel, ModelReprMixin):
    middle_value = StructProp[int]()
    mod_x = StructProp[int]()
    mod_y = StructProp[int]()
    pan = StructProp[int]()


class Keyboard(MultiEventModel, ModelReprMixin):
    fine_tune = EventProp[int](ChannelID.FineTune)
    """-100 to +100 cents."""

    root_note = EventProp[int](ChannelID.RootNote)
    """Min: 0 (C0), Max: 131 (B10)."""

    # is_main_pitch_enabled: Optional[bool] = None
    # """Whether triggered note is affected by changes to `project.main_pitch`."""

    # is_added_to_key: Optional[bool] = None
    # """Whether root note should be added to triggered note instead of pitch."""

    # note_range: tuple[int] - Should be a 2-short or 2-byte tuple


class Playback(MultiEventModel, ModelReprMixin):
    # ping_pong_loop: bool
    # start_offset: int
    use_loop_points = EventProp[bool](ChannelID.UsesLoopPoints)


class TimeStretching(MultiEventModel, ModelReprMixin):
    # mode: enum
    # multiplier: Optional[int] = None
    # pitch: Optional[int] = None
    time = EventProp[float](ChannelID.StretchTime)


class Channel(MultiEventModel):
    """Represents a channel in the channel rack."""

    def __repr__(self):
        if self.display_name is None:
            return f"Unnamed {type(self).__name__.lower()} #{self.iid}"
        return f"{type(self).__name__} {self.display_name!r} #{self.iid}"

    color = EventProp[colour.Color](PluginID.Color)
    controllers = KWProp[List[RemoteController]]()
    default_name = EventProp[str](PluginID.DefaultName)
    """Default name of the channel.

    The value of this depends on the type of `plugin`:

    * Native (stock) plugin: The factory name of the plugin.
    * VST instruments: "Fruity Wrapper".

    See `name` also.
    """

    enabled = EventProp[bool](ChannelID.IsEnabled)
    group = KWProp[DisplayGroup]()
    """Display group / filter under which this channel is grouped."""

    icon = EventProp[int](PluginID.Icon)
    iid = EventProp[int](ChannelID.New)
    keyboard = NestedProp(Keyboard, ChannelID.FineTune, ChannelID.RootNote)
    locked = EventProp[bool](ChannelID.IsLocked)
    name = EventProp[str](PluginID.Name)
    """The name associated with a channel.

    It's value depends on the type of plugin:

    * Native (stock): User-given name, None if not given one.
    * VST instrument: The name obtained from the VST or the user-given name.

    !!! tip "See also"
        `default_name` and `display_name`.
    """

    @property
    def pan(self) -> Optional[int]:
        """Min: 0, Max: 12800, Default: 6400."""
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
    def volume(self) -> Optional[int]:
        """Min: 0, Max: 12800, Default: 10000."""
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

    @property
    def zipped(self) -> bool:
        """Whether the channel is in zipped state.

        ???+ info "Internal representation"
            If the channel is not zipped, underlying event is not stored.
        """
        if ChannelID.Zipped in self._events:
            return self._events[ChannelID.Zipped][0].value
        return False

    @property
    def display_name(self) -> Optional[str]:
        """The name of the channel that will be displayed in FL Studio."""
        return self.name or self.default_name


class Automation(Channel):
    ...


class Layer(Channel):
    @property
    def children(self) -> Iterator[Channel]:
        if ChannelID.Children in self._events:
            for event in self._events[ChannelID.Children]:
                yield self._kw["channels"][event.value]

    # TODO Discover
    flags = EventProp[int](ChannelID.LayerFlags)


class _SamplerInstrument(Channel):
    arp = NestedProp(Arp, ChannelID.Parameters)
    delay = NestedProp(Delay, ChannelID.Delay)

    # TODO Discover
    flags = EventProp[int](ChannelID.SamplerFlags)
    insert = EventProp[int](ChannelID.RoutedTo)
    """The index of the `Insert` the channel is routed to. Min = -1."""

    level_adjusts = NestedProp(LevelAdjusts, ChannelID.LevelAdjusts)
    polyphony = NestedProp(Polyphony, ChannelID.Polyphony)
    stretching = NestedProp(TimeStretching, ChannelID.StretchTime)
    time = NestedProp(Time, ChannelID.Swing)
    tracking = IterProp(ChannelID.Tracking, Tracking)


class Instrument(_SamplerInstrument):
    plugin: Optional[IPlugin] = None
    """The plugin loaded into the channel.

    Valid only if channel is of instrument type.
    """


class Sampler(_SamplerInstrument):
    au_sample_rate = EventProp[int](ChannelID.AUSampleRate)
    """AU-format sample specific."""

    cut_group = EventProp[Tuple[int, int]](ChannelID.CutGroup)
    """Cut group in the form of (Cut self, cut by)."""

    envelopes = IterProp(ChannelID.EnvelopeLFO, Envelope)
    """Upto 5 elements for Volume, Panning, Mod X, Mod Y and Pitch envelopes.

    Note:
        FL's interface doesn't have an envelope for panning, but still stores
        the default values in the underlying event data.
    """

    fx = NestedProp[FX](
        FX,
        ChannelID.Cutoff,
        ChannelID.FadeIn,
        ChannelID.FadeOut,
        ChannelID.Preamp,
        ChannelID.Resonance,
        ChannelID.StereoDelay,
    )
    lfos = IterProp(ChannelID.EnvelopeLFO, LFO)
    """Upto 5 elements for Volume, Panning, Mod X, Mod Y and Pitch LFOs."""

    @property
    def pitch_shift(self) -> Optional[int]:
        """-4800 to +4800 cents max.

        Raises:
            PropertyCannotBeSet: When a ChannelID.Levels event is not found.
        """
        if ChannelID.Levels in self._events:
            return cast(LevelsEvent, self._events[ChannelID.Levels][0])["pitch_shift"]

    @pitch_shift.setter
    def pitch_shift(self, value: int):
        try:
            event = self._events[ChannelID.Levels][0]
        except KeyError:
            raise PropertyCannotBeSet(ChannelID.Levels)
        else:
            cast(LevelsEvent, event)["pitch_shift"] = value

    playback = NestedProp[Playback](Playback, ChannelID.UsesLoopPoints)
    sample_path = EventProp[str](ChannelID.SamplePath)
    """Absolute path of a sample file on the disk.

    Valid only if channel is a Sampler instance or an audio clip / track.
    Contains the string '%FLStudioFactoryData%' for stock samples.
    """


class Rack(MultiEventModel, Sized, Iterable[Channel]):
    def __repr__(self) -> str:
        return f"ChannelRack - {len(self)} channels"

    def __iter__(self):
        return self.channels

    def __len__(self):
        if ChannelID.New not in self._events:
            return NotImplemented
        return len(self._events[ChannelID.New])

    @property
    def automations(self) -> Iterator[Automation]:
        for channel in self.channels:
            if isinstance(channel, Automation):
                yield channel

    @property
    def channels(self) -> Iterator[Channel]:
        ch_dict: Dict[int, Channel] = {}
        events: DefaultDict[int, List[AnyEvent]] = collections.defaultdict(list)
        cur_ch_events = []
        for event in self._events_tuple:
            if event.id == ChannelID.New:
                cur_ch_events = events[event.value]

            if event.id not in RackID:
                cur_ch_events.append(event)

        for iid, ch_events in events.items():
            ct = None
            for event in ch_events:
                if event.id == ChannelID.Type:
                    if event.value == ChannelType.Automation:
                        ct = Automation
                    elif event.value == ChannelType.Instrument:
                        ct = Instrument
                    elif event.value == ChannelType.Layer:
                        ct = Layer
                    elif event.value == ChannelType.Sampler:
                        ct = Sampler
                    else:
                        ct = Channel

            if ct is not None:
                cur_ch = ch_dict[iid] = ct(*ch_events, channels=ch_dict)
                yield cur_ch

    fit_to_steps = EventProp[int](RackID._FitToSteps)

    @property
    def groups(self) -> Iterator[DisplayGroup]:
        if DisplayGroupID.Name in self._events:
            for event in self._events[DisplayGroupID.Name]:
                yield DisplayGroup(event)

    @property
    def instruments(self) -> Iterator[Instrument]:
        for channel in self.channels:
            if isinstance(channel, Instrument):
                yield channel

    @property
    def layers(self) -> Iterator[Layer]:
        for channel in self.channels:
            if isinstance(channel, Layer):
                yield channel

    @property
    def samplers(self) -> Iterator[Sampler]:
        for channel in self.channels:
            if isinstance(channel, Sampler):
                yield channel

    swing = EventProp[int](RackID.Swing)
    """Global channel swing mix. Min: 0, Max: 128, Default: 64."""
