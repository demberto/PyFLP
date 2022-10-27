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
import warnings
from collections import defaultdict
from itertools import chain
from typing import DefaultDict, Iterator, cast

import colour
import construct as c

from ._descriptors import EventProp, FlagProp, StdEnum, StructProp
from ._events import (
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
from ._models import EventModel, ItemModel
from .exceptions import ModelNotFound, NoModelsFound

__all__ = ["Note", "Controller", "Pattern", "Patterns"]


class ControllerEvent(ListEventBase):
    STRUCT = c.Struct(
        "position" / c.Int32ul,  # 4, can be delta as well!
        "_u1" / c.Byte,  # 5
        "_u2" / c.Byte,  # 6
        "channel" / c.Int8ul,  # 7
        "_flags" / c.Int8ul,  # 8
        "value" / c.Float32l,  # 12
    ).compile()


@enum.unique
class _NoteFlags(enum.IntFlag):
    Slide = 1 << 3


class NotesEvent(ListEventBase):
    STRUCT = c.Struct(
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
    ).compile()


class PatternsID(EventEnum):
    PlayTruncatedNotes = (30, BoolEvent)
    CurrentlySelected = (WORD + 3, U16Event)


# ChannelIID, _161, _162, Looped, Length occur when pattern is looped.
# ChannelIID and _161 occur for every channel in order.
# ! Looping a pattern puts timemarkers in it. The same TimeMarkerID events are
# ! used, which means I need to refactor it out from pyflp.arrangement.
# TODO Patterns share TimeMarker events with Arrangements
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
        return "Note (key={}, position={}, length={}, channel={})".format(
            self.key, self.position, self.length, self.rack_channel
        )

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
        return self._NOTE_NAMES[self["key"] % 12] + str(self["key"] // 12)

    @key.setter
    def key(self, value: int | str):
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


class Controller(ItemModel[ControllerEvent]):
    channel = StructProp[int]()
    """Corresponds to the containing channel's `Channel.IID`."""

    position = StructProp[int]()
    value = StructProp[float]()


# As of the latest version of FL, note and controller events are stored before
# all channel events (if they exist). The rest is stored later on as it occurs.
class Pattern(EventModel):
    """Represents a MIDI pattern.

    Iterate over it to get the notes contained inside it:

    >>> [note for pattern in project.patterns for note in pattern]
    [Note (key="C5", position=192, length=96, channel=2), ...]
    """

    def __index__(self):
        return self.index

    def __iter__(self) -> Iterator[Note]:
        """MIDI notes contained inside the pattern.

        Note:
            FL Studio uses its own custom format to represent notes internally.
            However by using the :class:`Note` properties with a MIDI parsing
            library for example, you can export them to MIDI.
        """
        if PatternID.Notes in self.events:
            event = cast(NotesEvent, self.events.first(PatternID.Notes))
            yield from (Note(item, i, event) for i, item in enumerate(event))

    def __repr__(self):
        num_notes = (
            len(cast(NotesEvent, self.events.first(PatternID.Notes)))
            if PatternID.Notes in self.events
            else 0
        )
        return f"Pattern (index={self.index}, name={self.name!r}, {num_notes} notes)"

    color = EventProp[colour.Color](PatternID.Color)
    """Returns a colour if one is set while saving the project file, else ``None``.

    ![](https://bit.ly/3eNeSSW)

    Defaults to #485156 in FL Studio.
    """

    @property
    def controllers(self) -> Iterator[Controller]:
        """Parameter automations associated with this pattern (if any)."""
        if PatternID.Controllers in self.events:
            event = cast(ControllerEvent, self.events.first(PatternID.Controllers))
            yield from (Controller(item, i, event) for i, item in enumerate(event))

    @property
    def index(self) -> int:
        """Internal index of the pattern starting from 1.

        Caution:
            Changing this will not solve any collisions thay may occur due to
            2 patterns that might end up having the same index.
        """
        return self.events.first(PatternID.New).value

    @index.setter
    def index(self, value: int):
        for event in self.events[PatternID.New]:
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


class Patterns(EventModel):
    def __repr__(self):
        indexes = [pattern.__index__() for pattern in self]
        return f"{len(indexes)} Patterns {indexes!r}"

    def __getitem__(self, i: int | str) -> Pattern:
        """Returns the pattern with the specified index or :attr:`Pattern.name`.

        Args:
            i: Internal index used by the pattern or its name.

        Raises:
            ModelNotFound: A :class:`Pattern` with the specified name or index
                isn't found.
        """
        if not i:
            warnings.warn("Patterns use a 1 based index; try 1 instead", stacklevel=0)
            return NotImplemented

        for pattern in self:
            if pattern.__index__() == i:
                return pattern
        raise ModelNotFound(i)

    def __iter__(self) -> Iterator[Pattern]:
        """An iterator over the patterns found in the project."""
        cur_pat_id = 0
        tmp_dict: DefaultDict[int, list[IndexedEvent]] = defaultdict(list)

        for ie in sorted(chain.from_iterable(self.events.dct.values())):
            if ie.e.id == PatternID.New:
                cur_pat_id = ie.e.value

            if ie.e.id in PatternID:
                tmp_dict[cur_pat_id].append(ie)

        for events in tmp_dict.values():
            yield Pattern(EventTree(self.events, events))

    def __len__(self):
        """Returns the number of patterns found in the project.

        Raises:
            NoModelsFound: No patterns were found.
        """
        if PatternID.New not in self.events:
            raise NoModelsFound
        return len({event.value for event in self.events[PatternID.New]})

    play_cut_notes = EventProp[bool](PatternsID.PlayTruncatedNotes)
    """Whether truncated notes of patterns placed in the playlist should be played.

    Located at :menuselection:`Options -> &Project general settings --> Advanced`
    under the name :guilabel:`Play truncated notes in clips`.

    *Changed in FL Studio v12.3 beta 3*: Enabled by default.
    """

    @property
    def current(self) -> Pattern | None:
        """Returns the currently selected pattern."""
        if PatternsID.CurrentlySelected in self.events:
            index = self.events.first(PatternsID.CurrentlySelected).value
            for pattern in self:
                if pattern.index == index:
                    return pattern
