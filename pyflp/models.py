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

"""Contains the event structures and dataclasses used by the FLP format."""

import pathlib
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum, IntFlag, auto
from platform import platform
from typing import ClassVar, Dict, Iterator, List, Optional, TypeVar

import colour

from .events import *
from .events import PluginEvent

__all__ = [
    "DELPHI_EPOCH",
    "ENVELOPE_NAMES",
    "TRACKING_TYPES",
    "Arrangement",
    "BooBass",
    "BooBassEvent",
    "Channel",
    "ChannelArp",
    "ChannelArpDirection",
    "ChannelDelay",
    "ChannelDelayEvent",
    "ChannelEnvelope",
    "ChannelEnvelopeFlags",
    "ChannelEnvelopeLFOEvent",
    "ChannelLevelAdjustsEvent",
    "ChannelLevelsEvent",
    "ChannelLFO",
    "ChannelLFOShape",
    "ChannelParametersEvent",
    "ChannelPolyphonyEvent",
    "ChannelPolyphonyFlags",
    "ChannelPlaylistItem",
    "ChannelReverbType",
    "ChannelTracking",
    "ChannelType",
    "DisplayGroup",
    "EventID",
    "FileFormat",
    "FLVersion",
    "FruityBalance",
    "FruityBalanceEvent",
    "FruityFastDist",
    "FruityFastDistEvent",
    "FruityNotebook2",
    "FruityNotebook2Event",
    "FruitySend",
    "FruitySendEvent",
    "FruitySoftClipper",
    "FruitySoftClipperEvent",
    "FruityStereoEnhancer",
    "FruityStereoEnhancerEvent",
    "Insert",
    "InsertDock",
    "InsertFlags",
    "InsertRoute",
    "InsParamsEventID",
    "InsertSlot",
    "PanLaw",
    "Pattern",
    "PatternController",
    "PatternNote",
    "PatternPlaylistItem",
    "PlaylistItemType",
    "Project",
    "RemoteController",
    "Soundgoodizer",
    "SoundgoodizerEvent",
    "TimeMarker",
    "TimeMarkerType",
    "TimeSignature",
    "Track",
    "VSTPlugin",
]

DELPHI_EPOCH = datetime(1899, 12, 30)
ENVELOPE_NAMES = ("Panning", "Volume", "Pitch", "Mod X", "Mod Y")
TRACKING_TYPES = ("Vol", "Key")


class ChannelDelayEvent(StructEventBase):
    SIZE = 20
    PROPS = dict.fromkeys(("feedback", "pan", "pitch_shift", "echoes", "time"), "I")


class ChannelEnvelopeLFOEvent(StructEventBase):
    SIZE = 68
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


class ChannelLevelAdjustsEvent(StructEventBase):
    SIZE = 20
    PROPS = {"pan": "I", "volume": "I", "_u4": 4, "mod_x": "I", "mod_y": "I"}


class ChannelLevelsEvent(StructEventBase):
    SIZE = 24
    PROPS = {"pan": "I", "volume": "I", "pitch_shift": "I", "_u12": 12}


class ChannelParametersEvent(StructEventBase):
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


class ChannelPolyphonyEvent(StructEventBase):
    SIZE = 9
    PROPS = {"max": "I", "slide": "I", "flags": "B"}


class ChannelTrackingEvent(StructEventBase):
    SIZE = 16
    PROPS = {"middle_value": "i", "pan": "i", "mod_x": "i", "mod_y": "i"}


class InsertFlagsEvent(StructEventBase):
    SIZE = 12
    PROPS = {"_u1": "I", "flags": "I", "_u2": "I"}


class InsertParametersEventItem:
    SIZE = 12
    PROPS = {
        "_u4": 4,  # 4
        "index": "b",  # 5
        "_u1": 1,  # 6
        "channel_data": "H",  # 8
        "msg": "i",  # 12
    }


class PlaylistEventItem:
    SIZE = 32
    PROPS = {
        "position": "I",  # 4
        "pattern_base": "H",  # 6
        "item_index": "H",  # 8
        "length": "I",  # 12
        "track_index": "i",  # 16
        "_u2": 2,  # 18
        "item_flags": "H",  # 20
        "_u4": 4,  # 24
        "start_offset": "i",  # 28
        "end_offset": "i",  # 32
    }


class PatternContollerEventItem:
    SIZE = 12
    PROPS = {
        "position": "I",  # 4
        "_u1": 1,  # 5
        "_u2": 1,  # 6
        "channel": "B",  # 7
        "_flags": "B",  # 8
        "value": "f",  # 12
    }


class PatternNotesEventItem:
    SIZE = 24
    PROPS = {
        "position": "I",  # 4
        "flags": "H",  # 6
        "rack_channel": "H",  # 8
        "duration": "I",  # 12
        "key": "I",  # 16
        "fine_pitch": "b",  # 17
        "_u1": 1,  # 18
        "release": "B",  # 19
        "midi_channel": "B",  # 20
        "pan": "b",  # 21
        "velocity": "B",  # 22
        "mod_x": "B",  # 23
        "mod_y": "B",  # 24
    }


class TimestampEvent(StructEventBase):
    SIZE = 16
    PROPS = dict.fromkeys(("created_on", "work_time"), "d")


class TrackEvent(StructEventBase):
    PROPS = {
        "index": "I",  # 4
        "color": "i",  # 8
        "icon": "i",  # 12
        "enabled": "bool",  # 13
        "height": "f",  # 17
        "locked_height": "f",  # 21
        "locked_to_content": "bool",  # 22
        "motion": "I",  # 26
        "press": "I",  # 30
        "trigger_sync": "I",  # 34
        "queued": "I",  # 38
        "tolerant": "I",  # 42
        "position_sync": "I",  # 46
        "grouped": "bool",  # 47
        "locked": "bool",  # 48
    }


class RemoteControllerEvent(StructEventBase):
    SIZE = 20
    PROPS = {
        "_u1": 2,  # 2
        "_u2": 1,  # 3
        "_u3": 1,  # 4
        "parameter_data": "H",  # 6
        "destination_data": "h",  # 8
        "_u4": 8,  # 16
        "_u5": 4,  # 20
    }


class EventID(IntEnum):
    def __new__(cls, id, type=None):
        obj = int.__new__(cls, id)
        obj._value_ = id
        obj.type = type
        return obj

    # def __hash__(cls, id) -> int:
    #     return hash(cls(id).value)

    ChIsEnabled = (0, BoolEvent)
    _ChVolByte = (2, U8Event)
    _ChPanByte = (3, U8Event)
    ProjLoopActive = (9, BoolEvent)
    ProjShowInfo = (10, BoolEvent)
    ProjSwing = (11, U8Event)
    _ProjVolume = (12, U8Event)
    _ProjFitToSteps = (13, U8Event)
    ChZipped = (15, BoolEvent)
    ProjTimeSigNum = (17, U8Event)
    ProjTimeSigBeat = (18, U8Event)
    ChUsesLoopPoints = (19, BoolEvent)
    ChType = (21, U8Event)
    ChRoutedTo = (22, I8Event)
    ProjPanLaw = (23, U8Event)
    # ChFXProperties = 27
    ProjRegistered = (28, BoolEvent)
    ProjPlayTruncatedNotes = (30, BoolEvent)
    ChIsLocked = (32, BoolEvent)  # FL12.3+
    TMNumerator = (33, U8Event)
    TMDenominator = (34, U8Event)

    ChNew = (WORD, U16Event)
    PatNew = (WORD + 1, U16Event)  # Marks the beginning of a new pattern, twice.
    # _Tempo = WORD + 2
    ProjCurPatIdx = (WORD + 3, U16Event)
    # Fx = WORD + 5
    # FadeStereo = WORD + 6
    ChCutoff = (WORD + 7, U16Event)
    _ChVolWord = (WORD + 8, U16Event)
    _ChPanWord = (WORD + 9, U16Event)
    ChPreamp = (WORD + 10, U16Event)
    ChFadeOut = (WORD + 11, U16Event)
    ChFadeIn = (WORD + 12, U16Event)
    # DotNote = WORD + 13
    # DotPitch = WORD + 14
    # DotMix = WORD + 15
    ProjPitch = (WORD + 16, I16Event)
    ChResonance = (WORD + 19, U16Event)
    # _LoopBar = WORD + 20
    ChStereoDelay = (WORD + 21, U16Event)
    # Fx3 = WORD + 22
    # DotReso = WORD + 23
    # DotCutOff = WORD + 24
    # ShiftDelay = WORD + 25
    # _LoopEndBar = WORD + 26
    # Dot = WORD + 27
    # _TempoFine = WORD + 29
    # DotRel = WORD + 32
    # DotShift = WORD + 28
    ChChildren = (WORD + 30, U16Event)
    InsIcon = (WORD + 31, I16Event)
    ChSwing = (WORD + 33, U16Event)
    SlotIndex = (WORD + 34, U16Event)
    ArrNew = (WORD + 35, U16Event)

    ChColor = SlotColor = (DWORD, ColorEvent)
    # _PlaylistItem = DWORD + 1
    # Echo = DWORD + 2
    # FxSine = DWORD + 3
    ChCutGroup = (DWORD + 4, U16TupleEvent)
    ChRootNote = (DWORD + 7, U32Event)
    # _MainResoCutOff = DWORD + 9
    # DelayModXY = DWORD + 10
    ChReverb = (DWORD + 11, U32Event)
    ChStretchTime = (DWORD + 12, F32Event)
    ChFineTune = (DWORD + 14, I32Event)
    ChSamplerFlags = (DWORD + 15, U32Event)
    ChLayerFlags = (DWORD + 16, U32Event)
    ChGroupNum = (DWORD + 17, I32Event)
    ProjCurGroupId = (DWORD + 18, I32Event)
    InsOutput = (DWORD + 19, I32Event)
    TMPosition = (DWORD + 20, U32Event)
    InsColor = (DWORD + 21, ColorEvent)
    PatColor = (DWORD + 22, ColorEvent)
    ProjLoopPos = (DWORD + 24, U32Event)
    ChAUSampleRate = (DWORD + 25, U32Event)
    InsInput = (DWORD + 26, I32Event)
    ChIcon = SlotIcon = (DWORD + 27, U32Event)
    ProjTempo = (DWORD + 28, U32Event)
    # _157 = DWORD + 29   # FL 12.5+
    # _158 = DWORD + 30   # default: -1
    ProjVerBuild = (DWORD + 31, U32Event)
    # _164 = DWORD + 36   # default: 0

    PatName = TEXT + 1
    ProjTitle = TEXT + 2
    ProjComments = TEXT + 3
    ChSamplePath = TEXT + 4
    ProjUrl = TEXT + 5
    _ProjRTFComments = TEXT + 6
    ProjFLVersion = (TEXT + 7, AsciiEvent)
    ProjRegisteredTo = TEXT + 8
    ChDefaultName = SlotDefaultName = TEXT + 9
    ProjDataPath = TEXT + 10
    ChName = SlotName = TEXT + 11
    InsName = TEXT + 12
    TMName = TEXT + 13
    ProjGenre = TEXT + 14
    ProjArtists = TEXT + 15
    GroupName = TEXT + 39
    TrackName = TEXT + 47
    ArrName = TEXT + 49

    ChDelay = (DATA + 1, ChannelDelayEvent)
    # Plugin wrapper data, windows pos of plugin etc, currently
    # selected plugin wrapper page; minimized, closed or not
    ChPlugWrapper = SlotPlugWrapper = (DATA + 4, UnknownDataEvent)  # TODO
    ChPlugin = SlotPlugin = (DATA + 5, PluginEvent)
    ChParameters = (DATA + 7, ChannelParametersEvent)
    ChEnvelopeLFO = (DATA + 10, ChannelEnvelopeLFOEvent)
    ChLevels = (DATA + 11, ChannelLevelsEvent)
    # _ChFilter = DATA + 12
    ChPolyphony = (DATA + 13, ChannelPolyphonyEvent)
    PatControllers = (DATA + 15, DataArrayEvent)
    PatNotes = (DATA + 16, DataArrayEvent)
    InsParameters = (DATA + 17, DataArrayEvent)
    RemoteController = (DATA + 19, RemoteControllerEvent)
    ChTracking = (DATA + 20, ChannelTrackingEvent)
    ChLevelAdjusts = (DATA + 21, ChannelLevelAdjustsEvent)
    PlaylistData = (DATA + 25, DataArrayEvent)
    InsRouting = (DATA + 27, DataArrayEvent)
    InsFlags = (DATA + 28, InsertFlagsEvent)
    ProjTimestamp = (DATA + 29, TimestampEvent)
    TrackData = (DATA + 30, TrackEvent)


@dataclass
class DisplayGroup:
    name: Optional[str] = None


@dataclass
class RemoteController:
    parameter: Optional[int] = None
    """The ID of the plugin parameter to which controller is linked to."""

    is_vst_param: Optional[bool] = None
    """Whether `parameter` is linked to a VST plugin.

    None when linked to a plugin parameter on an insert slot.
    """


@dataclass
class ChannelDelay:
    echoes: Optional[int] = None
    """Number of echoes generated for each note."""

    feedback: Optional[int] = None
    """Factor with which the volume of every next echo is multiplied."""

    # is_fat_mode: Optional[bool] = None
    # is_ping_pong: Optional[bool] = None
    # mod_x: Optional[int] = None
    # mod_y: Optional[int] = None
    pan: Optional[int] = None
    pitch_shift: Optional[int] = None
    time: Optional[int] = None


class ChannelArpDirection(IntEnum):
    Off = 0
    Up = 1
    Down = 2
    UpDownBounce = 3
    UpDownSticky = 4
    Random = 5


@dataclass
class ChannelArp:
    direction: Optional[ChannelArpDirection] = None
    range: Optional[int] = None
    """Range (in octaves)."""

    chord: Optional[int] = None
    """Index of the selected arpeggio chord."""

    repeat: Optional[int] = None
    """Number of times a note is repeated."""

    time: Optional[float] = None
    """Delay between two successive notes played."""

    gate: Optional[float] = None
    """Higher values result in a more staccato sound."""

    slide: Optional[bool] = None
    """Whether arpeggio will slide between notes."""


@dataclass
class ChannelLevelAdjusts:
    pan: Optional[int] = None
    volume: Optional[int] = None
    # unknown int 1
    mod_x: Optional[int] = None
    mod_y: Optional[int] = None


class ChannelType(IntEnum):
    Sampler = 0
    Native = 2  # Used by audio clips and other native FL Studio synths
    Layer = 3
    Instrument = 4
    Automation = 5


class ChannelLFOShape(IntEnum):
    Sine = 0
    Triangle = 1
    Pulse = 2


class ChannelEnvelopeFlags(IntFlag):
    LFOTempoSync = 1 << 1
    Unknown = 1 << 2  # Occurs for volume envlope only.
    LFORetrig = 1 << 5


class ChannelReverbType(IntEnum):
    A = 0
    B = 65536


@dataclass
class ChannelTime:
    swing: Optional[int] = None
    # gate: int
    # shift: int
    # is_full_porta: bool


@dataclass
class ChannelReverb:
    kind: Optional[ChannelReverbType] = None
    mix: Optional[int] = 0
    """Reverb mix (dry/wet). Min: 0, Max: 256, Default: 0."""


@dataclass
class ChannelFX:
    boost: Optional[int] = None
    """Pre-amp. Min: 0, Max: 256, Default: 0."""

    cutoff: Optional[int] = None
    """Filter Mod X. Min = 0, Max = 1024, Default = 1024."""

    fade_in: Optional[int] = None
    """Quick fade-in. Min = 0, Max = 1024, Default = 0."""

    fade_out: Optional[int] = None
    """Quick fade-out. Min = 0, Max = 1024, Default = 0."""

    resonance: Optional[int] = None
    """Filter Mod Y. Min = 0, Max = 1024, Default = 0."""

    reverb: ChannelReverb = field(default_factory=ChannelReverb)
    stereo_delay: Optional[int] = None


@dataclass
class ChannelEnvelope:
    enabled: Optional[bool] = None
    """Whether envelope section is enabled."""

    predelay: Optional[int] = None
    """Min: 100 (0%), Max: 65536 (100%), Default: 100 (0%)."""

    attack: Optional[int] = None
    """Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    hold: Optional[int] = None
    """Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    decay: Optional[int] = None
    """Min: 100 (0%), Max: 65536 (100%), Default: 30000 (46%)."""

    sustain: Optional[int] = None
    """Min: 0 (0%), Max: 128 (100%), Default: 50 (39%)."""

    release: Optional[int] = None
    """Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    attack_tension: Optional[int] = None
    """Min: -128 (-100%), Max: 128 (100%), Default: 0 (0%)."""

    sustain_tension: Optional[int] = None
    """Min: -128 (-100%), Max: 128 (100%), Default: 0 (0%)."""

    release_tension: Optional[int] = None
    """Min: -128 (-100%), Max: 128 (100%), Default: -101 / 0 (-79% / 0%)."""


@dataclass
class ChannelLFO:
    # amount: Optional[int] = None
    # attack: Optional[int] = None
    is_synced: Optional[bool] = None
    """Whether LFO is synced with tempo."""

    is_retrig: Optional[bool] = None
    """Whether LFO phase is in global / retriggered mode."""

    # predelay: Optional[int] = None
    shape: Optional[ChannelLFOShape] = None
    """Sine, triangle or pulse. Default: Sine."""

    # speed: Optional[int] = None


@dataclass
class ChannelPolyphony:
    max: Optional[int] = None
    slide: Optional[int] = None
    is_porta: Optional[bool] = None
    is_mono: Optional[bool] = None


class ChannelPolyphonyFlags(IntFlag):
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


@dataclass
class ChannelTracking:
    middle_value: Optional[int] = None
    mod_x: Optional[int] = None
    mod_y: Optional[int] = None
    pan: Optional[int] = None


@dataclass
class ChannelKeyboard:
    fine_tune: Optional[int] = None
    """-100 to +100 cents."""

    root_note: Optional[int] = None
    """Min: 0 (C0), Max: 131 (B10)."""

    # is_main_pitch_enabled: Optional[bool] = None
    # """Whether triggered note is affected by changes to `project.main_pitch`."""

    # is_added_to_key: Optional[bool] = None
    # """Whether root note should be added to triggered note instead of pitch."""

    # note_range: tuple[int] - Should be a 2-short or 2-byte tuple


@dataclass
class ChannelPlayback:
    # start_offset: int
    use_loop_points: bool = False
    # ping_pong_loop: bool


@dataclass
class ChannelTimeStretching:
    # mode: enum
    # multiplier: Optional[int] = None
    # pitch: Optional[int] = None
    time: Optional[float] = None


@dataclass
class Channel:
    """Represents a channel in the channel rack."""

    arp: ChannelArp = field(default_factory=ChannelArp)
    au_sample_rate: Optional[int] = None
    """AU-format sample specific."""

    children: List["Channel"] = field(default_factory=list)
    """List of children `index`es of a Layer.

    Valid only if for layer channels (i.e. `ChannelType.Layer`).
    """

    color: colour.Color = field(default_factory=colour.Color)
    controllers: List[RemoteController] = field(default_factory=list)
    cut_group: List[int] = field(default_factory=list)
    """Cut group in the form of (Cut self, cut by)."""

    delay: ChannelDelay = field(default_factory=ChannelDelay)
    default_name: Optional[str] = None
    """Default name of the channel.
    The value of this depends on the type of `plugin`:

    * Native (stock) plugin: The factory name of the plugin.
    * VST instruments: "Fruity Wrapper".

    See `name` also.
    """

    enabled: Optional[bool] = None
    envelopes: Dict[str, ChannelEnvelope] = field(default_factory=dict)
    fx: ChannelFX = field(default_factory=ChannelFX)
    group: DisplayGroup = field(default_factory=DisplayGroup)
    """Index of the filter group under which this channel is grouped."""

    icon: Optional[int] = None
    keyboard: ChannelKeyboard = field(default_factory=ChannelKeyboard)
    layer_flags: Optional[int] = None  # TODO Discover
    level_adjusts: ChannelLevelAdjusts = field(default_factory=ChannelLevelAdjusts)
    lfos: Dict[str, ChannelLFO] = field(default_factory=dict)
    locked: Optional[bool] = None
    name: Optional[str] = None
    """The value of this depends on the type of instrument plugin.

    If it is,
    - Native (stock) plugin: User-given name.
    - VST plugin (VSTi): The name obtained from the VST, or the user-given name.

    See `default_name` also.
    """

    pan: Optional[int] = None
    """Min: 0, Max: 12800, Default: 6400."""

    pitch_shift: Optional[int] = None
    """-4800 to +4800 cents max."""

    playback: ChannelPlayback = field(default_factory=ChannelPlayback)
    plugin: Optional[object] = None
    """The plugin loaded into the channel.

    Valid only if channel is of instrument type.
    """

    polyphony: ChannelPolyphony = field(default_factory=ChannelPolyphony)
    sample_path: Optional[str] = None
    """Absolute path of a sample file on the disk.

    Valid only if channel is a Sampler instance or an audio clip / track.
    Contains the string '%FLStudioFactoryData%' for stock samples.
    """

    target_insert: Optional[int] = None
    """The index of the `Insert` the channel is routed to. Min = -1."""

    time: ChannelTime = field(default_factory=ChannelTime)
    sampler_flags: Optional[int] = None  # TODO Discover
    stretching: ChannelTimeStretching = field(default_factory=ChannelTimeStretching)
    tracking: Dict[str, ChannelTracking] = field(default_factory=dict)
    type: Optional[ChannelType] = None
    volume: Optional[int] = None
    """Min: 0, Max: 12800, Default: 10000."""

    zipped: bool = False
    """Whether the channel is in zipped state."""

    def __post_init__(self) -> None:
        for key in ENVELOPE_NAMES:
            self.envelopes[key] = ChannelEnvelope()
            self.lfos[key] = ChannelLFO()

        for key in TRACKING_TYPES:
            self.tracking[key] = ChannelTracking()

    @property
    def display_name(self) -> Optional[str]:
        if self.name:
            return self.name
        return self.default_name


@dataclass
class PatternNote:
    fine_pitch: Optional[int] = None
    """Min: -128 (-100 cents), Max: 127 (+100 cents)."""

    flags: Optional[int] = None  # TODO Seems like, but NOT porta, slide etc.
    key: Optional[int] = None
    """0-131 for C0-B10. Can hold stamped chords and scales also."""

    length: Optional[int] = None
    midi_channel: Optional[int] = None
    """For note colors, min: 0, max: 15.

    128 for MIDI dragged into the piano roll.
    """

    mod_x: Optional[int] = None
    mod_y: Optional[int] = None
    pan: Optional[int] = None
    """Min: -128, Max: 127."""

    position: Optional[int] = None
    rack_channel: Optional[int] = None
    """Index of the channel this note is on."""

    release: Optional[int] = None
    """Min: 0, Max: 128."""

    velocity: Optional[int] = None
    """Min: 0, Max: 128."""


@dataclass
class PatternController:
    position: Optional[int] = None
    channel: Optional[int] = None
    value: Optional[int] = None


@dataclass
class Pattern:
    color: colour.Color = field(default_factory=colour.Color)
    controllers: List[PatternController] = field(default_factory=list)
    name: Optional[str] = None
    notes: List[PatternNote] = field(default_factory=list)


@dataclass
class _PlaylistItem(ABC):
    position: Optional[int] = None
    length: Optional[int] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    muted: Optional[bool] = None


PlaylistItemType = TypeVar("PlaylistItemType", bound=_PlaylistItem)


@dataclass
class ChannelPlaylistItem(_PlaylistItem):
    channel: Optional[Channel] = None


@dataclass
class PatternPlaylistItem(_PlaylistItem):
    pattern: Optional[Pattern] = None


class TrackMotion(IntEnum):
    Stay = 0
    OneShot = 1
    MarchWrap = 2
    MarchStay = 3
    MarchStop = 4
    Random = 5
    ExclusiveRandom = 6


class TrackPress(IntEnum):
    Retrigger = 0
    HoldStop = 1
    HoldMotion = 2
    Latch = 3


class TrackSync(IntEnum):
    Off = 0
    QuarterBeat = 1
    HalfBeat = 2
    Beat = 3
    TwoBeats = 4
    FourBeats = 5
    Auto = 6


class TimeMarkerType(IntEnum):
    Marker = 0
    """Normal text marker."""

    Signature = 134217728
    """Used for time signature markers."""


@dataclass
class TimeMarker:
    denominator: Optional[int] = None  # 2, 4, 8 or 16
    name: Optional[str] = None
    numerator: Optional[int] = None  # 1-16
    position: Optional[int] = None
    type: Optional[TimeMarkerType] = None


@dataclass
class Track:
    color: colour.Color = field(default_factory=colour.Color)
    enabled: Optional[bool] = None
    grouped: Optional[bool] = None
    """Whether grouped with the track above (index - 1) or not."""

    height: Optional[float] = None
    """Min: 0.0 (0%), Max: 18.4 (1840%), Default: 1.0 (100%)."""

    icon: Optional[int] = None
    index: Optional[int] = None
    items: List[PlaylistItemType] = field(default_factory=list)
    """Playlist items present on the track."""

    locked: Optional[bool] = None
    locked_height: Optional[float] = None
    locked_to_content: Optional[bool] = None
    motion: Optional[TrackMotion] = None
    name: Optional[str] = None
    position_sync: Optional[TrackSync] = None
    press: Optional[TrackPress] = None
    tolerant: Optional[bool] = None
    trigger_sync: Optional[TrackSync] = None
    queued: Optional[bool] = None


@dataclass
class Arrangement:
    name: Optional[str] = None
    timemarkers: List[TimeMarker] = field(default_factory=list)
    tracks: List[Track] = field(default_factory=list)


class InsParamsEventID(IntEnum):
    SlotEnabled = 0
    # SlotVolume = 1
    SlotMix = 1
    RouteVolStart = 64  # 64 - 191 are send level events
    Volume = 192
    Pan = 193
    StereoSeparation = 194
    LowGain = 208
    BandGain = 209
    HighGain = 210
    LowFreq = 216
    BandFreq = 217
    HighFreq = 218
    LowQ = 224
    BandQ = 225
    HighQ = 226


class InsertDock(Enum):
    Left = auto()
    Middle = auto()
    Right = auto()


class InsertFlags(IntFlag):
    None_ = 0
    PolarityReversed = 1 << 0
    SwapLeftRight = 1 << 1
    """Left and right channels are swapped."""

    EnableEffects = 1 << 2
    """All slots are enabled. If this flag is absent, slots are bypassed."""

    Enabled = 1 << 3
    DisableThreadedProcessing = 1 << 4
    U5 = 1 << 5
    DockMiddle = 1 << 6
    DockRight = 1 << 7
    U8 = 1 << 8
    U9 = 1 << 9
    SeparatorShown = 1 << 10
    Locked = 1 << 11
    Solo = 1 << 12
    U13 = 1 << 13
    U14 = 1 << 14
    AudioTrack = 1 << 15
    """Whether insert is linked to an audio track."""


@dataclass
class InsertEQBand:
    gain: Optional[int] = None
    """Min: -1800, Max: 1800, Default: 0."""

    frequency: Optional[int] = None
    """Min: 0, Max: 65536, default depends on band."""

    resonance: Optional[int] = None
    """Min: 0, Max: 65536, Default: 17500."""


@dataclass
class InsertEQ:
    low: InsertEQBand = field(default_factory=InsertEQBand)
    """Low shelf band. Default frequency: 5777 (90 Hz)."""

    band: InsertEQBand = field(default_factory=InsertEQBand)
    """Middle band. Default frequency: 33145 (1500 Hz)."""

    high: InsertEQBand = field(default_factory=InsertEQBand)
    """High shelf band. Default frequency: 55825 (8000 Hz)."""


@dataclass
class InsertRoute:
    is_routed: bool = False
    volume: Optional[int] = None


@dataclass
class InsertSlot:
    """Represents an effect slot in an `Insert` / mixer channel."""

    color: colour.Color = field(default_factory=colour.Color)
    controllers: List[RemoteController] = field(default_factory=list)
    default_name: Optional[str] = None
    """'Fruity Wrapper' for VST/AU plugins or factory name for native plugins."""

    enabled: Optional[bool] = None
    icon: Optional[int] = None
    index: Optional[int] = None
    mix: Optional[int] = None
    """Dry/Wet mix. Min: 0 (0%), Max: 12800 (100%), Default: 12800 (100%)."""

    name: Optional[str] = None
    plugin: Optional[object] = None
    """The effect loaded into the slot."""


@dataclass
class Insert:
    """Represents a channel in the mixer."""

    bypassed: Optional[bool] = None
    """All slots are bypassed."""

    channels_swapped: Optional[bool] = None
    color: colour.Color = field(default_factory=colour.Color)
    docked_to: Optional[InsertDock] = None
    enabled: Optional[bool] = None
    """Whether an insert in the mixer is enabled or disabled."""

    eq: InsertEQ = field(default_factory=InsertEQ)
    """3-band post EQ."""

    icon: Optional[int] = None
    input: Optional[int] = None
    is_solo: Optional[bool] = None
    """Whether the insert is solo'd."""

    locked: Optional[bool] = None
    """Whether an insert in the mixer is in locked state."""

    name: Optional[str] = None
    output: Optional[int] = None
    pan: Optional[int] = None
    """Min: -6400 (100% left), Max: 6400 (100% right), Default: 0."""

    polarity_reversed: Optional[bool] = None
    routes: List[InsertRoute] = field(default_factory=list)
    separator_shown: Optional[bool] = None
    slots: List[InsertSlot] = field(default_factory=list)
    stereo_separation: Optional[int] = None
    """Min: -64 (100% merged), Max: 64 (100% separated), Default: 0."""

    volume: Optional[int] = None
    """Post volume fader.

    Min: 0 (0% / -INFdB / 0.00).
    Max: 16000 (125% / 5.6dB / 1.90).
    Default: 12800 (100% / 0.0dB / 1.00).
    """

    def __iter__(self) -> Iterator[InsertSlot]:
        return iter(self.slots)


class PanLaw(IntEnum):
    Circular = 0
    Triangular = 2


class FileFormat(IntEnum):
    """File formats used by FL Studio."""

    None_ = -1
    """Temporary"""

    Song = 0
    """FL Studio project (*.flp)."""

    Score = 0x10
    """FL Studio score (*.fsc). Stores pattern notes and controller events."""

    Automation = 24
    """FL Studio state (*.fst). Stores controller events and automation channels."""

    ChannelState = 0x20
    """Entire channel (including plugin events). Stores as FST."""

    PluginState = 0x30
    """Events of a native plugin on a channel or insert slot. Stored as FST."""

    GeneratorState = 0x31
    """Plugins events of a VST instrument. Stored as FST."""

    FXState = 0x32
    """Plugin events of a VST effect. Stored as FST."""

    InsertState = 0x40
    """Insert and all its slots. Stored as FST."""

    _ProbablyPatcher = 0x50  # TODO Patcher presets are stored as `PluginState`.


@dataclass
class TimeSignature:
    num: Optional[int] = None
    beat: Optional[int] = None


@dataclass
class Selection:
    pattern: Optional[Pattern] = None
    """Currently selected pattern index."""

    group: Optional[DisplayGroup] = None
    """Currently selected filter channel index."""

    song_loop: Optional[int] = None
    """Duration of the song selected as a loop."""


class VSTPluginEventID(IntEnum):
    MIDI = 1
    Flags = 2
    IO = 30
    Inputs = 31
    Outputs = 32
    PluginInfo = 50
    FourCC = 51  # Not present for Waveshells
    GUID = 52
    State = 53
    Name = 54
    PluginPath = 55
    Vendor = 56
    _57 = 57  # TODO, not present for Waveshells


@dataclass
class PluginIOInfo:
    mixer_offset: Optional[int] = None
    flags: Optional[int] = None


@dataclass
class VSTPlugin:
    DEFAULT_NAME: ClassVar[str] = "Fruity Wrapper"
    fourcc: Optional[str] = None
    """A unique four character code identifying the plugin.

    A database can be found on Steinberg's developer portal.
    """

    guid: Optional[bytes] = None  # See issue #8
    midi_in: Optional[int] = None
    """MIDI Input Port. Min: 0, Max: 255."""

    midi_out: Optional[int] = None
    """MIDI Output Port. Min: 0, Max: 255."""

    name: Optional[str] = None
    """Name of the plugin."""

    num_inputs: Optional[int] = None
    """Number of inputs the plugin supports."""

    num_outputs: Optional[int] = None
    """Number of outputs the plugin supports."""

    pitch_bend: Optional[int] = None
    """Pitch bend range (in semitones)."""

    state: Optional[bytes] = None
    """Plugin specific preset data blob."""

    vendor: Optional[str] = None
    """Plugin developer (vendor) name."""

    vst_number: Optional[int] = None  # TODO


class BooBassEvent(PluginEvent):
    SIZE = 16
    PROPS = dict.fromkeys(("_u1", "bass", "mid", "high"), "I")  # _u1 = [1, 0, 0, 0]


@dataclass
class BooBass:
    DEFAULT_NAME: ClassVar[str] = "BooBass"
    bass: Optional[int] = None
    """Min: 0, Max: 65535, Default: 32767."""

    high: Optional[int] = None
    """Min: 0, Max: 65535, Default: 32767."""

    mid: Optional[int] = None
    """Min: 0, Max: 65535, Default: 32767."""


class FruityBalanceEvent(PluginEvent):
    SIZE = 8
    PROPS = {"pan": "I", "volume": "I"}


@dataclass
class FruityBalance:
    DEFAULT_NAME: ClassVar[str] = "Fruity Balance"
    pan: Optional[int] = None
    """Min: -128, Max: 127, Default: 0 (0.50, Centred). Linear."""

    volume: Optional[int] = None
    """Min: 0, Max: 320, Default: 256 (0.80, 0dB). Logarithmic."""


class FruityFastDistEvent(PluginEvent):
    SIZE = 20
    PROPS = dict.fromkeys(("pre", "threshold", "kind", "mix", "post"), "I")


class FruityFastDistKind(IntEnum):
    A = 0
    B = 1


@dataclass
class FruityFastDist:
    DEFAULT_NAME: ClassVar[str] = "Fruity Fast Dist"
    kind: Optional[FruityFastDistKind] = None
    mix: Optional[int] = None
    """Min: 0 (0%), Max: 128 (100%), Default: 128 (100%). Linear."""

    post: Optional[int] = None
    """Min: 0 (0%), Max: 128 (100%), Default: 128 (100%). Linear."""

    pre: Optional[int] = None
    """Min: 64 (33%), Max: 192 (100%), Default: 128 (67%). Linear."""

    threshold: Optional[int] = None
    """Threshold. Min: 1 (10%), Max: 10 (100%), Default: 10 (100%). Linear. Stepped."""


@dataclass
class FruityNotebook2:
    CODEC: ClassVar[str] = "utf-16-le" if platform() == "Windows" else "utf-8"
    DEFAULT_NAME: ClassVar[str] = "Fruity Notebook 2"
    active_page: Optional[int] = None
    editable: Optional[bool] = None
    pages: List[str] = field(default_factory=list)


class FruityNotebook2Event(PluginEvent):
    def __init__(self, data: bytes) -> None:
        super().__init__(data, False)
        self.props = {"pages": []}

        self.stream.seek(4)
        self.props["active_page"] = self.stream.read_I()
        while True:
            page_num = self.stream.read_i()
            if page_num == -1:
                break

            size = self.stream.read_v()
            raw = self.stream.read(size)
            page = raw.decode(FruityNotebook2.CODEC)
            self.props["pages"].append(page)
        self.props["editable"] = self.stream.read_bool()


class FruitySendEvent(PluginEvent):
    SIZE = 16
    PROPS = dict.fromkeys(("pan", "dry", "volume", "send_to"), "I")


@dataclass
class FruitySend:
    DEFAULT_NAME: ClassVar[str] = "Fruity Send"
    dry: Optional[int] = None
    """Min: 0 (0%), Max: 256 (100%), Default: 256 (100%). Linear."""

    pan: Optional[int] = None
    """Min: -128 (100% left), Max: 127 (100% right), Default: 0 (Centred). Linear."""

    send_to: Optional[int] = None
    """Target insert index; depends on insert routing. Default: -1 (Master)."""

    volume: Optional[int] = None
    """Min: 0 (-INF db, 0.00), Max: 320 (5.6 dB, 1.90), Default: 256 (0.0 dB, 1.00). Logarithmic."""  # noqa


class FruitySoftClipperEvent(PluginEvent):
    SIZE = 8
    PROPS = {"threshold": "I", "post": "I"}


@dataclass
class FruitySoftClipper:
    DEFAULT_NAME: ClassVar[str] = "Fruity Soft Clipper"
    post: Optional[int] = None
    """Min: 0, Max: 160, Default: 128 (80%). Linear."""

    threshold: Optional[int] = None
    """Min: 1, Max: 127, Default: 100 (0.60, -4.4dB). Logarithmic."""


class SoundgoodizerEvent(PluginEvent):
    SIZE = 12
    PROPS = dict.fromkeys(("_u1", "mode", "amount"), "I")


class SoundgoodizerMode(IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3


@dataclass
class Soundgoodizer:
    DEFAULT_NAME: ClassVar[str] = "Soundgoodizer"
    mode: Optional[SoundgoodizerMode] = None
    amount: Optional[int] = None
    """Min: 0, Max: 1000, Default: 600. Logarithmic."""


class FruityStereoEnhancerEvent(PluginEvent):
    SIZE = 24
    PROPS = dict.fromkeys(
        (
            "pan",
            "volume",
            "stereo_separation",
            "phase_offset",
            "effect_position",
            "phase_inversion",
        ),
        "I",
    )


class StereoEnhancerEffectPosition(IntEnum):
    Pre = 0
    Post = 1


class StereoEnhancerPhaseInversion(IntEnum):
    None_ = 0
    Left = 1
    Right = 2


@dataclass
class FruityStereoEnhancer:
    DEFAULT_NAME: ClassVar[str] = "Fruity Stereo Enhancer"
    effect_position: Optional[StereoEnhancerEffectPosition] = None
    """Default: StereoEnhancerEffectPosition.Post."""

    pan: Optional[int] = None
    """Min: -128, Max: 127, Default: 0 (0.50, Centred). Linear."""

    phase_inversion: Optional[StereoEnhancerPhaseInversion] = None
    """Default: StereoEnhancerPhaseInversion.None_."""

    phase_offset: Optional[int] = None
    """Min: -512 (500ms L), Max: 512 (500ms R), Default: 0 (no offset). Linear."""

    stereo_separation: Optional[int] = None
    """Min: -96 (100% separation), Max: 96 (100% merged), Default: 0. Linear."""

    volume: Optional[int] = None
    """Min: 0, Max: 320, Default: 256 (0.80, 0dB). Logarithmic."""


@dataclass
class FLVersion:
    major: int
    minor: int
    build: int
    patch: Optional[int] = None


@dataclass
class Project:
    format: Optional[FileFormat] = None
    channel_count: Optional[int] = None
    """Number of channels in the rack.

    For Patcher presets, the total number of plugins used inside it.
    """

    ppq: Optional[int] = None
    """Pulses per quarter."""

    show_info: bool = False
    """Whether to show a banner while project on opening."""

    title: Optional[str] = None
    comments: Optional[str] = None
    url: Optional[str] = None
    genre: Optional[str] = None
    artists: Optional[str] = None
    created_on: Optional[datetime] = None
    """The date and time at which the project was created."""

    work_time: Optional[timedelta] = None
    """The amount of time spent working on the project."""

    data_path: Optional[pathlib.Path] = None
    play_truncated_notes: Optional[bool] = None
    """Whether to play truncated notes in pattern clips."""

    loop_active: Optional[bool] = None
    """Whether a portion of the song was selected while saving."""

    version: Optional[FLVersion] = None
    """FL Studio version which was used to save the FLP.

    Changing this to a lower version will not make an FLP load magically
    inside FL Studio, as newer events and/or plugins might have been used.
    """

    registered_to: Optional[str] = None
    """Jumbled up name of the artist's FL Studio username.

    Can be found out decoded in Debug log section of FL.
    *Most pirated versions of FL cause this to be stored empty.*
    *IL can then detect projects made from cracked FL easily.*
    """

    tempo: Optional[float] = None
    """Initial tempo stored in BPM (beats per minute)."""

    version_build: Optional[int] = None
    """FL Studio version build number; same as `FLVersion.build`."""

    main_pitch: Optional[int] = None
    main_volume: Optional[int] = None
    registered: Optional[bool] = None
    """Whether project was saved in a purchased copy of FL or in trial mode."""

    time_signature: TimeSignature = field(default_factory=TimeSignature)
    swing: Optional[int] = None
    """Global channel swing mix. Min: 0, Max: 128, Default: 64."""

    selection: Selection = field(default_factory=Selection)
    pan_law: Optional[PanLaw] = None
    fit_to_steps: Optional[int] = None
    arrangements: Dict[int, Arrangement] = field(default_factory=dict)
    channels: Dict[int, Channel] = field(default_factory=dict)
    groups: List[DisplayGroup] = field(default_factory=list)
    inserts: List[Insert] = field(default_factory=list)
    patterns: Dict[int, Pattern] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._events: List[EventType] = []
        self._is_dirty = False

    @staticmethod
    def with_events(events: List[EventType]):
        project = Project()
        project._events = events
        return project
