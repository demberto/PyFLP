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

from __future__ import annotations

import collections
import dataclasses
import enum
import sys
from typing import DefaultDict, List, NamedTuple, cast

if sys.version_info >= (3, 8):
    from typing import SupportsIndex, TypedDict
else:
    from typing_extensions import SupportsIndex, TypedDict

if sys.version_info >= (3, 9):
    from collections.abc import Iterator, Sequence
else:
    from typing import Iterator, Sequence

if sys.version_info >= (3, 11):
    from typing import Never, NotRequired, Unpack
else:
    from typing_extensions import NotRequired, Unpack, Never

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
    FLVersion,
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
from .exceptions import ModelNotFound, NoModelsFound
from .plugin import (
    AnyPlugin,
    FruityBalance,
    FruityBalanceEvent,
    FruityFastDist,
    FruityFastDistEvent,
    FruityNotebook2,
    FruityNotebook2Event,
    FruitySend,
    FruitySendEvent,
    FruitySoftClipper,
    FruitySoftClipperEvent,
    FruityStereoEnhancer,
    FruityStereoEnhancerEvent,
    IPlugin,
    PluginID,
    VSTPlugin,
    VSTPluginEvent,
)


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
    Color = (DWORD + 21, ColorEvent)  # 4.0+
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
    def __get__(self, instance: ModelBase, owner: object = None) -> int | None:
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

    def sizeof(self) -> int:
        return MixerParamsItem.SIZE * len(self._kw)

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

    def __get__(self, instance: object, owner: object = None) -> InsertEQBand:
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
    def __init__(self, params: list[MixerParamsItem]):
        super().__init__(params=params)

    def __repr__(self):
        low = f"{self.low.freq},{self.low.gain},{self.low.reso}"
        mid = f"{self.mid.freq},{self.mid.gain},{self.mid.reso}"
        high = f"{self.high.freq},{self.high.gain},{self.high.reso}"
        return f"InsertEQ (low={low}, mid={mid}, high={high})"

    def sizeof(self) -> int:
        return MixerParamsItem.SIZE * self._kw["param"]

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

    def __get__(self, instance: Insert, owner: object = None) -> T | None:
        if owner is None:
            return NotImplemented

        for param in instance._kw["params"]:
            if param["id"] == self._id:
                return param["msg"]

    def __set__(self, instance: Insert, value: T):
        for param in instance._kw["params"]:
            if param["id"] == self._id:
                param["msg"] = value


class Slot(MultiEventModel, SupportsIndex):
    """Represents an effect slot in an `Insert` / mixer channel."""

    def __init__(
        self,
        params: list[MixerParamsItem],
        *events: AnyEvent,
        plugin: IPlugin | None = None,
    ):
        super().__init__(*events, kw={"params": params, "plugin": plugin})

    def __repr__(self) -> str:
        repr = "Unnamed slot" if self.name is None else f"Slot {self.name!r}"
        if self.plugin is None:
            return f"Empty {repr.lower()}"
        return f"{repr} ({self.plugin.INTERNAL_NAME})"  # type: ignore

    def __index__(self) -> int:
        if SlotID.Index not in self._events:
            return NotImplemented
        return self._events[SlotID.Index][0].value

    color = EventProp[colour.Color](PluginID.Color)
    controllers = KWProp[List[RemoteController]]()  # TODO
    internal_name = EventProp[str](PluginID.InternalName)
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

    @property
    def plugin(self) -> AnyPlugin | bytes | None:
        """The effect loaded into the slot."""
        try:
            event = self._events[PluginID.Data][0]
        except (KeyError, IndexError):
            return

        if isinstance(event, VSTPluginEvent):
            return VSTPlugin(event)
        elif isinstance(event, FruityBalanceEvent):
            return FruityBalance(event)
        elif isinstance(event, FruityFastDistEvent):
            return FruityFastDist(event)
        elif isinstance(event, FruityNotebook2Event):
            return FruityNotebook2(event)
        elif isinstance(event, FruitySendEvent):
            return FruitySend(event)
        elif isinstance(event, FruitySoftClipperEvent):
            return FruitySoftClipper(event)
        elif isinstance(event, FruityStereoEnhancerEvent):
            return FruityStereoEnhancer(event)

        return event._raw

    @plugin.setter
    def plugin(self, plugin: AnyPlugin):
        if isinstance(plugin, IPlugin):
            self.internal_name = plugin.INTERNAL_NAME
        self._events[PluginID.Data] = [plugin.event()]


class _InsertKW(TypedDict):
    index: SupportsIndex
    params: NotRequired[list[MixerParamsItem]]


class Insert(MultiEventModel, Sequence[Slot], SupportsIndex):
    """Represents a mixer track to which channel from the rack are routed to."""

    def __init__(self, *events: AnyEvent, **kw: Unpack[_InsertKW]):
        super().__init__(*events, **kw)

    # TODO Add number of used slots
    def __repr__(self):
        if self.name is None:
            return f"Unnamed insert #{self.__index__()}"
        return f"Insert {self.name!r} #{self.__index__()}"

    def __getitem__(self, index: SupportsIndex):
        """Returns an effect slot of the specified `index`.

        Args:
            index (SupportsIndex): A zero based integer value.

        Raises:
            ModelNotFound: An effect slot with the specified `index` couldn't be found.
        """
        for idx, slot in enumerate(self):
            if idx == index:
                return slot
        raise ModelNotFound(index)

    def __index__(self) -> int:
        return self._kw["index"]

    def __iter__(self):
        """Provides an iterator over the effect slots (empty & used) of an insert."""
        index = 0
        while True:
            events: list[AnyEvent] = []
            params: list[MixerParamsItem] = []

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

    def __len__(self):
        if SlotID.Index in self._events:
            return len(self._events[SlotID.Index])
        return len(list(self))

    bypassed = FlagProp(InsertFlags.EnableEffects, InsertID.Flags, inverted=True)
    """Whether all slots are bypassed."""

    channels_swapped = FlagProp(InsertFlags.SwapLeftRight, InsertID.Flags)
    """Whether the left and right channels are swapped."""

    color = EventProp[colour.Color](InsertID.Color)
    """*New in FL Studio v4.0*."""

    @property
    def dock(self) -> InsertDock | None:
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
    """Linear.

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
        """Send volumes to routed inserts.

        *New in FL Studio v4.0*.
        """
        items = cast(InsertRoutingEvent, self._events[InsertID.Routing][0]).items
        for idx, param in enumerate(self._kw["params"]):
            if param["id"] >= MixerParamsID.RouteVolStart and items[idx]["is_routed"]:
                yield param["msg"]

    separator_shown = FlagProp(InsertFlags.SeparatorShown, InsertID.Flags)
    """Whether separator is shown before the insert."""

    stereo_separation = _MixerParamProp[int](MixerParamsID.StereoSeparation)
    """Linear.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -64   | 100% merged    |
    | Max     | 64    | 100% separated |
    | Default | 0     | No effect      |
    """

    volume = _MixerParamProp[int](MixerParamsID.Volume)
    """Post volume fader. Logarithmic.

    | Type     | Value | Representation         |
    | -------- | :---: | ---------------------- |
    | Min      | 0     | 0% / -INFdB / 0.00     |
    | Max      | 16000 | 125% / 5.6dB / 1.90    |
    | Default  | 12800 | 100% / 0.0dB / 1.00    |
    """


class _MixerKW(TypedDict):
    version: FLVersion


# TODO FL Studio version in which slots were increased to 10
# TODO A move() method to change the placement of Inserts; it's difficult!
class Mixer(MultiEventModel, Sequence[Insert]):
    def __init__(self, *events: AnyEvent, **kw: Unpack[_MixerKW]):
        super().__init__(*events, **kw)

    # Inserts don't store their index internally.
    def __getitem__(self, index: SupportsIndex):
        """Returns an insert with the specified `index`.

        Args:
            index (SupportsIndex): A zero based integer value.

        Raises:
            ModelNotFound: An insert with the specified `index` could not be found.
        """
        for idx, insert in enumerate(self):
            if idx == index:
                return insert
        raise ModelNotFound(index)

    def __iter__(self) -> Iterator[Insert]:
        index = 0
        events: list[AnyEvent] = []
        params_dict: DefaultDict[int, list[MixerParamsItem]] = collections.defaultdict(
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
                    yield Insert(*events, index=index)
                else:
                    yield Insert(*events, index=index, params=params_list)
                events = []
                index += 1

    def __len__(self):
        """Returns the number of inserts present in the project.

        Raises:
            NoModelsFound: When no inserts could be found.
        """
        if InsertID.Flags not in self._events:
            raise NoModelsFound
        return len(self._events[InsertID.Flags])

    def __repr__(self):
        return f"Mixer: {len(self)} inserts"

    @property
    def max_inserts(self):
        """Estimated max number of inserts including sends, master and current.

        * 1.6.5: 4 inserts + master, 5 in total
        * 2.0.1: 8
        * 3.0.0: 16 inserts, 2 sends.
        * 3.3.0: +2 sends.
        * 4.0.0: 64
        * 9.0.0: 99 inserts, 105 in total.
        * 12.9.0: 125 + master + current.
        """
        version = dataclasses.astuple(self._kw["version"])

        if version >= (1, 6, 5):
            return 5
        elif version >= (2, 0, 1):
            return 8
        elif version >= (3, 0, 0):
            return 18
        elif version >= (3, 3, 0):
            return 20
        elif version >= (4, 0, 0):
            return 64
        elif version >= (9, 0, 0):
            return 105
        elif version >= (12, 9, 0):
            return 127

        return Never

    @property
    def max_slots(self):
        """Estimated max number of effect slots per insert.

        * 1.6.5: 4
        * 3.3.0: 8
        """
        version = dataclasses.astuple(self._kw["version"])

        if version >= (1, 6, 5):
            return 4
        elif version >= (3, 3, 0):
            return 8
        return 10
