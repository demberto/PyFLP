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

"""Contains the types used by tracks and arrangements."""

from __future__ import annotations

import enum
from typing import Any, Iterator, Literal, Optional, cast

import construct as c
import construct_typed as ct
from typing_extensions import TypedDict, Unpack

from pyflp._adapters import FourByteBool, StdEnum
from pyflp._descriptors import EventProp, NestedProp, StructProp
from pyflp._events import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    EventEnum,
    EventTree,
    ListEventBase,
    StructEventBase,
    U8Event,
    U16Event,
    U16TupleEvent,
)
from pyflp._models import (
    EventModel,
    ItemModel,
    ModelCollection,
    ModelReprMixin,
    supports_slice,
)
from pyflp.channel import Channel, ChannelRack
from pyflp.exceptions import ModelNotFound, NoModelsFound, PropertyCannotBeSet
from pyflp.pattern import Pattern, Patterns
from pyflp.timemarker import TimeMarker, TimeMarkerID
from pyflp.types import RGBA, FLVersion

__all__ = [
    "Arrangements",
    "Arrangement",
    "Track",
    "TrackMotion",
    "TrackPress",
    "TrackSync",
    "ChannelPLItem",
    "PatternPLItem",
]


class PLSelectionEvent(StructEventBase):
    STRUCT = c.Struct("start" / c.Optional(c.Int32ul), "end" / c.Optional(c.Int32ul)).compile()


class PlaylistEvent(ListEventBase):
    STRUCT = c.GreedyRange(
        c.Struct(
            "position" / c.Int32ul,  # 4
            "pattern_base" / c.Int16ul * "Always 20480",  # 6
            "item_index" / c.Int16ul,  # 8
            "length" / c.Int32ul,  # 12
            "track_rvidx" / c.Int16ul * "Stored reversed i.e. Track 1 would be 499",  # 14
            "group" / c.Int16ul,  # 16
            "_u1" / c.Bytes(2) * "Always (120, 0)",  # 18
            "item_flags" / c.Int16ul * "Always (64, 0)",  # 20
            "_u2" / c.Bytes(4) * "Always (64, 100, 128, 128)",  # 24
            "start_offset" / c.Float32l,  # 28
            "end_offset" / c.Float32l,  # 32
            "_u3" / c.If(c.this._params["new"], c.Bytes(28)) * "New in FL 21",  # 60
        )
    )
    SIZES = [32, 60]

    def __init__(self, id: EventEnum, data: bytes) -> None:
        super().__init__(id, data, new=not len(data) % 60)


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


class HeightAdapter(ct.Adapter[float, float, str, str]):
    def _decode(self, obj: float, *_: Any) -> str:
        return str(int(obj * 100)) + "%"

    def _encode(self, obj: str, *_: Any) -> float:
        return int(obj[:-1]) / 100


class TrackEvent(StructEventBase):
    STRUCT = c.Struct(
        "iid" / c.Optional(c.Int32ul),  # 4
        "color" / c.Optional(c.Int32ul),  # 8
        "icon" / c.Optional(c.Int32ul),  # 12
        "enabled" / c.Optional(c.Flag),  # 13
        "height" / c.Optional(HeightAdapter(c.Float32l)),  # 17
        "locked_height" / c.Optional(c.Int32sl),  # 21
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
    _LoopPos = (DWORD + 24, U16TupleEvent)  #: 1.3.8+
    PLSelection = (DATA + 9, PLSelectionEvent)
    """.. versionadded:: v2.1.0"""


@enum.unique
class ArrangementID(EventEnum):
    New = (WORD + 35, U16Event)
    # _PlaylistItem = DWORD + 1
    Name = TEXT + 49
    Playlist = (DATA + 25, PlaylistEvent)


@enum.unique
class TrackID(EventEnum):
    Name = TEXT + 47
    Data = (DATA + 30, TrackEvent)


class PLItemBase(ItemModel[PlaylistEvent], ModelReprMixin):
    group = StructProp[int]()
    """Returns 0 for no group, else a group number for clips in the same group."""

    length = StructProp[int]()
    """PPQ-dependant quantity."""

    muted = StructProp[bool]()
    """Whether muted / disabled in the playlist. *New in FL Studio v9.0.0*."""

    @property
    def offsets(self) -> tuple[float, float]:
        """Returns a ``(start, end)`` offset tuple.

        An offset is the distance from the item's actual start or end.
        """
        return (self["start_offset"], self["end_offset"])

    @offsets.setter
    def offsets(self, value: tuple[float, float]) -> None:
        self["start_offset"], self["end_offset"] = value

    position = StructProp[int]()
    """PPQ-dependant quantity."""


class ChannelPLItem(PLItemBase, ModelReprMixin):
    """An audio clip or automation on the playlist of an arrangement.

    *New in FL Studio v2.0.1*.
    """

    @property
    def channel(self) -> Channel:
        return self._kw["channel"]

    @channel.setter
    def channel(self, channel: Channel) -> None:
        self._kw["channel"] = channel
        self["item_index"] = channel.iid


class PatternPLItem(PLItemBase, ModelReprMixin):
    """A pattern block or clip on the playlist of an arrangement.

    *New in FL Studio v7.0.0*.
    """

    @property
    def pattern(self) -> Pattern:
        return self._kw["pattern"]

    @pattern.setter
    def pattern(self, pattern: Pattern) -> None:
        self._kw["pattern"] = pattern
        self["item_index"] = pattern.iid + self["pattern_base"]


class _TrackColorProp(StructProp[RGBA]):
    def _get(self, ev_or_ins: Any) -> RGBA | None:
        value = cast(Optional[int], super()._get(ev_or_ins))
        if value is not None:
            return RGBA.from_bytes(value.to_bytes(4, "little"))

    def _set(self, ev_or_ins: Any, value: RGBA) -> None:
        super()._set(ev_or_ins, int.from_bytes(bytes(value), "little"))  # type: ignore


class _TrackKW(TypedDict):
    items: list[PLItemBase]


class Track(EventModel, ModelCollection[PLItemBase]):
    """Represents a track in an arrangement on which playlist items are arranged.

    ![](https://bit.ly/3de6R8y)
    """

    def __init__(self, events: EventTree, **kw: Unpack[_TrackKW]) -> None:
        super().__init__(events, **kw)

    def __getitem__(self, index: int | slice | str):
        if isinstance(index, str):
            return NotImplemented
        return self._kw["items"][index]

    def __iter__(self) -> Iterator[PLItemBase]:
        """An iterator over :attr:`items`."""
        yield from self._kw["items"]

    def __len__(self) -> int:
        return len(self._kw["items"])

    def __repr__(self) -> str:
        return f"Track(name={self.name}, iid={self.iid}, {len(self)} items)"

    color = _TrackColorProp(TrackID.Data)
    """Defaults to #485156 (dark slate gray).

    ![](https://bit.ly/3yVGGuW)

    Note:
        Unlike :attr:`Channel.color` and :attr:`Insert.color`, values below ``20`` for
        any color component (i.e red, green or blue) are NOT ignored by FL Studio.
    """

    content_locked = StructProp[bool](TrackID.Data)
    """:guilabel:`Lock to content`, defaults to ``False``."""

    enabled = StructProp[bool](TrackID.Data)
    """![](https://bit.ly/3eGd91O)"""

    grouped = StructProp[bool](TrackID.Data)
    """Whether grouped with the track above (index - 1) or not.

    ![](https://bit.ly/3yXO5tM)

    :guilabel:`&Group with above track`
    """

    height = StructProp[str](TrackID.Data)
    """Track height in FL's interface. Linear. :guilabel:`&Size`."""

    icon = StructProp[int](TrackID.Data)
    """Returns ``0`` if not set, else an internal icon ID.

    ![](https://bit.ly/3gln8Kc)

    :guilabel:`Change icon`
    """

    iid = StructProp[int](TrackID.Data)
    """An integer in the range of 1 to :attr:`Arrangements.max_tracks`."""

    locked = StructProp[bool](TrackID.Data)
    """Whether the tracked is in a locked state.

    ![](https://bit.ly/3VFG6eP)
    """

    motion = StructProp[TrackMotion](TrackID.Data)
    """:guilabel:`&Performance settings`, defaults to :attr:`TrackMotion.Stay`."""

    name = EventProp[str](TrackID.Name)
    """Returns a string or ``None`` if not set."""

    position_sync = StructProp[TrackSync](TrackID.Data)
    """:guilabel:`&Performance settings`, defaults to :attr:`TrackSync.Off`."""

    press = StructProp[TrackPress](TrackID.Data)
    """:guilabel:`&Performance settings`, defaults to :attr:`TrackPress.Retrigger`."""

    tolerant = StructProp[bool](TrackID.Data)
    """:guilabel:`&Performance settings`, defaults to ``True``."""

    trigger_sync = StructProp[TrackSync](TrackID.Data)
    """:guilabel:`&Performance settings`, defaults to :attr:`TrackSync.FourBeats`."""

    queued = StructProp[bool](TrackID.Data)
    """:guilabel:`&Performance settings`, defaults to ``False``."""


class _ArrangementKW(TypedDict):
    channels: ChannelRack
    patterns: Patterns
    version: FLVersion


class Arrangement(EventModel):
    """Contains the timemarkers and tracks in an arrangement.

    ![](https://bit.ly/3B6is1z)

    *New in FL Studio v12.9.1*: Support for multiple arrangements.
    """

    def __init__(self, events: EventTree, **kw: Unpack[_ArrangementKW]) -> None:
        super().__init__(events, **kw)

    def __repr__(self) -> str:
        return "Arrangement(iid={}, name={}, {} timemarkers, {} tracks)".format(
            self.iid,
            repr(self.name),
            len(tuple(self.timemarkers)),
            len(tuple(self.tracks)),
        )

    iid = EventProp[int](ArrangementID.New)
    """A 1-based internal index."""

    name = EventProp[str](ArrangementID.Name)
    """Name of the arrangement; defaults to **Arrangement**."""

    @property
    def timemarkers(self) -> Iterator[TimeMarker]:
        yield from (TimeMarker(ed) for ed in self.events.group(*TimeMarkerID))

    @property
    def tracks(self) -> Iterator[Track]:
        pl_evt = None
        max_idx = 499 if self._kw["version"] >= FLVersion(12, 9, 1) else 198
        channels = {channel.iid: channel for channel in self._kw["channels"]}
        patterns = {pattern.iid: pattern for pattern in self._kw["patterns"]}

        if ArrangementID.Playlist in self.events.ids:
            pl_evt = cast(PlaylistEvent, self.events.first(ArrangementID.Playlist))

        for track_idx, ed in enumerate(self.events.divide(TrackID.Data, *TrackID)):
            if pl_evt is None:
                yield Track(ed, items=[])
                continue

            items: list[PLItemBase] = []
            for i, item in enumerate(pl_evt):
                if max_idx - item["track_rvidx"] != track_idx:
                    continue

                if item["item_index"] <= item["pattern_base"]:
                    iid = item["item_index"]
                    items.append(ChannelPLItem(item, i, pl_evt, channel=channels[iid]))
                else:
                    num = item["item_index"] - item["pattern_base"]
                    items.append(PatternPLItem(item, i, pl_evt, pattern=patterns[num]))
            yield Track(ed, items=items)


# TODO Find whether time is set to signature or division mode.
class TimeSignature(EventModel, ModelReprMixin):
    """![](https://bit.ly/3EYiMmy)"""

    def __str__(self) -> str:
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


class Arrangements(EventModel, ModelCollection[Arrangement]):
    """Iterator over arrangements in the project and some related properties."""

    def __init__(self, events: EventTree, **kw: Unpack[_ArrangementKW]) -> None:
        super().__init__(events, **kw)

    @supports_slice  # type: ignore
    def __getitem__(self, i: int | str | slice) -> Arrangement:
        """Returns an arrangement based either on its index or name.

        Args:
            i: The index of the arrangement in which they occur or
               :attr:`Arrangement.name` of the arrangement to lookup for or a
               slice of indexes.

        Raises:
            ModelNotFound: An :class:`Arrangement` with the specifed name or
                index isn't found.
        """
        for idx, arr in enumerate(self):
            if (isinstance(i, str) and i == arr.name) or idx == i:
                return arr
        raise ModelNotFound(i)

    # TODO Verify ArrangementsID.Current is the end
    # FL changed event ordering a lot, the latest being the most easiest to
    # parse; it contains ArrangementID.New event followed by TimeMarker events
    # followed by 500 TrackID events. TimeMarkers occured before new arrangement
    # event in initial versions of FL20, making them harder to group.
    # TODO This logic might not work on older versions of FL.
    def __iter__(self) -> Iterator[Arrangement]:
        """Yields :class:`Arrangement` found in the project.

        Raises:
            NoModelsFound: When no arrangements are found.
        """
        arrnew_occured = False

        def select(e: AnyEvent) -> bool | None:
            nonlocal arrnew_occured
            if e.id == ArrangementID.New:
                if arrnew_occured:
                    return False
                arrnew_occured = True

            if e.id in (*ArrangementID, *TimeMarkerID, *TrackID):
                return True

            if e.id == ArrangementsID.Current:
                return False  # Yield out last arrangement

        yield from (Arrangement(ed, **self._kw) for ed in self.events.subtrees(select, len(self)))

    def __len__(self) -> int:
        """The number of arrangements present in the project.

        Raises:
            NoModelsFound: When no arrangements are found.
        """
        if ArrangementID.New not in self.events.ids:
            raise NoModelsFound
        return self.events.count(ArrangementID.New)

    def __repr__(self) -> str:
        return f"{len(self)} arrangements"

    @property
    def current(self) -> Arrangement | None:
        """Currently selected arrangement (via FL's interface).

        Raises:
            ModelNotFound: When the underlying event value points to an
                invalid arrangement index.
        """
        if ArrangementsID.Current in self.events.ids:
            event = self.events.first(ArrangementsID.Current)
            index: int = event.value
            try:
                return list(self)[index]
            except IndexError as exc:
                raise ModelNotFound(index) from exc

    @property
    def loop_pos(self) -> tuple[int, int] | None:
        """Playlist loop start and end points. PPQ dependant.

        .. versionchanged:: v2.1.0

           :attr:`ArrangementsID.PLSelection` is used by default
           while :attr:`ArrangementsID._LoopPos` is a fallback.

        *New in FL Studio v1.3.8*.
        """
        if ArrangementsID.PLSelection in self.events:
            event = cast(PLSelectionEvent, self.events.first(ArrangementsID.PLSelection))
            return event["start"], event["end"]

        if ArrangementsID._LoopPos in self.events:
            return self.events.first(ArrangementsID._LoopPos).value

    @loop_pos.setter
    def loop_pos(self, value: tuple[int, int]) -> None:
        if ArrangementsID.PLSelection in self.events:
            event = cast(PLSelectionEvent, self.events.first(ArrangementsID.PLSelection))
            event["start"], event["end"] = value
        elif ArrangementsID._LoopPos in self.events:
            self.events.first(ArrangementsID._LoopPos).value = value
        else:
            raise PropertyCannotBeSet(ArrangementsID.PLSelection, ArrangementsID._LoopPos)

    @property
    def max_tracks(self) -> Literal[500, 199]:
        return 500 if self._kw["version"] >= FLVersion(12, 9, 1) else 199

    time_signature = NestedProp(
        TimeSignature, ArrangementsID.TimeSigNum, ArrangementsID.TimeSigBeat
    )
    """Project time signature (also used by playlist).

    :menuselection:`Options --> &Project general settings --> Time settings`
    """
