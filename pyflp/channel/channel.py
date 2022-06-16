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

import enum
import struct
from typing import Any, Dict, List, Optional, Tuple

import colour

from pyflp._event import (
    ByteEventType,
    DataEventType,
    DWordEventType,
    EventType,
    TextEventType,
    WordEventType,
)
from pyflp._flobject import _FLObject
from pyflp._properties import (
    _BoolProperty,
    _ColorProperty,
    _EnumProperty,
    _IntProperty,
    _StrProperty,
    _UIntProperty,
)
from pyflp.channel.arp import ChannelArp
from pyflp.channel.delay import ChannelDelay
from pyflp.channel.envlfo import (
    ChannelEnvelopeLFO,
    ChannelEnvelopeLFOEvent,
    EnvelopeLFONames,
)
from pyflp.channel.fx import ChannelFX
from pyflp.channel.level_offsets import ChannelLevelOffsets
from pyflp.channel.levels import ChannelLevels
from pyflp.channel.polyphony import ChannelPolyphony
from pyflp.channel.tracking import ChannelTracking, ChannelTrackingEvent
from pyflp.constants import DATA, DWORD, TEXT, WORD
from pyflp.plugin._plugin import _Plugin
from pyflp.plugin.synths.boobass import BooBass
from pyflp.plugin.vst import VSTPlugin


class Channel(_FLObject):
    """Represents a channel of one of the kinds in `Kind` in the channel rack."""

    def __init__(self):
        super().__init__()
        self._layer_children: List[int] = []

        # Since default event isn't stored and having this event means it is zipped.
        self._zipped = False

        # 1 for vol tracking, 1 for key tracking.
        self.__tracking_events: List[ChannelTrackingEvent] = []

        # 1 each for panning, volume, pitch, mod x and mod y
        self._env_lfos: Dict[str, ChannelEnvelopeLFO] = {}
        self.__envlfo_events: List[ChannelEnvelopeLFOEvent] = []

    def _setprop(self, n: str, v: Any) -> None:
        if n == "volume":
            self.levels.volume = v
        elif n == "pan":
            self.levels.pan = v
        else:
            super()._setprop(n, v)

    @enum.unique
    class Kind(enum.IntEnum):
        """Used by `Channel.kind` for event `Channel.EventID.Kind`."""

        Sampler = 0
        Native = 2  # Used by audio clips and other native FL Studio synths
        Layer = 3
        Instrument = 4
        Automation = 5

    @enum.unique
    class EventID(enum.IntEnum):
        """Event IDs used by `Channel`."""

        Enabled = 0
        """See `Channel.enabled`."""

        _Vol = 2
        """See `Channel.volume`. Obsolete."""

        _Pan = 3
        """See `Channel.pan`. Obsolete."""

        Zipped = 15
        """See `Channel.zipped`. Default event is not stored."""

        UseLoopPoints = 19
        Kind = 21
        """Stores `ChannelKind`, used by `Channel.kind`."""

        TargetInsert = 22
        """See `Channel.insert`."""

        # FXProperties = 27
        Locked = 32
        """See `Channel.locked`. FL 12.3+."""

        New = WORD
        """Marks the beginning of a new channel."""

        # Fx = WORD + 5
        # FadeStereo = WORD + 6
        _Volume = WORD + 8
        """See `Channel.volume`. Deprecates `ChannelEventID._Vol`. Obsolete."""

        _Panning = WORD + 9
        """See `Channel.pan`. Deprecates `ChannelEventID._Pan`. Obsolete."""

        # DotNote = WORD + 13
        # DotPitch = WORD + 14
        # DotMix = WORD + 15
        # Fx3 = WORD + 22
        # DotReso = WORD + 23
        # DotCutOff = WORD + 24
        # ShiftDelay = WORD + 25
        # Dot = WORD + 27
        # DotRel = WORD + 32
        # DotShift = WORD + 28

        LayerChildren = WORD + 30
        """Stores index of a child `Channel`. See `Channel.children`.
        Used by layer channels only. Each child has its own events."""

        Swing = WORD + 33
        """See `Channel.swing`."""

        Color = DWORD
        """See `Channel.color`. Defaults to #485156."""

        # Echo = DWORD + 2
        # FxSine = DWORD + 3

        CutSelfCutBy = DWORD + 4
        """See `Channel.cut_group`. Default event (0, 0)
        is not stored only for Layer channels."""

        RootNote = DWORD + 7
        """See `Channel.root_note`. Default event is not stored."""

        # _MainResoCutOff = DWORD + 9
        """Obsolete."""

        # DelayModXY = DWORD + 10

        StretchTime = DWORD + 12
        """See `Channel.stretch_time`."""

        # FineTune = DWORD + 14
        SamplerFlags = DWORD + 15
        """See `Channel.sampler_flags`."""

        LayerFlags = DWORD + 16
        """See `Channel.layer_flags`."""

        FilterChannelNum = DWORD + 17
        """See `Channel.filter_channel`."""

        AUSampleRate = DWORD + 25
        """See `Channel.au_sample_rate`. Possibly obsolete."""

        Icon = DWORD + 27
        """Index of the icon used. See `Channel.icon`."""

        SamplePath = TEXT + 4
        """See `Channel.sample_path`. Default event is not stored."""

        DefaultName = TEXT + 9
        """See `Channel.default_name`."""

        Name = TEXT + 11
        """See `Channel.name`. Default event is not stored."""

        Delay = DATA + 1
        """See `Channel.delay`. Implemented by `ChannelDelayEvent`."""

        Plugin = DATA + 5
        """See `Channel.plugin`. Implemented by `Plugin`."""

        Parameters = DATA + 7
        """See `Channel.parameters`. Implemented by `ChannelParametersEvent`."""

        Levels = DATA + 11
        """See `Channel.levels`. Implemented by `ChannelLevelsEvent`."""

        # _Filter = DATA + 12
        Polyphony = DATA + 13
        """See `Channel.polyphony`. Implemented by `ChannelPolyphonyEvent`."""

        EnvelopeLFO = DATA + 10
        """See `Channel.env_lfos`. Impelemented by `ChannelEnvelopeLFOEvent`"""

        Tracking = DATA + 20
        """See `Channel.tracking`. Implemented by `ChannelTrackingEvent`."""

        LevelOffsets = DATA + 21
        """See `Channel.level_offsets`. Implemented by `ChannelLevelOffsetsEvent`."""

    # * Properties
    default_name: Optional[str] = _StrProperty()
    """Default name of the channel.
    The value of this depends on the type of `plugin`:

    * Native (stock) plugin: The factory name of the plugin.
    * VST instruments: "Fruity Wrapper".

    See `name` also."""

    index: Optional[int] = _UIntProperty()

    volume: Optional[int] = _UIntProperty(max_=12800)
    """Min: 0, Max: 12800, Default: 10000."""

    pan: Optional[int] = _UIntProperty(max_=12800)
    """Min: 0, Max: 12800, Default: 6400."""

    color: Optional[colour.Color] = _ColorProperty()

    target_insert: Optional[int] = _IntProperty(min_=-1)
    """The index of the `Insert` the channel is routed to."""

    kind: Optional[Kind] = _EnumProperty(Kind)
    """Type of channel. See `Kind`."""

    enabled: Optional[bool] = _BoolProperty()
    """Whether the channel is in enabled state."""

    locked: Optional[bool] = _BoolProperty()
    """Whether the channel is locked in the channel rack. Paired with
    the `Channel.enabled`, it represents actual state of the channel."""

    zipped: bool = _BoolProperty()
    """Whether the channel is in zipped state."""

    root_note: Optional[int] = _IntProperty()
    """Miscellaneous settings -> Root note. Min: 0 (C0), Max: 131 (B10)"""

    icon: Optional[int] = _IntProperty()

    sample_path: Optional[str] = _StrProperty()
    """Absolute path of a sample file on the disk. Valid only if
    `Channel.kind` is `ChannelKind.Sampler` or `ChannelKind.Audio`.
    Contains '%FLStudioFactoryData%' for stock samples."""

    # TODO Maybe the lower limit for this is -1
    filter_channel: Optional[int] = _IntProperty()
    """Display filter under which this channel is grouped. See `Filter`."""

    @property
    def plugin(self) -> Optional[_Plugin]:
        """The `Plugin` associated with the channel. Valid
        only if `kind` is `ChannelKind.Instrument`."""
        return getattr(self, "_plugin", None)

    @property
    def children(self) -> List[int]:
        """List of children `index`es of a Layer.
        Valid only if `kind` is `ChannelKind.Layer`."""
        return getattr(self, "_layer_children")

    @property
    def fx(self) -> Optional[ChannelFX]:
        """See `ChannelFX`."""
        return getattr(self, "_fx", None)

    name: Optional[str] = _StrProperty()
    """The value of this depends on the type of `plugin`:

    * Native (stock) plugin: User-given name. Default event is not stored.
    * VST plugin (VSTi): The name obtained from the VST, or the user-given name.
        Default event (i.e VST plugin name) is stored.

    See `default_name` also."""

    # TODO Discover
    sampler_flags: Optional[int] = _IntProperty()
    """Flags associated with `Channel` of kind `Kind.Sampler`."""

    # TODO Discover
    layer_flags: Optional[int] = _IntProperty()
    """Flags associated with a `Channel` of kind `Kind.Layer`."""

    use_loop_points: Optional[bool] = _BoolProperty()
    """Sampler/Audio -> Playback -> Use loop points."""

    swing: Optional[int] = _UIntProperty()
    """Sampler/Instruemnt -> Miscellaneous functions -> Time -> Swing."""

    @property
    def delay(self) -> Optional[ChannelDelay]:
        """See `ChannelDelay`."""
        return getattr(self, "_delay", None)

    @property
    def polyphony(self) -> Optional[ChannelPolyphony]:
        """See `ChannelPolyphony`."""
        return getattr(self, "_polyphony", None)

    @property
    def levels(self) -> Optional[ChannelLevels]:
        """See `ChannelLevels`."""
        return getattr(self, "_levels", None)

    @property
    def tracking_vol(self) -> Optional[ChannelTracking]:
        """Volume tracking. See `ChannelTracking`."""
        return getattr(self, "_tracking_vol", None)

    @property
    def tracking_key(self) -> Optional[ChannelTracking]:
        """Key tracking. See `ChannelTracking`."""
        return getattr(self, "_tracking_key", None)

    @property
    def level_offsets(self) -> Optional[ChannelLevelOffsets]:
        """See `ChannelLevelOffsets`."""
        return getattr(self, "_level_offsets", None)

    stretch_time: Optional[int] = _UIntProperty()
    """Sampler/Audio -> Time stretching -> Time.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_sampler.htm#Sampler_Beatmatching)"""  # noqa

    au_sample_rate: Optional[int] = _UIntProperty()
    """AU-format sample specific."""

    @property
    def arp(self) -> Optional[ChannelArp]:
        """See `ChannelArp` and `ChannelParametersEvent`."""
        return getattr(self, "_arp", None)

    @property
    def env_lfos(self) -> Dict[str, ChannelEnvelopeLFO]:
        """Channel AHDSR envelopes and LFOs for Panning, Volume, Pitch, Mod X (Cutoff)
        and Mod Y (Resonance). See `ChannelEnvelope` and `ChannelEnvelopeEvent`."""
        return getattr(self, "_env_lfos", {})

    @property
    def cut_group(self) -> Tuple[int]:
        """Cut group in the form of (Cut self, cut by)."""
        return getattr(self, "_cut_group", tuple())

    @cut_group.setter
    def cut_group(self, value: Tuple[int]):
        if len(value) != 2:
            raise TypeError("Expected a tuple of size 2")
        self._events["cut_group"]._data = struct.pack("2H", *value)
        self._cut_group = value

    # * Parsing logic
    def parse_event(self, e: EventType) -> None:
        if e.id_ in ChannelFX.EventID.__members__.values():
            if not hasattr(self, "_fx"):
                self._fx = ChannelFX()
            return self._fx.parse_event(e)
        return super().parse_event(e)

    def _parse_byte_event(self, e: ByteEventType) -> None:
        if e.id_ == Channel.EventID.Enabled:
            self._parse_bool(e, "enabled")
        elif e.id_ == Channel.EventID._Vol:
            self._parse_B(e, "volume")
        elif e.id_ == Channel.EventID._Pan:
            self._parse_b(e, "pan")
        elif e.id_ == Channel.EventID.Kind:
            self._events["kind"] = e
            kind = e.to_uint8()
            try:
                self._kind = Channel.Kind(kind)
            except AttributeError:
                self._kind = kind
        elif e.id_ == Channel.EventID.Zipped:
            self._parse_bool(e, "zipped")
        elif e.id_ == Channel.EventID.UseLoopPoints:
            self._parse_bool(e, "use_loop_points")
        elif e.id_ == Channel.EventID.TargetInsert:
            self._parse_b(e, "target_insert")
        elif e.id_ == Channel.EventID.Locked:
            self._parse_bool(e, "locked")

    def _parse_word_event(self, e: WordEventType) -> None:
        if e.id_ == Channel.EventID.New:
            self._parse_H(e, "index")
        elif e.id_ == Channel.EventID._Volume:
            self._parse_H(e, "volume")
        elif e.id_ == Channel.EventID._Panning:
            self._parse_h(e, "pan")
        elif e.id_ == Channel.EventID.LayerChildren:
            self._events[f"child{len(self._layer_children)}"] = e
            self._layer_children.append(e.to_uint16())
        elif e.id_ == Channel.EventID.Swing:
            self._parse_H(e, "swing")

    def _parse_dword_event(self, e: DWordEventType) -> None:
        if e.id_ == Channel.EventID.Color:
            self._parse_color(e, "color")
        elif e.id_ == Channel.EventID.CutSelfCutBy:
            self._parseprop(e, "cut_group", struct.unpack("2H", e.data))
        elif e.id_ == Channel.EventID.RootNote:
            self._parse_I(e, "root_note")
        elif e.id_ == Channel.EventID.StretchTime:
            self._parse_I(e, "stretch_time")
        elif e.id_ == Channel.EventID.SamplerFlags:
            self._parse_I(e, "sampler_flags")
        elif e.id_ == Channel.EventID.LayerFlags:
            self._parse_I(e, "layer_flags")
        elif e.id_ == Channel.EventID.FilterChannelNum:
            self._parse_i(e, "filter_channel")
        elif e.id_ == Channel.EventID.Icon:
            self._parse_I(e, "icon")
        elif e.id_ == Channel.EventID.AUSampleRate:
            self._parse_I(e, "au_sample_rate")

    def _parse_text_event(self, e: TextEventType) -> None:
        if e.id_ == Channel.EventID.DefaultName:
            self._parse_s(e, "default_name")
        elif e.id_ == Channel.EventID.SamplePath:
            self._parse_s(e, "sample_path")
        elif e.id_ == Channel.EventID.Name:
            self._parse_s(e, "name")

    def _parse_data_event(self, e: DataEventType) -> None:
        if e.id_ == Channel.EventID.Plugin:
            if self.default_name == "BooBass":
                plugin = BooBass()
            elif self.default_name == "Fruity Wrapper":
                plugin = VSTPlugin()
            else:
                plugin = _Plugin()
            self._parse_flobject(e, "plugin", plugin)
        elif e.id_ == Channel.EventID.Delay:
            self._parse_flobject(e, "delay", ChannelDelay())
        elif e.id_ == Channel.EventID.Polyphony:
            self._parse_flobject(e, "polyphony", ChannelPolyphony())
        elif e.id_ == Channel.EventID.LevelOffsets:
            self._parse_flobject(e, "level_offsets", ChannelLevelOffsets())
        elif e.id_ == Channel.EventID.Levels:
            self._parse_flobject(e, "levels", ChannelLevels())
            self._volume = self.levels.volume
            self._pan = self.levels.pan
        elif e.id_ == Channel.EventID.Tracking:
            self.__tracking_events.append(e)
            ct = ChannelTracking()
            ct.parse_event(e)
            if not self.tracking_vol:
                self._tracking_vol = ct
            else:
                self._tracking_key = ct
        elif e.id_ == Channel.EventID.Parameters:
            self._events["parameters"] = e
            self._arp = e.arp
        elif e.id_ == Channel.EventID.EnvelopeLFO:
            idx = len(self.__envlfo_events)
            name = EnvelopeLFONames[idx]
            self.__envlfo_events.append(e)
            el = ChannelEnvelopeLFO()
            el.parse_event(e)
            self._env_lfos[name] = el

    def _save(self) -> List[EventType]:
        if self.plugin:
            self.plugin._save()
        events = list(super()._save())
        if self.fx:
            events.extend(list(self.fx._save()))
        events.extend(self.__tracking_events)
        events.extend(self.__envlfo_events)
        return events

    # * Utility methods
    def get_name(self) -> Optional[str]:
        if self.name:
            return self.name
        return self.default_name
