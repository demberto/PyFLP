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

"""Contains the types used by patterns, MIDI notes and their automation data."""

from __future__ import annotations

import enum
from collections import defaultdict
from typing import DefaultDict, Iterator, cast

import construct as c

from pyflp._adapters import StdEnum
from pyflp._descriptors import EventProp, FlagProp, StructProp
from pyflp._events import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    BoolEvent,
    ColorEvent,
    EventEnum,
    EventTree,
    I32Event,
    IndexedEvent,
    ListEventBase,
    U16Event,
    U32Event,
)
from pyflp._models import EventModel, ItemModel, ModelCollection, ModelReprMixin, supports_slice
from pyflp.exceptions import ModelNotFound, NoModelsFound
from pyflp.timemarker import TimeMarker, TimeMarkerID
from pyflp.types import RGBA

__all__ = ["Note", "Controller", "Pattern", "Patterns"]


class ControllerEvent(ListEventBase):
    STRUCT = c.GreedyRange(
        c.Struct(
            "position" / c.Int32ul,  # 4, can be delta as well!
            "_u1" / c.Byte,  # 5
            "_u2" / c.Byte,  # 6
            "channel" / c.Int8ul,  # 7
            "_flags" / c.Int8ul,  # 8
            "value" / c.Float32l,  # 12
        )
    )


@enum.unique
class _NoteFlags(enum.IntFlag):
    Slide = 1 << 3


class NotesEvent(ListEventBase):
    STRUCT = c.GreedyRange(
        c.Struct(
            "position" / c.Int32ul,  # 4
            "flags" / StdEnum[_NoteFlags](c.Int16ul),  # 6
            "rack_channel" / c.Int16ul,  # 8
            "length" / c.Int32ul,  # 12
            "key" / c.Int16ul,  # 14
            "group" / c.Int16ul,  # 16
            "fine_pitch" / c.Int8ul,  # 17
            "_u1" / c.Byte,  # 18
            "release" / c.Int8ul,  # 19
            "midi_channel" / c.Int8ul,  # 20
            "pan" / c.Int8ul,  # 21
            "velocity" / c.Int8ul,  # 22
            "mod_x" / c.Int8ul,  # 23
            "mod_y" / c.Int8ul,  # 24
        )
    )


class PatternsID(EventEnum):
    PlayTruncatedNotes = (30, BoolEvent)
    CurrentlySelected = (WORD + 3, U16Event)


# ChannelIID, _161, _162, Looped, Length occur when pattern is looped.
# ChannelIID and _161 occur for every channel in order.
class PatternID(EventEnum):
    Looped = (26, BoolEvent)
    New = (WORD + 1, U16Event)  # Marks the beginning of a new pattern, twice.
    Color = (DWORD + 22, ColorEvent)
    Name = TEXT + 1
    # _157 = DWORD + 29  #: 12.5+
    # _158 = DWORD + 30  # default: -1
    ChannelIID = (DWORD + 32, U32Event)  # TODO (FL v20.1b1+)
    _161 = (DWORD + 33, I32Event)  # TODO -3 if channel is looped else 0 (FL v20.1b1+)
    _162 = (DWORD + 34, U32Event)  # TODO Appears when pattern is looped, default: 2
    Length = (DWORD + 36, U32Event)
    Controllers = (DATA + 15, ControllerEvent)
    Notes = (DATA + 16, NotesEvent)


class Note(ItemModel[NotesEvent]):
    _NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

    def __repr__(self) -> str:
        return "Note(key={}, position={}, length={}, channel={})".format(
            self.key, self.position, self.length, self.rack_channel
        )

    def __str__(self) -> str:
        return f"{self.key} note @ {self.position} of {self.length}"

    fine_pitch = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -1200 cents    |
    | Max     | 240   | +1200 cents    |
    | Default | 120   | No fine tuning |

    *New in FL Studio v3.3.0*.
    """

    group = StructProp[int]()
    """A number shared by notes in the same group or ``0`` if ungrouped.

    ![](https://bit.ly/3TgjFva)
    """

    @property
    def key(self) -> str:
        """Note name with octave, for e.g. 'C5' or 'A#3' ranging from C0 to B10.

        Only sharp key names (C#, D#, etc.) are used, flats aren't.

        Raises:
            ValueError: A value not in between 0-131 is tried to be set.
            ValueError: Invalid note name (not in the format {note-name}{octave}).
        """
        return self._NOTE_NAMES[self["key"] % 12] + str(self["key"] // 12)  # pyright: ignore

    @key.setter
    def key(self, value: int | str) -> None:
        if isinstance(value, int):
            if value not in range(132):
                raise ValueError("Expected a value between 0-131.")
            self["key"] = value
        else:
            for i, name in enumerate(self._NOTE_NAMES):
                if value.startswith(name):
                    octave = int(value.replace(name, "", 1))
                    self["key"] = octave * 12 + i
            raise ValueError(f"Invalid key name: {value}")

    length = StructProp[int]()
    """Returns 0 for notes punched in through step sequencer."""

    midi_channel = StructProp[int]()
    """Used for a variety of purposes.

    For note colors, min: 0, max: 15.
    +128 for MIDI dragged into the piano roll.

    *Changed in FL Studio v6.0.1*: Used for both, MIDI channels and colors.
    """

    mod_x = StructProp[int]()
    """Plugin configurable parameter.

    | Min | Max | Default |
    | --- | --- | ------- |
    | 0   | 255 | 128     |
    """

    mod_y = StructProp[int]()
    """Plugin configurable parameter.

    | Min | Max | Default |
    | --- | --- | ------- |
    | 0   | 255 | 128     |
    """

    pan = StructProp[int]()
    """
    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 100% left      |
    | Max     | 128   | 100% right     |
    | Default | 64    | Centered       |
    """

    position = StructProp[int]()
    rack_channel = StructProp[int]()
    """Containing channel's :attr:`Channel.IID`."""

    release = StructProp[int]()
    """
    | Min | Max | Default |
    | --- | --- | ------- |
    | 0   | 128 | 64      |
    """

    slide = FlagProp(_NoteFlags.Slide)
    """Whether note is a sliding note."""

    velocity = StructProp[int]()
    """
    | Min | Max | Default |
    | --- | --- | ------- |
    | 0   | 128 | 100     |
    """


class Controller(ItemModel[ControllerEvent], ModelReprMixin):
    def __str__(self) -> str:
        return f"Controller @ {self.position} of channel #{self.channel}"

    channel = StructProp[int]()
    """Corresponds to the containing channel's :attr:`Channel.iid`."""

    position = StructProp[int]()
    value = StructProp[float]()


class Pattern(EventModel):
    """Represents a pattern which can contain notes, controllers and time markers."""

    def __repr__(self) -> str:
        try:
            num_notes = len(self.events.first(PatternID.Notes))  # type: ignore
        except KeyError:
            num_notes = 0

        try:
            num_ctrls = len(self.events.first(PatternID.Controllers))  # type: ignore
        except KeyError:
            num_ctrls = 0

        return (
            f"Pattern(iid={self.iid}, name={self.name!r},"
            f"{num_notes} notes, {num_ctrls} controllers)"
        )

    color = EventProp[RGBA](PatternID.Color)
    """Returns a colour if one is set while saving the project file, else ``None``.

    ![](https://bit.ly/3eNeSSW)

    Defaults to #485156 in FL Studio.
    """

    @property
    def controllers(self) -> Iterator[Controller]:
        """Parameter automations associated with this pattern (if any)."""
        if PatternID.Controllers in self.events.ids:
            event = cast(ControllerEvent, self.events.first(PatternID.Controllers))
            yield from (Controller(item, i, event) for i, item in enumerate(event))

    @property
    def iid(self) -> int:
        """Internal index of the pattern starting from 1.

        Caution:
            Changing this will not solve any collisions thay may occur due to
            2 patterns that might end up having the same index.
        """
        return self.events.first(PatternID.New).value

    @iid.setter
    def iid(self, value: int) -> None:
        for event in self.events.get(PatternID.New):
            event.value = value

    length = EventProp[int](PatternID.Length)
    """The number of steps multiplied by the :attr:`pyflp.project.Project.ppq`.

    Returns `None` if pattern is in Auto mode (i.e. :attr:`looped` is `False`).
    """

    looped = EventProp[bool](PatternID.Looped, default=False)
    """Whether a pattern is in live loop mode.

    *New in FL Studio v2.5.0*.
    """

    name = EventProp[str](PatternID.Name)
    """User given name of the pattern; None if not set."""

    @property
    def notes(self) -> Iterator[Note]:
        """MIDI notes contained inside the pattern.

        Note:
            FL Studio uses its own custom format to represent notes internally.
            However by using the :class:`Note` properties with a MIDI parsing
            library for example, you can export them to MIDI.
        """
        if PatternID.Notes in self.events.ids:
            event = cast(NotesEvent, self.events.first(PatternID.Notes))
            yield from (Note(item, i, event) for i, item in enumerate(event))

    @property
    def timemarkers(self) -> Iterator[TimeMarker]:
        """Yields timemarkers inside this pattern."""
        yield from (TimeMarker(et) for et in self.events.group(*TimeMarkerID))


class Patterns(EventModel, ModelCollection[Pattern]):
    def __str__(self) -> str:
        iids = [pattern.iid for pattern in self]
        return f"{len(iids)} Patterns {iids!r}"

    @supports_slice  # type: ignore
    def __getitem__(self, i: int | str | slice) -> Pattern:
        """Returns the pattern with the specified index or :attr:`Pattern.name`.

        Args:
            i: A zero-based index, its name or a slice of indexes.

        Raises:
            ModelNotFound: A :class:`Pattern` with the specified name or index
                isn't found.
        """
        for idx, pattern in enumerate(self):
            if (isinstance(i, int) and idx == i) or i == pattern.name:
                return pattern
        raise ModelNotFound(i)

    # Doesn't use EventTree delegates since PatternID.New occurs twice.
    # Once for note and controller events and again for the rest of them.
    def __iter__(self) -> Iterator[Pattern]:
        """An iterator over the patterns found in the project."""
        cur_pat_id = 0
        tmp_dict: DefaultDict[int, list[IndexedEvent]] = defaultdict(list)

        for ie in self.events.lst:
            if ie.e.id == PatternID.New:
                cur_pat_id = ie.e.value

            if ie.e.id in (*PatternID, *TimeMarkerID):
                tmp_dict[cur_pat_id].append(ie)

        for events in tmp_dict.values():
            et = EventTree(self.events, events)
            self.events.children.append(et)
            yield Pattern(et)

    def __len__(self) -> int:
        """Returns the number of patterns found in the project.

        Raises:
            NoModelsFound: No patterns were found.
        """
        if PatternID.New not in self.events.ids:
            raise NoModelsFound
        return len({e.value for e in self.events.get(PatternID.New)})

    play_cut_notes = EventProp[bool](PatternsID.PlayTruncatedNotes)
    """Whether truncated notes of patterns placed in the playlist should be played.

    Located at :menuselection:`Options -> &Project general settings --> Advanced`
    under the name :guilabel:`Play truncated notes in clips`.

    *Changed in FL Studio v12.3 beta 3*: Enabled by default.
    """

    @property
    def current(self) -> Pattern | None:
        """Returns the currently selected pattern."""
        if PatternsID.CurrentlySelected in self.events.ids:
            index = self.events.first(PatternsID.CurrentlySelected).value
            for pattern in self:
                if pattern.iid == index:
                    return pattern
