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

"""Contains the types used by timemarkers, tracks and arrangements."""

from __future__ import annotations

import collections
import enum
import sys
from typing import Any, DefaultDict, Iterator, Optional, cast

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

import colour
import construct as c
import construct_typed as ct

from ._descriptors import EventProp, KWProp, NestedProp, StructProp
from ._events import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    ColorEvent,
    EventEnum,
    FourByteBool,
    ListEventBase,
    StdEnum,
    StructEventBase,
    U8Event,
    U16Event,
    U32Event,
)
from ._models import FLVersion, ItemModel, ModelCollection, MultiEventModel, getslice
from .channel import Channel
from .exceptions import ModelNotFound, NoModelsFound
from .pattern import Pattern

__all__ = [
    "Arrangements",
    "Arrangement",
    "TimeMarker",
    "TimeMarkerType",
    "Track",
    "TrackMotion",
    "TrackPress",
    "TrackSync",
    "ChannelPlaylistItem",
    "PatternPlaylistItem",
]


class PlaylistEvent(ListEventBase):
    STRUCT = c.Struct(
        "position" / c.Int32ul,  # 4
        "pattern_base" / c.Int16ul,  # 6
        "item_index" / c.Int16ul,  # 8
        "length" / c.Int32ul,  # 12
        "track_index" / c.Int16ul,  # 14
        "group" / c.Int16ul,  # 16
        "_u1" / c.Bytes(2),  # 18
        "item_flags" / c.Int16ul,  # 20
        "_u2" / c.Bytes(4),  # 24
        "start_offset" / c.Int32sl,  # 28
        "end_offset" / c.Int32sl,  # 32
    ).compile()


@enum.unique
class TrackMotion(ct.EnumBase):
    Stay = 0
    OneShot = 1
    MarchWrap = 2
    MarchStay = 3
    MarchStop = 4
    Random = 5
    ExclusiveRandom = 6


@enum.unique
class TrackPress(ct.EnumBase):
    Retrigger = 0
    HoldStop = 1
    HoldMotion = 2
    Latch = 3


@enum.unique
class TrackSync(ct.EnumBase):
    Off = 0
    QuarterBeat = 1
    HalfBeat = 2
    Beat = 3
    TwoBeats = 4
    FourBeats = 5
    Auto = 6


class TrackEvent(StructEventBase):
    STRUCT = c.Struct(
        "index" / c.Optional(c.Int32ul),  # 4
        "color" / c.Optional(c.Int32ul),  # 8
        "icon" / c.Optional(c.Int32ul),  # 12
        "enabled" / c.Optional(c.Flag),  # 13
        "height" / c.Optional(c.Float32l),  # 17
        "locked_height" / c.Optional(c.Float32l),  # 21
        "content_locked" / c.Optional(c.Flag),  # 22
        "motion" / c.Optional(StdEnum[TrackMotion](c.Int32ul)),  # 26
        "press" / c.Optional(StdEnum[TrackPress](c.Int32ul)),  # 30
        "trigger_sync" / c.Optional(StdEnum[TrackSync](c.Int32ul)),  # 34
        "queued" / c.Optional(FourByteBool),  # 38
        "tolerant" / c.Optional(FourByteBool),  # 42
        "position_sync" / c.Optional(StdEnum[TrackSync](c.Int32ul)),  # 46
        "grouped" / c.Optional(c.Flag),  # 47
        "locked" / c.Optional(c.Flag),  # 48
        "_u1" / c.Optional(c.GreedyBytes),  # * 66 as of 20.9.1
    ).compile()


@enum.unique
class ArrangementsID(EventEnum):
    TimeSigNum = (17, U8Event)
    TimeSigBeat = (18, U8Event)
    Current = (WORD + 36, U16Event)
    LoopPos = (DWORD + 24, U32Event)  #: 1.3.8+


@enum.unique
class ArrangementID(EventEnum):
    New = (WORD + 35, U16Event)
    # _PlaylistItem = DWORD + 1
    Name = TEXT + 49
    Playlist = (DATA + 25, PlaylistEvent)


@enum.unique
class TimeMarkerID(EventEnum):
    Numerator = (33, U8Event)
    Denominator = (34, U8Event)
    Position = (DWORD + 20, U32Event)
    Name = TEXT + 13


@enum.unique
class TrackID(EventEnum):
    Name = TEXT + 47
    Data = (DATA + 30, TrackEvent)


class TimeMarkerType(enum.IntEnum):
    Marker = 0
    """Normal text marker."""

    Signature = 134217728
    """Used for time signature markers."""


class PlaylistItemBase(ItemModel):
    def __repr__(self):
        return "{} @ {} of length {} in group {}".format(
            type(self).__name__, self.position, self.length, self.group
        )

    end_offset = StructProp[int]()
    group = StructProp[int]()
    """Returns 0 for no group, else a group number for clips in the same group."""

    length = StructProp[int]()
    muted = StructProp[bool]()
    """Whether muted / disabled in the playlist. *New in FL Studio v9.0.0*."""

    position = StructProp[int]()
    start_offset = StructProp[int]()


class ChannelPlaylistItem(PlaylistItemBase):
    """An audio clip or automation on the playlist of an arrangement.

    *New in FL Studio v2.0.1*.
    """

    def __repr__(self):
        if self.channel is None:
            return super().__repr__()
        return f"{super().__repr__()} for channel #{self.channel.iid}"

    channel = KWProp[Channel]()


class PatternPlaylistItem(PlaylistItemBase):
    """A pattern block or clip on the playlist of an arrangement.

    *New in FL Studio v7.0.0*.
    """

    def __repr__(self):
        if self.pattern is None:
            return super().__repr__()
        return f"{super().__repr__()} for pattern #{self.pattern!r}"

    pattern = KWProp[Pattern]()


class TimeMarker(MultiEventModel):
    """A marker in the timeline of an :class:`Arrangement`."""

    def __repr__(self):
        if self.type == TimeMarkerType.Marker:
            if self.name:
                return f"Marker {self.name!r} @ {self.position!r}"
            return f"Unnamed marker @ {self.position!r}"

        time_sig = f"{self.numerator}/{self.denominator}"
        if self.name:
            return f"Signature {self.name!r} ({time_sig}) @ {self.position!r}"
        return f"Unnamed {time_sig} signature @ {self.position!r}"

    denominator: EventProp[int] = EventProp[int](TimeMarkerID.Denominator)
    name = EventProp[str](TimeMarkerID.Name)
    numerator = EventProp[int](TimeMarkerID.Numerator)

    @property
    def position(self) -> int | None:
        events = self._events.get(TimeMarkerID.Position)
        if events is not None:
            event = events[0]
            if event.value < TimeMarkerType.Signature:
                return event.value
            return event.value - TimeMarkerType.Signature

    @property
    def type(self) -> TimeMarkerType | None:
        """The action with which a time marker is associated.

        [![](https://bit.ly/3RDM1yn)]()
        """
        events = self._events.get(TimeMarkerID.Position)
        if events is not None:
            event = events[0]
            if event.value >= TimeMarkerType.Signature:
                return TimeMarkerType.Signature
            return TimeMarkerType.Marker


class _TrackColorProp(StructProp[colour.Color]):
    def _get(self, ev_or_ins: Any):
        value = cast(Optional[int], super()._get(ev_or_ins))
        if value is not None:
            return ColorEvent.decode(bytearray(value.to_bytes(4, "little")))

    def _set(self, ev_or_ins: Any, value: colour.Color):
        color_u32 = int.from_bytes(ColorEvent.encode(value), "little")
        super()._set(ev_or_ins, color_u32)  # type: ignore


class _TrackKW(TypedDict):
    items: list[PlaylistItemBase]


class Track(MultiEventModel, ModelCollection[PlaylistItemBase]):
    """Represents a track in an arrangement on which playlist items are arranged.

    ![](https://bit.ly/3de6R8y)
    """

    def __init__(self, *events: AnyEvent, **kw: Unpack[_TrackKW]):
        super().__init__(*events, **kw)

    def __getitem__(self, index: int | slice | str):
        return self._kw["items"][index]

    def __index__(self) -> int:
        """An integer in the range of 1 to :attr:`Arrangements.max_tracks`."""
        return cast(TrackEvent, self._events[TrackID.Data][0])["index"]

    def __iter__(self) -> Iterator[PlaylistItemBase]:
        """An iterator over :attr:`items`."""
        yield from self._kw["items"]

    def __len__(self) -> int:
        return len(self._kw["items"])

    def __repr__(self):
        return f"Track (name={self.name}, index={self.__index__()}, {len(self)} items)"

    color = _TrackColorProp(TrackID.Data)
    """Defaults to #485156 (dark slate gray).

    Note:
        Unlike :attr:`Channel.color` and :attr:`Insert.color`, values
        below 20 for any color component are NOT ignored by FL Studio.
    """

    content_locked = StructProp[bool](TrackID.Data)
    """Defaults to :ref:`False`."""

    # TODO Add link to GIF from docs once Bitly quota is available again.
    enabled = StructProp[bool](TrackID.Data)
    grouped = StructProp[bool](TrackID.Data)
    """Whether grouped with the track above (index - 1) or not."""

    height = StructProp[float](TrackID.Data)
    """Track height in FL's interface. Linear.

    | Type    | Value | Percentage |
    |---------|-------|------------|
    | Min     | 0.0   | 0%         |
    | Max     | 18.4  | 1840%      |
    | Default | 1.0   | 100%       |
    """

    icon = StructProp[int](TrackID.Data)
    """Returns 0 if not set, else an internal icon ID."""

    # TODO Add link to GIF from docs once Bitly quota is available again.
    locked = StructProp[bool](TrackID.Data)
    """Whether the tracked is in a locked state."""

    locked_height = StructProp[float](TrackID.Data)
    motion = StructProp[TrackMotion](TrackID.Data)
    """Defaults to :attr:`TrackMotion.Stay`."""

    name = EventProp[str](TrackID.Name)
    """Returns `None` if not set."""

    position_sync = StructProp[TrackSync](TrackID.Data)
    """Defaults to :attr:`TrackSync.Off`."""

    press = StructProp[TrackPress](TrackID.Data)
    """Defaults to :attr:`TrackPress.Retrigger`."""

    tolerant = StructProp[bool](TrackID.Data)
    """Defaults to `True`."""

    trigger_sync = StructProp[TrackSync](TrackID.Data)
    """Defaults to :attr:`TrackSync.FourBeats`."""

    queued = StructProp[bool](TrackID.Data)
    """Defaults to :ref:`False`."""


class _ArrangementKW(TypedDict):
    version: FLVersion


class Arrangement(MultiEventModel):
    """Contains the timemarkers and tracks in an arrangement.

    ![](https://bit.ly/3B6is1z)

    *New in FL Studio v12.9.1*: Support for multiple arrangements.
    """

    def __init__(self, *events: AnyEvent, **kw: Unpack[_ArrangementKW]):
        super().__init__(*events, **kw)

    def __repr__(self):
        timemarkers = f"{len(tuple(self.timemarkers))} timemarkers"
        tracks = f"{len(tuple(self.tracks))} tracks"
        suffix = f"#{self.__index__()} {timemarkers} and {tracks}"
        if self.name:
            return f"Arrangement {self.name!r} {suffix}"
        return f"Unnamed arrangement {suffix}"

    def __index__(self) -> int:
        """A 1-based index."""
        return self._events[ArrangementID.New][0].value

    name = EventProp[str](ArrangementID.Name)
    """Name of the arrangement; defaults to **Arrangement**."""

    def _collect_events(self, enum_: type[EventEnum]):
        counter: list[int] = []
        ins_events: list[list[AnyEvent]] = []
        for id, events in self._events.items():
            if id in enum_:
                counter.append(len(events))
                ins_events.append(events)

        ins_dict: DefaultDict[int, list[AnyEvent]] = collections.defaultdict(list)
        for i in range(max(counter, default=0)):
            for sublist in ins_events:
                try:
                    event = sublist[i]
                except IndexError:
                    pass
                else:
                    ins_dict[i].append(event)
        return ins_dict.values()

    @property
    def timemarkers(self) -> Iterator[TimeMarker]:
        for events in self._collect_events(TimeMarkerID):
            yield TimeMarker(*events)

    @property
    def tracks(self) -> Iterator[Track]:
        count = 0
        pl_event = None
        max_idx = 499 if self._kw["version"] >= FLVersion(12, 9, 1) else 198

        if ArrangementID.Playlist in self._events:
            pl_event = cast(PlaylistEvent, self._events[ArrangementID.Playlist][0])

        for events in self._collect_events(TrackID):
            items: list[PlaylistItemBase] = []
            if pl_event is not None:
                for item in pl_event:
                    idx = item["track_index"]
                    if max_idx - idx == count:
                        items.append(PlaylistItemBase(item))
            yield Track(*events, items=items)
            count += 1


# TODO Find whether time is set to signature or division mode.
class TimeSignature(MultiEventModel):
    def __repr__(self) -> str:
        return f"Global time signature: {self.num}/{self.beat}"

    num = EventProp[int](ArrangementsID.TimeSigNum)
    """Beats per bar in time division & numerator in time signature mode.

    | Min | Max | Default |
    |-----|-----|---------|
    | 1   | 16  | 4       |
    """

    beat = EventProp[int](ArrangementsID.TimeSigBeat)
    """Steps per beat in time division & denominator in time signature mode.

    In time signature mode it can be 2, 4, 8 or 16 but in time division mode:

    | Min | Max | Default |
    |-----|-----|---------|
    | 1   | 16  | 4       |
    """


class Arrangements(MultiEventModel, ModelCollection[Arrangement]):
    """Iterator over arrangements in the project and some related properties."""

    def __init__(self, *events: AnyEvent, **kw: Unpack[_ArrangementKW]):
        super().__init__(*events, **kw)

    @getslice
    def __getitem__(self, i: int | str | slice):
        """Returns an arrangement based either on its index or name.

        Args:
            i (int | str | slice): The index of the arrangement in which they
                occur or :attr:`Arrangement.name` of the arrangement to lookup
                for or a slice of indexes.

        Raises:
            ModelNotFound: An :class:`Arrangement` with the specifed name or
                index isn't found.
        """
        for arr in self:
            if (isinstance(i, str) and i == arr.name) or arr.__index__() == i:
                return arr
        raise ModelNotFound(i)

    # TODO Verify ArrangementsID.Current is the end
    # FL changed event ordering a lot, the latest being the most easiest to
    # parse; it contains ArrangementID.New event followed by TimeMarker events
    # followed by 500 TrackID events. TimeMarkers occured before new arrangement
    # event in initial versions of FL20, making them harder to group.
    # TODO This logic might not work on older versions of FL.
    def __iter__(self) -> Iterator[Arrangement]:
        """Provides an iterator over :class:`Arrangement` found in the project.

        Raises:
            NoModelsFound: When no arrangements are found.
        """
        arrs_evs: list[list[AnyEvent]] = [[] for _ in range(len(self))]
        idx = 0
        for event in self._events_tuple:
            if event.id == ArrangementID.New:
                idx = event.value

            for enum_ in (ArrangementID, TimeMarkerID, TrackID):
                if event.id in enum_:
                    arrs_evs[idx].append(event)

        for arr_evs in arrs_evs:
            yield Arrangement(*arr_evs, version=self._kw["version"])

    def __len__(self):
        """The number of arrangements present in the project.

        Raises:
            NoModelsFound: When no arrangements are found.
        """
        if ArrangementID.New not in self._events:
            raise NoModelsFound
        return len(self._events[ArrangementID.New])

    def __repr__(self):
        return f"{len(self)} arrangements"

    @property
    def current(self) -> Arrangement | None:
        """Currently selected arrangement (via FL's interface).

        Raises:
            ModelNotFound: When the underlying event value points to an
                invalid arrangement index.
        """
        if ArrangementsID.Current in self._events:
            event = self._events[ArrangementsID.Current][0]
            index = event.value
            try:
                return list(self)[index]
            except IndexError as exc:
                raise ModelNotFound(index) from exc

    loop_pos = EventProp[int](ArrangementsID.LoopPos)
    """*New in FL Studio v1.3.8*."""

    @property
    def max_tracks(self) -> Literal[500, 199]:
        return 500 if self._kw["version"] >= FLVersion(12, 9, 1) else 199

    time_signature = NestedProp(
        TimeSignature, ArrangementsID.TimeSigNum, ArrangementsID.TimeSigBeat
    )
    """Project time signature (also used by playlist)."""
