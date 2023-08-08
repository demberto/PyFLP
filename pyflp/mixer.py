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

"""Contains the types used by the mixer, inserts and effect slots."""

from __future__ import annotations

import enum
from collections import defaultdict
from typing import Any, Generic, Iterator, NamedTuple, TypeVar, cast

import attrs
import construct as c
import construct_typed as ct

from pyflp._adapters import StdEnum
from pyflp._descriptors import EventProp, FlagProp, NamedPropMixin
from pyflp._events import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    ColorAdapter,
    EventEnum,
    EventProxy,
    RGBA,
    I16Event,
    I32Event,
    ListEventBase,
    make_struct_event,
    U16Event,
)
from pyflp.plugin import (
    FruityBalance,
    FruityBloodOverdrive,
    FruityCenter,
    FruityFastDist,
    FruityNotebook2,
    FruitySend,
    FruitySoftClipper,
    FruityStereoEnhancer,
    PluginID,
    PluginProp,
    Soundgoodizer,
    VSTPlugin,
)

__all__ = ["Insert", "InsertDock", "InsertEQ", "InsertEQBand", "Mixer", "Slot"]

_T = TypeVar("_T")


@enum.unique
class _InsertFlags(enum.IntFlag):
    None_ = 0
    PolarityReversed = 1 << 0
    SwapLeftRight = 1 << 1
    EnableEffects = 1 << 2
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
    AudioTrack = 1 << 15  # Whether insert is linked to an audio track


@enum.unique
class _MixerParamsID(ct.EnumBase):
    SlotEnabled = 0
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


InsertFlagsEvent = make_struct_event(
    "_u1" / c.Bytes(4),  # 4
    "flags" / StdEnum[_InsertFlags](c.Int32ul),  # 8
    "_u2" / c.Bytes(4),  # 12
)


class InsertRoutingEvent(ListEventBase):
    STRUCT = c.GreedyRange(c.Flag)


@attrs.define
class _InsertItems:
    slots: defaultdict[int, dict[int, dict[str, Any]]] = attrs.field(
        factory=lambda: defaultdict(dict)
    )
    own: dict[int, dict[str, Any]] = attrs.field(factory=dict)


class MixerParamsEvent(ListEventBase):
    STRUCT = c.GreedyRange(
        c.Struct(
            "_u4" / c.Bytes(4),  # 4
            "id" / StdEnum[_MixerParamsID](c.Byte),  # 5
            "_u1" / c.Byte,  # 6
            "channel_data" / c.Int16ul,  # 8
            "msg" / c.Int32sl,  # 12
        )
    )

    def __init__(self, id: Any, data: bytes) -> None:
        super().__init__(id, data)
        self.items_: defaultdict[int, _InsertItems] = defaultdict(_InsertItems)

        for item in self.value:
            insert_idx = (item["channel_data"] >> 6) & 0x7F
            slot_idx = item["channel_data"] & 0x3F
            insert = self.items_[insert_idx]
            id = item["id"]

            if id in (_MixerParamsID.SlotEnabled, _MixerParamsID.SlotMix):
                insert.slots[slot_idx][id] = item
            else:
                insert.own[id] = item


@enum.unique
class InsertID(EventEnum):
    Icon = (WORD + 31, I16Event)
    Output = (DWORD + 19, I32Event)
    Color = (DWORD + 21, ColorAdapter)  #: 4.0+
    Input = (DWORD + 26, I32Event)
    Name = TEXT + 12  #: 3.5.4+
    Routing = (DATA + 27, InsertRoutingEvent)
    Flags = (DATA + 28, InsertFlagsEvent)


@enum.unique
class MixerID(EventEnum):
    APDC = 29
    Params = (DATA + 17, MixerParamsEvent)


@enum.unique
class SlotID(EventEnum):
    Index = (WORD + 34, U16Event)


# ? Maybe, added in FL Studio v6.0.1
class InsertDock(enum.Enum):
    """![](https://bit.ly/3eLum9D)

    See Also:
        :attr:`Insert.dock`
    """  # noqa

    Left = enum.auto()
    Middle = enum.auto()
    Right = enum.auto()


class _InsertEQBandProp(NamedPropMixin):
    def __get__(self, ins: InsertEQBand, owner: Any = None) -> int | None:
        if owner is None:
            return NotImplemented
        return getattr(ins, self.prop)["msg"]

    def __set__(self, ins: InsertEQBand, value: int) -> None:
        getattr(ins, self.prop)["msg"] = value


@attrs.define
class InsertEQBand:
    gain: dict[str, Any]
    freq: dict[str, Any]
    reso: dict[str, Any]

    @property
    def size(self) -> int:
        return 12 * len(self._kw)  # ! TODO

    gain = _InsertEQBandProp()
    """
    | Min   | Max  | Default |
    |-------|------|---------|
    | -1800 | 1800 | 0       |
    """

    freq = _InsertEQBandProp()
    """Nonlinear. Default depends on band e.g. ``InsertEQ.low``.

    | Type | Value | Representation |
    |------|-------|----------------|
    | Min  | 0     | 10 Hz          |
    | Max  | 65536 | 16 kHz         |
    """

    reso = _InsertEQBandProp()
    """
    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65536 | 17500   |
    """


class _InsertEQPropArgs(NamedTuple):
    freq: int
    gain: int
    reso: int


class _InsertEQProp(NamedPropMixin):
    def __init__(self, ids: _InsertEQPropArgs) -> None:
        super().__init__()
        self._ids = ids

    def __get__(self, ins: InsertEQ, owner: Any = None) -> InsertEQBand:
        if owner is None:
            return NotImplemented

        items: dict[str, Any] = {}
        for id, param in ins.params.own.items():
            if id == self._ids.freq:
                items["freq"] = param
            elif id == self._ids.gain:
                items["gain"] = param
            elif id == self._ids.reso:
                items["reso"] = param
        return InsertEQBand(**items)


# Stored in MixerID.Params event.
@attrs.define
class InsertEQ:
    """Post-effect :class:`Insert` EQ with 3 adjustable bands.

    ![](https://bit.ly/3RUCQt6)

    See Also:
        :attr:`Insert.eq`
    """

    params: _InsertItems

    @property
    def size(self) -> int:
        return 12 * self.params  # ! TODO

    low = _InsertEQProp(
        _InsertEQPropArgs(_MixerParamsID.LowFreq, _MixerParamsID.LowGain, _MixerParamsID.LowQ)
    )
    """Low shelf band. Default frequency - 5777 (90 Hz)."""

    mid = _InsertEQProp(
        _InsertEQPropArgs(_MixerParamsID.MidFreq, _MixerParamsID.MidGain, _MixerParamsID.MidQ)
    )
    """Middle band. Default frequency - 33145 (1500 Hz)."""

    high = _InsertEQProp(
        _InsertEQPropArgs(_MixerParamsID.HighFreq, _MixerParamsID.HighGain, _MixerParamsID.HighQ)
    )
    """High shelf band. Default frequency - 55825 (8000 Hz)."""


class _MixerParamProp(Generic[_T]):
    def __init__(self, id: int) -> None:
        self._id = id

    def __get__(self, ins: Insert, owner: object = None) -> _T | None:
        if owner is None:
            return NotImplemented

        for id, item in ins.params.own.items():
            if id == self._id:
                return item["msg"]

    def __set__(self, ins: Insert, value: _T) -> None:
        for id, item in ins.params.own.items():
            if id == self._id:
                item["msg"] = value
                return
        raise KeyError(self._id)


@attrs.define(kw_only=True)
class Slot(EventProxy):
    """Represents an effect slot in an `Insert` / mixer channel.

    ![](https://bit.ly/3RUDtTu)
    """

    params: list[dict[str, Any]] = attrs.field(factory=list)

    def __repr__(self) -> str:
        return f"Slot (name={self.name}, iid={self.index}, plugin={self.plugin!r})"

    color = EventProp[RGBA](PluginID.Color)
    # TODO controllers = KWProp[List[RemoteController]]()
    iid = EventProp[int](SlotID.Index)
    """A 0-based internal index."""

    internal_name = EventProp[str](PluginID.InternalName)
    """'Fruity Wrapper' for VST/AU plugins or factory name for native plugins."""

    enabled = _MixerParamProp[bool](_MixerParamsID.SlotEnabled)
    """![](https://bit.ly/3eN4Ile)"""

    icon = EventProp[int](PluginID.Icon)
    index = EventProp[int](SlotID.Index)
    mix = _MixerParamProp[int](_MixerParamsID.SlotMix)
    """Dry/Wet mix. Defaults to maximum value.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -6400 | 100% left      |
    | Max     | 6400  | 100% right     |
    | Default | 0     | Centred        |
    """

    name = EventProp[str](PluginID.Name)
    plugin = PluginProp(
        VSTPlugin,
        FruityBalance,
        FruityBloodOverdrive,
        FruityCenter,
        FruityFastDist,
        FruityNotebook2,
        FruitySend,
        FruitySoftClipper,
        FruityStereoEnhancer,
        Soundgoodizer,
    )
    """The effect loaded into the slot."""


# TODO Need to make a `load()` method which will be able to parse preset files
# (by looking at Project.format) and use `MixerParameterEvent.items` to get
# remaining data. Normally, the `Mixer` passes this information to the Inserts
# (and Inserts to the `Slot`s directly).
@attrs.define(kw_only=True)
class Insert(EventProxy):
    """Represents a mixer track to which channel from the rack are routed to.

    ![](https://bit.ly/3LeGKuN)
    """

    iid: int
    """-1 for "current" insert, 0 for master and upto :attr:`Mixer.max_inserts`."""

    max_slots: int
    params: _InsertItems = attrs.field(factory=_InsertItems)

    def __iter__(self) -> Iterator[Slot]:
        """Iterator over the effect empty and used slots."""
        for idx, ed in enumerate(self.events.divide(SlotID.Index, *SlotID, *PluginID)):
            yield Slot(ed, params=self.params.slots[idx])

    def __len__(self) -> int:
        try:
            return self.events.count(SlotID.Index)
        except KeyError:
            return len(list(self))

    bypassed = FlagProp(_InsertFlags.EnableEffects, InsertID.Flags, inverted=True)
    """Whether all slots are bypassed."""

    channels_swapped = FlagProp(_InsertFlags.SwapLeftRight, InsertID.Flags)
    """Whether the left and right channels are swapped."""

    color = EventProp[RGBA](InsertID.Color)
    """Defaults to #636C71 (granite gray) in FL Studio.

    ![](https://bit.ly/3yVKXPc)

    Values below 20 for any color component (R, G, B) are ignored by FL.

    *New in FL Studio v4.0*.
    """

    @property
    def dock(self) -> InsertDock | None:
        """The position (left, middle or right) where insert is docked in mixer.

        :menuselection:`Insert --> Layout --> Dock to`

        ![](https://bit.ly/3eLum9D)
        """
        try:
            event = self.events.first(InsertID.Flags)
        except KeyError:
            return None

        flags = _InsertFlags(event.value["flags"])
        if _InsertFlags.DockMiddle in flags:
            return InsertDock.Middle
        if _InsertFlags.DockRight in flags:
            return InsertDock.Right
        return InsertDock.Left

    enabled = FlagProp(_InsertFlags.Enabled, InsertID.Flags)
    """Whether an insert in the mixer is enabled or disabled.

    ![](https://bit.ly/3BoRBOj)
    """

    @property
    def eq(self) -> InsertEQ:
        """3-band post EQ.

        ![](https://bit.ly/3RUCQt6)
        """
        return InsertEQ(self.params)

    icon = EventProp[int](InsertID.Icon)
    """Internal ID of the icon shown beside ``name``.

    ![](https://bit.ly/3Slr6jc)
    """

    input = EventProp[int](InsertID.Input)
    """![](https://bit.ly/3RO0ckC)"""

    is_solo = FlagProp(_InsertFlags.Solo, InsertID.Flags)
    """Whether the insert is solo'd."""

    locked = FlagProp(_InsertFlags.Locked, InsertID.Flags)
    """Whether an insert in the mixer is in locked state.

    ![](https://bit.ly/3SdPbc2)
    """

    name = EventProp[str](InsertID.Name)
    """*New in FL Studio v3.5.4*."""

    output = EventProp[int](InsertID.Output)
    """![](https://bit.ly/3LjWjBD)"""

    pan = _MixerParamProp[int](_MixerParamsID.Pan)
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -6400 | 100% left      |
    | Max     | 6400  | 100% right     |
    | Default | 0     | Centred        |

    ![](https://bit.ly/3DsZRj4)
    """

    polarity_reversed = FlagProp(_InsertFlags.PolarityReversed, InsertID.Flags)
    """Whether phase / polarity is reversed / inverted."""

    @property
    def routes(self) -> Iterator[int]:
        """Send volumes to routed inserts.

        *New in FL Studio v4.0*.
        """
        items = iter(cast(InsertRoutingEvent, self.events.first(InsertID.Routing)))
        for id, item in self.params.own.items():
            if id >= _MixerParamsID.RouteVolStart:
                try:
                    cond = next(items)
                except StopIteration:
                    continue
                else:
                    if cond:
                        yield item["msg"]

    separator_shown = FlagProp(_InsertFlags.SeparatorShown, InsertID.Flags)
    """Whether separator is shown before the insert.

    :menuselection:`Insert --> Group --> Separator`
    """

    stereo_separation = _MixerParamProp[int](_MixerParamsID.StereoSeparation)
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 64    | 100% merged    |
    | Max     | -64   | 100% separated |
    | Default | 0     | No effect      |
    """

    volume = _MixerParamProp[int](_MixerParamsID.Volume)
    """Post volume fader. Logarithmic.

    | Type    | Value | Representation      |
    |---------|-------|---------------------|
    | Min     | 0     | 0% / -INFdB / 0.00  |
    | Max     | 16000 | 125% / 5.6dB / 1.90 |
    | Default | 12800 | 100% / 0.0dB / 1.00 |
    """


# TODO FL Studio version in which slots were increased to 10
# TODO A move() method to change the placement of Inserts; it's difficult!
@attrs.define(kw_only=True)
class Mixer(EventProxy):
    """Represents the mixer which contains :class:`Insert` instances.

    ![](https://bit.ly/3eOsblF)
    """

    version: FLVersion

    _MAX_INSERTS = {
        (1, 6, 5): 5,
        (2, 0, 1): 8,
        (3, 0, 0): 18,
        (3, 3, 0): 20,
        (4, 0, 0): 64,
        (9, 0, 0): 105,
        (12, 9, 0): 127,
    }

    _MAX_SLOTS = {(1, 6, 5): 4, (3, 0, 0): 8}

    def __iter__(self) -> Iterator[Insert]:
        def select(e: AnyEvent) -> bool | None:
            if e.id == InsertID.Output:
                return False

            if e.id in (*InsertID, *PluginID, *SlotID):
                return True

        params: dict[int, _InsertItems] = {}
        if MixerID.Params in self.events.ids:
            params = cast(MixerParamsEvent, self.events.first(MixerID.Params)).items_

        for i, ed in enumerate(self.events.subtrees(select, self.max_inserts)):
            if i in params:
                yield Insert(ed, iid=i - 1, max_slots=self.max_slots, params=params[i])
            else:
                yield Insert(ed, iid=i - 1, max_slots=self.max_slots)

    def __len__(self) -> int:
        """Returns the number of inserts present in the project."""
        return self.events.count(InsertID.Flags)

    def __str__(self) -> str:
        return f"Mixer: {len(self)} inserts"

    apdc = EventProp[bool](MixerID.APDC)
    """Whether automatic plugin delay compensation is enabled for the inserts."""

    @property
    def max_inserts(self) -> int:
        """Estimated max number of inserts including sends, master and current.

        Maximum number of slots w.r.t. FL Studio:

        * 1.6.5: 4 inserts + master, 5 in total
        * 2.0.1: 8
        * 3.0.0: 16 inserts, 2 sends.
        * 3.3.0: +2 sends.
        * 4.0.0: 64
        * 9.0.0: 99 inserts, 105 in total.
        * 12.9.0: 125 + master + current.
        """
        version = attrs.astuple(self.version)
        for k, v in self._MAX_INSERTS.items():
            if version <= k:
                return v
        return 127

    @property
    def max_slots(self) -> int:
        """Estimated max number of effect slots per insert.

        Maximum number of slots w.r.t. FL Studio:

        * 1.6.5: 4
        * 3.3.0: 8
        """
        version = attrs.astuple(self.version)
        for k, v in self._MAX_SLOTS.items():
            if version <= k:
                return v
        return 10
