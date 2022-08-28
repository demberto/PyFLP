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
pyflp.pattern
=============

Contains the types used by MIDI patterns, notes and their automation data.
"""

import collections
import sys
from typing import DefaultDict, Iterator, List, Optional, Sized

if sys.version_info >= (3, 8):
    from typing import SupportsIndex
else:
    from typing_extensions import SupportsIndex

import colour

from ._base import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    BoolEvent,
    ColorEvent,
    EventEnum,
    EventProp,
    IterProp,
    ListEventBase,
    MultiEventModel,
    SingleEventModel,
    StructBase,
    StructProp,
    U16Event,
)


class ContollerStruct(StructBase):
    PROPS = {
        "position": "I",  # 4
        "_u1": 1,  # 5
        "_u2": 1,  # 6
        "channel": "B",  # 7
        "_flags": "B",  # 8
        "value": "f",  # 12
    }


class NoteStruct(StructBase):
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


class ControllerEvent(ListEventBase):
    STRUCT = ContollerStruct


class NotesEvent(ListEventBase):
    STRUCT = NoteStruct


class PatternsID(EventEnum):
    PlayTruncatedNotes = (30, BoolEvent)
    CurrentlySelected = (WORD + 3, U16Event)


# TODO Undiscovered events
class PatternID(EventEnum):
    New = (WORD + 1, U16Event)  # Marks the beginning of a new pattern, twice.
    Color = (DWORD + 22, ColorEvent)
    Name = TEXT + 1
    # _157 = DWORD + 29   # FL 12.5+
    # _158 = DWORD + 30   # default: -1
    # _164 = DWORD + 36   # default: 0
    Controllers = (DATA + 15, ControllerEvent)
    Notes = (DATA + 16, NotesEvent)


class Note(SingleEventModel):
    fine_pitch = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -128  | -100 cents     |
    | Max     | 127   | +100 cents     |
    | Default | 0     | No fine tuning |
    """

    key = StructProp[int]()  # TODO Separate property and chord/scale detection
    """0-131 for C0-B10. Can hold stamped chords and scales also."""

    length = StructProp[int]()
    midi_channel = StructProp[int]()
    """Use for a variety of purposes.

    For note colors, min: 0, max: 15.
    +128 for MIDI dragged into the piano roll.

    *Changed in FL Studio v6.0.1*: Used for both, MIDI channels and colors.
    """

    mod_x = StructProp[int]()
    mod_y = StructProp[int]()
    pan = StructProp[int]()
    """Min: -128, Max: 127."""

    position = StructProp[int]()
    rack_channel = StructProp[int]()
    """Corresponds to `Channel.iid` this note is for."""

    release = StructProp[int]()
    """Min: 0, Max: 128."""

    velocity = StructProp[int]()
    """Min: 0, Max: 128."""


class Controller(SingleEventModel):
    channel = StructProp[int]()
    position = StructProp[int]()
    value = StructProp[float]()


# As of the latest version of FL, note and controller events are stored before
# all channel events (if they exist). The rest is stored later on as it occurs.
class Pattern(MultiEventModel, SupportsIndex):
    def __repr__(self):
        if self.name is None:
            repr = "Unnamed pattern"
        else:
            repr = "Pattern " + self.name

        num_notes = len(tuple(self.notes))
        if num_notes > 0:
            return f"{repr} with {num_notes} notes"
        return f"Empty {repr}"

    def __index__(self):
        return self.index

    color = EventProp[colour.Color](PatternID.Color)
    controllers = IterProp(PatternID.Controllers, Controller)

    @property
    def index(self) -> int:
        """Internal index of the pattern starting from 1."""
        return self._events[PatternID.New][0].value

    @index.setter
    def index(self, value: int):
        for event in self._events[PatternID.New]:
            event.value = value

    name = EventProp[str](PatternID.Name)
    """User given name of the pattern; None if not set."""

    notes = IterProp(PatternID.Notes, Note)
    """MIDI notes contained inside the pattern."""


class Patterns(MultiEventModel, Sized):
    def __repr__(self):
        indexes = [pattern.__index__() for pattern in self.patterns]
        return f"{len(indexes)} Patterns {indexes!r}"

    def __len__(self):
        if PatternID.New not in self._events:
            return NotImplemented
        return len(set(event.value for event in self._events[PatternID.New]))

    @property
    def patterns(self) -> Iterator[Pattern]:
        cur_pat_id = 0
        events_dict: DefaultDict[int, List[AnyEvent]] = collections.defaultdict(list)

        for event in self._events_tuple:
            if event.id == PatternID.New:
                cur_pat_id = event.value
            events_dict[cur_pat_id].append(event)

        for events in events_dict.values():
            yield Pattern(*events)

    play_cut_notes = EventProp[bool](PatternsID.PlayTruncatedNotes)
    """Whether truncated notes of patterns placed in the playlist should be played.

    *Changed in FL Studio v12.3 beta 3*: Enabled by default.
    """

    @property
    def current(self) -> Optional[Pattern]:
        if PatternsID.CurrentlySelected in self._events:
            index = self._events[PatternsID.CurrentlySelected][0].value
            if index is not None:
                for pattern in self.patterns:
                    if pattern.__index__() == index:
                        return pattern
