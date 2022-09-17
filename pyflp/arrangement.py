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
import dataclasses
import enum
import sys
from typing import Any, DefaultDict, List, Optional, cast

if sys.version_info >= (3, 8):
    from typing import Literal, SupportsIndex, TypedDict
else:
    from typing_extensions import Literal, SupportsIndex, TypedDict

if sys.version_info >= (3, 9):
    from collections.abc import Iterable, Iterator, Sequence
else:
    from typing import Iterable, Iterator, Sequence

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

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
    FLVersion,
    KWProp,
    ListEventBase,
    ModelBase,
    MultiEventModel,
    NestedProp,
    StructBase,
    StructEventBase,
    StructProp,
    U8Event,
    U16Event,
    U32Event,
)
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


class _PlaylistItemStruct(StructBase):
    PROPS = {
        "position": "I",  # 4
        "pattern_base": "H",  # 6
        "item_index": "H",  # 8
        "length": "I",  # 12
        "track_index": "H",  # 14
        "group": "H",  # 16
        "_u2": 2,  # 18
        "item_flags": "H",  # 20
        "_u4": 4,  # 24
        "start_offset": "i",  # 28
        "end_offset": "i",  # 32
    }


class _TrackStruct(StructBase):
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
        "_u18": 18,  # 66
    }


class PlaylistEvent(ListEventBase):
    STRUCT = _PlaylistItemStruct


class TrackEvent(StructEventBase):
    STRUCT = _TrackStruct


@enum.unique
class ArrangementsID(EventEnum):
    TimeSigNum = (17, U8Event)
    TimeSigBeat = (18, U8Event)
    Current = (WORD + 36, U16Event)
    WindowHeight = (DWORD + 5, U32Event)
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


@enum.unique
class TrackMotion(enum.IntEnum):
    Stay = 0
    OneShot = 1
    MarchWrap = 2
    MarchStay = 3
    MarchStop = 4
    Random = 5
    ExclusiveRandom = 6


@enum.unique
class TrackPress(enum.IntEnum):
    Retrigger = 0
    HoldStop = 1
    HoldMotion = 2
    Latch = 3


@enum.unique
class TrackSync(enum.IntEnum):
    Off = 0
    QuarterBeat = 1
    HalfBeat = 2
    Beat = 3
    TwoBeats = 4
    FourBeats = 5
    Auto = 6


class TimeMarkerType(enum.IntEnum):
    Marker = 0
    """Normal text marker."""

    Signature = 134217728
    """Used for time signature markers."""


class PlaylistItemBase(MultiEventModel):
    def __repr__(self):
        cls = type(self).__name__
        return f"{cls} @ {self.position!r} of {self.length} in group {self.group}"

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

        ![](https://bit.ly/3RDM1yn)
        """
        events = self._events.get(TimeMarkerID.Position)
        if events is not None:
            event = events[0]
            if event.value >= TimeMarkerType.Signature:
                return TimeMarkerType.Signature
            return TimeMarkerType.Marker


class _TrackKW(TypedDict):
    items: list[_PlaylistItemStruct]


class _TrackColorProp(StructProp[colour.Color]):
    def __get__(self, instance: ModelBase, owner: Any = None):
        value = cast(Optional[int], super().__get__(instance, owner))
        if value is not None:
            return ColorEvent.decode(value.to_bytes(4, "little"))

    def __set__(self, instance: ModelBase, value: colour.Color):
        color_u32 = int.from_bytes(ColorEvent.encode(value), "little")
        super().__set__(instance, color_u32)  # type: ignore


class Track(MultiEventModel, Iterable[PlaylistItemBase], SupportsIndex):
    """Represents a track in an arrangement on which playlist items are arranged.

    ![](https://bit.ly/3de6R8y)
    """

    def __init__(self, *events: AnyEvent, **kw: Unpack[_TrackKW]):
        super().__init__(*events, **kw)

    def __index__(self) -> int:
        """An integer in the range of 1 to :attr:`~Arrangements.max_tracks`."""
        return self.index or NotImplemented

    def __iter__(self):
        """An iterator over :attr:`items`."""
        return iter(self.items)

    def __repr__(self):
        flags: list[str] = []
        for attr in ("enabled", "grouped", "locked"):
            if getattr(self, attr, False):
                flags.append(attr)
        if "enabled" not in flags:
            flags.insert(0, "disabled")

        suffix = f"#{self.index} - {len(self.items)} items ({', '.join(flags)})"
        if self.name is None:
            return f"Unnamed track {suffix}"
        return f"Track {self.name!r} {suffix}"

    color = _TrackColorProp(id=TrackID.Data)
    content_locked = StructProp[bool](id=TrackID.Data)
    enabled = StructProp[bool](id=TrackID.Data)
    grouped = StructProp[bool](id=TrackID.Data)
    """Whether grouped with the track above (index - 1) or not."""

    height = StructProp[float](id=TrackID.Data)
    """Track height in FL's interface. Linear.

    | Type    | Value | Percentage |
    |---------|-------|------------|
    | Min     | 0.0   | 0%         |
    | Max     | 18.4  | 1840%      |
    | Default | 1.0   | 100%       |
    """

    icon = StructProp[int](id=TrackID.Data)
    index = StructProp[int](id=TrackID.Data)
    items = KWProp[List[PlaylistItemBase]]()
    """Playlist items present on the track."""

    locked = StructProp[bool](id=TrackID.Data)
    """Whether the tracked is in a locked state."""

    locked_height = StructProp[float](id=TrackID.Data)
    motion = StructProp[TrackMotion](id=TrackID.Data)
    name = EventProp[str](TrackID.Name)
    position_sync = StructProp[TrackSync](id=TrackID.Data)
    press = StructProp[TrackPress](id=TrackID.Data)
    tolerant = StructProp[bool](id=TrackID.Data)
    trigger_sync = StructProp[TrackSync](id=TrackID.Data)
    queued = StructProp[bool](id=TrackID.Data)


class _ArrangementKW(TypedDict):
    version: FLVersion


class Arrangement(MultiEventModel, SupportsIndex):
    """Contains them timemarkers and tracks in an arrangement.

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
        max_idx = 499 if dataclasses.astuple(self._kw["version"]) >= (12, 9, 1) else 198

        if ArrangementID.Playlist in self._events:
            pl_event = cast(PlaylistEvent, self._events[ArrangementID.Playlist][0])

        for events in self._collect_events(TrackID):
            items: list[_PlaylistItemStruct] = []
            if pl_event is not None:
                for item in pl_event.items:
                    idx = item["track_index"]
                    if max_idx - idx == count:
                        items.append(cast(_PlaylistItemStruct, item))
            yield Track(*events, items=items)
            count += 1


class TimeSignature(MultiEventModel):
    def __repr__(self) -> str:
        return f"Global time signature: {self.num}/{self.beat}"

    num = EventProp[int](ArrangementsID.TimeSigNum)
    beat = EventProp[int](ArrangementsID.TimeSigBeat)


class Arrangements(MultiEventModel, Sequence[Arrangement]):
    """Iterator over arrangements in the project and some related properties."""

    def __init__(self, *events: AnyEvent, **kw: Unpack[_ArrangementKW]):
        super().__init__(*events, **kw)

    def __getitem__(self, index: SupportsIndex) -> Arrangement:
        """Returns the arrangement at :attr:`Arrangement.index`.

        Raises:
            ModelNotFound: An arrangement with `index` could not be found.
        """
        for arrangement in self:
            if arrangement.__index__() == index:
                return arrangement
        raise ModelNotFound(index)

    # TODO Verify ArrangementsID.Current is the end
    # FL changed event ordering a lot, the latest being the most easiest to
    # parse; it contains ArrangementID.New event followed by TimeMarker events
    # followed by 500 TrackID events. TimeMarkers occured before new arrangement
    # event in initial versions of FL20, making them harder to group.
    # TODO This logic might not work on older versions of FL.
    def __iter__(self) -> Iterator[Arrangement]:
        """Provides an iterator over :class:`Arrangement`s found in the project.

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

    height = EventProp[int](ArrangementsID.WindowHeight)
    """Window height / track width used by the interface."""

    loop_pos = EventProp[int](ArrangementsID.LoopPos)
    """*New in FL Studio v1.3.8*."""

    @property
    def max_tracks(self) -> Literal[500, 199]:
        version = dataclasses.astuple(self._kw["version"])
        return 500 if version >= (12, 9, 1) else 199

    time_signature = NestedProp(
        TimeSignature, ArrangementsID.TimeSigNum, ArrangementsID.TimeSigBeat
    )
    """Project time signature (also used by playlist)."""
