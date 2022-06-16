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
import io
from typing import TYPE_CHECKING, List, Optional

import colour

from pyflp._event import (
    DataEventType,
    DWordEventType,
    EventType,
    TextEventType,
    WordEventType,
)
from pyflp._flobject import _FLObject
from pyflp._properties import _ColorProperty, _StrProperty
from pyflp.constants import DATA, DWORD, TEXT, WORD
from pyflp.pattern.controller import PatternController, PatternControllersEvent
from pyflp.pattern.note import PatternNote, PatternNotesEvent

__all__ = ["Pattern"]


class Pattern(_FLObject):
    NOTE_SIZE = 24

    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `Pattern`."""

        New = WORD + 1
        """Marks the beginning of a new pattern, **twice**."""

        # _Data = WORD + 4
        Color = DWORD + 22
        """See `Pattern.color`. Default event is not stored."""

        Name = TEXT + 1
        """See `Pattern.color`. Default event deos not exist."""

        # _157 = DWORD + 29   # FL 12.5+
        # _158 = DWORD + 30   # default: -1
        # _164 = DWORD + 36   # default: 0
        Controllers = DATA + 15
        """See `Pattern.controllers`."""

        Notes = DATA + 16
        """See `Pattern.notes`."""

    # * Properties
    name: Optional[str] = _StrProperty()

    color: Optional[colour.Color] = _ColorProperty()

    @property
    def index(self) -> int:
        """Pattern index. Begins from 1.

        Occurs twice, once near the top with note data and once with rest of
        the metadata. The first time a `PatternEvent.New` occurs, it is
        parsed by `parse_index1()`. Empty patterns are not stored at the top
        since they don't have any note data. They come later on.

        See `Parser.__parse_pattern()` for implemntation."""
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        self._events["index"].dump(value)
        self._index = value
        self._events["index (metadata)"].dump(value)

    @property
    def notes(self) -> List[PatternNote]:
        """Contains the list of MIDI events (notes) of all channels."""
        return getattr(self, "_notes", [])

    @property
    def controllers(self) -> List[PatternController]:
        """Pattern control events, size is equal to pattern length."""
        return getattr(self, "_controllers", [])

    # * Parsing logic
    def parse_index1(self, e: WordEventType):
        """Thanks to FL for storing data of a single pattern at 2 different places."""
        self._events["index (metadata)"] = e

    def _parse_word_event(self, e: WordEventType):
        if e.id_ == Pattern.EventID.New:
            self._parse_H(e, "index")

    def _parse_dword_event(self, e: DWordEventType):
        if e.id_ == Pattern.EventID.Color:
            self._parse_color(e, "color")

    def _parse_text_event(self, e: TextEventType):
        if e.id_ == Pattern.EventID.Name:
            self._parse_s(e, "name")

    def _parse_data_event(self, e: DataEventType):
        if e.id_ == Pattern.EventID.Notes:
            if TYPE_CHECKING:
                if not isinstance(e, PatternNotesEvent):
                    raise TypeError
            self._events["notes"] = e
            self._notes = e.notes

        elif e.id_ == Pattern.EventID.Controllers:
            if TYPE_CHECKING:
                if not isinstance(e, PatternControllersEvent):
                    raise TypeError
            self._events["controllers"] = e
            self._controllers = e.controllers

    def _save(self) -> List[EventType]:
        # Note events
        notes = self.notes
        notes_ev = self._events.get("notes")
        if notes and notes_ev:
            notes_data = io.BytesIO()
            for note in notes:
                notes_data.write(note._save())
            notes_data.seek(0)
            notes_ev.dump(notes_data.read())

        # Controller events
        ctrls = self.controllers
        ctrls_ev = self._events.get("controllers")
        if ctrls and ctrls_ev:
            ctrls_data = io.BytesIO()
            for ctrl in ctrls:
                ctrls_data.write(ctrl._save())
            ctrls_data.seek(0)
            ctrls_ev.dump(ctrls_data.read())

        return super()._save()

    # * Utility methods
    def is_empty(self) -> bool:
        """Whether pattern has note data."""
        return "notes" in self._events

    def __init__(self):
        super().__init__()
        self._notes: List[PatternNote] = []
