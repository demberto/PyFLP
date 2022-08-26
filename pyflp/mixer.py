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
pyflp.mixer
===========

Contains the types used by the mixer, inserts and effect slots.
"""

import collections
import enum
import sys
from typing import (
    Any,
    DefaultDict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sized,
    cast,
)

if sys.version_info >= (3, 8):
    from typing import SupportsIndex, TypedDict
else:
    from typing_extensions import SupportsIndex, TypedDict

import colour

from ._base import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    ColorEvent,
    EventEnum,
    EventProp,
    FlagProp,
    I16Event,
    I32Event,
    KWProp,
    ListEventBase,
    ModelBase,
    MultiEventModel,
    NamedPropMixin,
    ROProperty,
    RWProperty,
    StructBase,
    StructEventBase,
    T,
    U16Event,
)
from .controller import RemoteController
from .plugin import IPlugin, PluginID


class InsertFlagsStruct(StructBase):
    PROPS = {"_u1": "I", "flags": "I", "_u2": "I"}


class InsertRoutingStruct(StructBase):
    PROPS = {"is_routed": "bool"}


class MixerParamsItem(StructBase):
    PROPS = {
        "_u4": 4,  # 4
        "id": "b",  # 5
        "_u1": 1,  # 6
        "channel_data": "H",  # 8
        "msg": "i",  # 12
    }


class InsertFlagsEvent(StructEventBase):
    STRUCT = InsertFlagsStruct


class InsertRoutingEvent(ListEventBase):
    STRUCT = InsertRoutingStruct


class MixerParamsEvent(ListEventBase):
    STRUCT = MixerParamsItem


@enum.unique
class InsertID(EventEnum):
    Icon = (WORD + 31, I16Event)
    Output = (DWORD + 19, I32Event)
    Color = (DWORD + 21, ColorEvent)
    Input = (DWORD + 26, I32Event)
    Name = TEXT + 12
    Routing = (DATA + 27, InsertRoutingEvent)
    Flags = (DATA + 28, InsertFlagsEvent)


@enum.unique
class MixerID(EventEnum):
    Params = (DATA + 17, MixerParamsEvent)


@enum.unique
class SlotID(EventEnum):
    Index = (WORD + 34, U16Event)


@enum.unique
class MixerParamsID(enum.IntEnum):
    SlotEnabled = 0
    # SlotVolume = 1
    SlotMix = 1
    RouteVolStart = 64  # 64 - 191 are send level events
    Volume = 192
    Pan = 193
    StereoSeparation = 194
    LowGain = 208
    MidGain = 209
    HighGain = 210
    LowFreq = 216
    MidFreq = 217
    HighFreq = 218
    LowQ = 224
    MidQ = 225
    HighQ = 226


class InsertDock(enum.Enum):
    Left = enum.auto()
    Middle = enum.auto()
    Right = enum.auto()


@enum.unique
class InsertFlags(enum.IntFlag):
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


class _InsertEQBandKW(TypedDict, total=False):
    gain: MixerParamsItem
    freq: MixerParamsItem
    reso: MixerParamsItem


class _InsertEQBandProp(NamedPropMixin, RWProperty[int]):
    def __get__(self, instance: ModelBase, owner: Any = None) -> Optional[int]:
        if not isinstance(instance, InsertEQBand) or owner is None:
            return NotImplemented
        return instance._kw[self._prop]["msg"]

    def __set__(self, instance: ModelBase, value: int):
        instance._kw[self._prop]["msg"] = value


class InsertEQBand(ModelBase):
    def __init__(self, **kw: _InsertEQBandKW):
        super().__init__(**kw)

    def __repr__(self):
        return f"InsertEQ band (gain={self.gain}, freq={self.freq}, q={self.reso})"

    gain = _InsertEQBandProp()
    """
    | Type     | Value |
    | -------- | :---: |
    | Min      | -1800 |
    | Max      | 1800  |
    | Default  | 0     |
    """

    freq = _InsertEQBandProp()
    """Min: 0, Max: 65536, default depends on band."""

    reso = _InsertEQBandProp()
    """Min: 0, Max: 65536, Default: 17500."""


class _InsertEQPropArgs(NamedTuple):
    freq: MixerParamsID
    gain: MixerParamsID
    reso: MixerParamsID


class _InsertEQProp(NamedPropMixin, ROProperty[InsertEQBand]):
    def __init__(self, ids: _InsertEQPropArgs) -> None:
        super().__init__()
        self._ids = ids

    def __get__(self, instance: Any, owner: Any = None) -> InsertEQBand:
        if not isinstance(instance, InsertEQ) or owner is None:
            return NotImplemented

        items: _InsertEQBandKW = {}
        for param in instance._kw["params"]:
            id = param["id"]
            if id == self._ids.freq:
                items["freq"] = param
            elif id == self._ids.gain:
                items["gain"] = param
            elif id == self._ids.reso:
                items["reso"] = param
        return InsertEQBand(kw=items)


class InsertEQ(ModelBase):
    def __init__(self, params: List[MixerParamsItem]):
        super().__init__(kw={"params": params})

    def __repr__(self):
        low = f"{self.low.freq},{self.low.gain},{self.low.reso}"
        mid = f"{self.mid.freq},{self.mid.gain},{self.mid.reso}"
        high = f"{self.high.freq},{self.high.gain},{self.high.reso}"
        return f"InsertEQ (low={low}, mid={mid}, high={high})"

    low = _InsertEQProp(
        _InsertEQPropArgs(
            MixerParamsID.LowFreq, MixerParamsID.LowGain, MixerParamsID.LowQ
        )
    )
    """Low shelf band. Default frequency: 5777 (90 Hz)."""

    mid = _InsertEQProp(
        _InsertEQPropArgs(
            MixerParamsID.MidFreq, MixerParamsID.MidGain, MixerParamsID.MidQ
        )
    )
    """Middle band. Default frequency: 33145 (1500 Hz)."""

    high = _InsertEQProp(
        _InsertEQPropArgs(
            MixerParamsID.HighFreq, MixerParamsID.HighGain, MixerParamsID.HighQ
        )
    )
    """High shelf band. Default frequency: 55825 (8000 Hz)."""


class _MixerParamProp(RWProperty[T]):
    def __init__(self, id: MixerParamsID) -> None:
        self._id = id

    def __get__(self, instance: Any, owner: Any = None) -> Optional[T]:
        if not isinstance(instance, Insert) or owner is None:
            return NotImplemented

        for param in instance._kw["params"]:
            if param["id"] == self._id:
                return param["msg"]

    def __set__(self, instance: Any, value: T):
        if not isinstance(instance, Insert):
            return NotImplemented

        for param in instance._kw["params"]:
            if param["id"] == self._id:
                param["msg"] = value


class Slot(MultiEventModel, SupportsIndex):
    """Represents an effect slot in an `Insert` / mixer channel."""

    def __init__(
        self,
        params: List[MixerParamsItem],
        *events: AnyEvent,
        plugin: Optional[IPlugin] = None,
    ):
        super().__init__(*events, kw={"params": params, "plugin": plugin})

    def __repr__(self) -> str:
        repr = "Unnamed slot" if self.name is None else f"Slot {self.name!r}"
        if self.plugin is None:
            return f"Empty {repr.lower()}"
        return f"{repr} ({self.plugin.DEFAULT_NAME})"

    def __index__(self) -> int:
        if SlotID.Index not in self._events:
            return NotImplemented
        return self._events[SlotID.Index][0].value

    color = EventProp[colour.Color](PluginID.Color)
    controllers = KWProp[List[RemoteController]]()  # TODO
    default_name = EventProp[str](PluginID.DefaultName)
    """'Fruity Wrapper' for VST/AU plugins or factory name for native plugins."""

    enabled = _MixerParamProp[bool](MixerParamsID.SlotEnabled)
    icon = EventProp[int](PluginID.Icon)
    index = EventProp[int](SlotID.Index)
    mix = _MixerParamProp[int](MixerParamsID.SlotMix)
    """Dry/Wet mix.

    | Type     | Value | Representation |
    | -------- | :---: | :------------: |
    | Min      | 0     | 0%             |
    | Max      | 12800 | 100%           |
    | Default  | 12800 | 100%           |
    """

    name = EventProp[str](PluginID.Name)
    plugin = KWProp[IPlugin]()
    """The effect loaded into the slot."""


class Insert(MultiEventModel, Iterable[Slot], SupportsIndex):
    """Represents a channel in the mixer."""

    def __init__(
        self,
        index: SupportsIndex,
        *events: AnyEvent,
        params: List[MixerParamsItem] = [],
    ):
        super().__init__(*events, kw={"index": index, "params": params})

    # TODO add num of used slots
    def __repr__(self):
        if self.name is None:
            return "Unnamed insert"
        return f"Insert {self.name!r}"

    def __index__(self):
        return self._kw["index"]

    def __iter__(self):
        return self.slots

    bypassed = FlagProp(InsertFlags.EnableEffects, InsertID.Flags, inverted=True)
    """Whether all slots are bypassed."""

    channels_swapped = FlagProp(InsertFlags.SwapLeftRight, InsertID.Flags)
    """Whether the left and right channels are swapped."""

    color = EventProp[colour.Color](InsertID.Color)

    @property
    def dock(self) -> Optional[InsertDock]:
        events = self._events.get(InsertID.Flags)
        if events is not None:
            event = cast(InsertFlagsEvent, events[0])
            if InsertFlags.DockMiddle in event["flags"]:
                return InsertDock.Middle
            elif InsertFlags.DockRight in event["flags"]:
                return InsertDock.Right
            return InsertDock.Left

    enabled = FlagProp(InsertFlags.Enabled, InsertID.Flags)
    """Whether an insert in the mixer is enabled or disabled."""

    @property
    def eq(self) -> InsertEQ:
        """3-band post EQ."""
        return InsertEQ(self._kw["params"])

    icon = EventProp[int](InsertID.Icon)
    input = EventProp[int](InsertID.Input)
    is_solo = FlagProp(InsertFlags.Solo, InsertID.Flags)
    """Whether the insert is solo'd."""

    locked = FlagProp(InsertFlags.Locked, InsertID.Flags)
    """Whether an insert in the mixer is in locked state."""

    name = EventProp[str](InsertID.Name)
    output = EventProp[int](InsertID.Output)
    pan = _MixerParamProp[int](MixerParamsID.Pan)
    """
    | Type     | Value | Representation |
    | -------- | :---: | -------------- |
    | Min      | -6400 | 100% left      |
    | Max      | 6400  | 100% right     |
    | Default  | 0     | Centred        |
    """

    polarity_reversed = FlagProp(InsertFlags.PolarityReversed, InsertID.Flags)
    """Whether phase / polarity is reversed / inverted."""

    @property
    def routes(self) -> Iterator[int]:
        """Send volumes to routed inserts."""
        items = cast(InsertRoutingEvent, self._events[InsertID.Routing][0]).items
        for idx, param in enumerate(self._kw["params"]):
            if param["id"] >= MixerParamsID.RouteVolStart and items[idx]["is_routed"]:
                yield param["msg"]

    separator_shown = FlagProp(InsertFlags.SeparatorShown, InsertID.Flags)
    """Whether separator is shown before the insert."""

    @property
    def slots(self) -> Iterator[Slot]:
        """Effect slots (upto 10 as of the latest version)."""
        index = 0
        while True:
            events: List[AnyEvent] = []
            params: List[MixerParamsItem] = []

            for param in self._kw["params"]:
                if param["channel_data"] % 0x3F == index:
                    params.append(param)

            for id, events in self._events.items():
                if id in SlotID or id in PluginID:
                    try:
                        events.append(events[index])
                    except IndexError:
                        pass

            if len(events) == 0:
                break

            index += 1
            yield Slot(params, *events)

    stereo_separation = _MixerParamProp[int](MixerParamsID.StereoSeparation)
    """
    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -64   | 100% merged    |
    | Max     | 64    | 100% separated |
    | Default | 0     | No effect      |
    """

    volume = _MixerParamProp[int](MixerParamsID.Volume)
    """Post volume fader.

    | Type     | Value | Representation         |
    | -------- | :---: | ---------------------- |
    | Min      | 0     | 0% / -INFdB / 0.00     |
    | Max      | 16000 | 125% / 5.6dB / 1.90    |
    | Default  | 12800 | 100% / 0.0dB / 1.00    |
    """


class Mixer(MultiEventModel, Iterable[Insert], Sized):
    def __iter__(self) -> Iterator[Insert]:
        return self.inserts

    def __repr__(self):
        return f"Mixer: {len(tuple(self.inserts))} inserts"

    def __len__(self):
        return len(list(self.inserts))

    @property
    def inserts(self) -> Iterator[Insert]:
        index = 0
        events: List[AnyEvent] = []
        params_dict: DefaultDict[int, List[MixerParamsItem]] = collections.defaultdict(
            list
        )

        for event in reversed(self._events_tuple):
            if event.id == MixerID.Params:
                event = cast(MixerParamsEvent, event)
                items = cast(List[MixerParamsItem], event.items)

                for item in items:
                    params_dict[(item["channel_data"] >> 6) & 0x7F].append(item)

        for event in self._events_tuple:
            for enum in (InsertID, SlotID):
                if event.id in enum:
                    events.append(event)

            if event.id == InsertID.Output:
                try:
                    params_list = params_dict[index]
                except IndexError:
                    yield Insert(index, *events)
                else:
                    yield Insert(index, *events, params=params_list)
                events = []
                index += 1
