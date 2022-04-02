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
from typing import List, Optional

from pyflp._event import _DataEvent, _EventType, _TextEvent, _WordEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _StrProperty, _UIntProperty
from pyflp.arrangement.playlist import Playlist
from pyflp.arrangement.timemarker import TimeMarker
from pyflp.arrangement.track import Track
from pyflp.constants import TEXT, WORD

__all__ = ["Arrangement"]


class Arrangement(_FLObject):
    """Represents an arrangement. FL 12.89 introduced support for multiple
    arrangements. Every arrangement has its own `Track` and `TimeMarker`
    objects as well as a `Playlist`."""

    _props = ("name", "index", "")

    def __init__(self):
        super().__init__()
        self._timemarkers = []
        self._tracks = []

        Playlist._count = 0
        TimeMarker._count = 0
        Track._count = 0

    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `Arrangement`."""

        Name = TEXT + 49
        """See `Arrangement.name`. Default event stores **Arrangement**."""

        New = WORD + 35
        """Marks the beginning of an arrangement. See `Arrangement.index`."""

    # * Properties
    name: str = _StrProperty()

    index: int = _UIntProperty()

    @property
    def tracks(self) -> List[Track]:
        """A list of `Track` objects of an arrangement contains."""
        return getattr(self, "_tracks", [])

    @property
    def playlist(self) -> Optional[Playlist]:
        """The `Playlist` of an arrangement."""
        return getattr(self, "_playlist", None)

    @property
    def timemarkers(self) -> List[TimeMarker]:
        """A list of `TimeMarker` objects an arrangement contains."""
        return getattr(self, "_timemarkers", [])

    # * Parsing logic
    def parse_event(self, e: _EventType):
        if e.id in Playlist.EventID.__members__.values():
            if not hasattr(self, "_playlist"):
                self._playlist = Playlist()
            self._playlist.parse_event(e)
        elif e.id == Track.EventID.Name:
            self._cur_track.parse_event(e)
        # * TimeMarkers get parsed by Parser.
        else:
            super().parse_event(e)

    def _parse_word_event(self, e: _WordEvent):
        if e.id == Arrangement.EventID.New:
            self._parse_H(e, "index")

    def _parse_text_event(self, e: _TextEvent):
        if e.id == Arrangement.EventID.Name:
            self._parse_s(e, "name")

    def _parse_data_event(self, e: _DataEvent):
        if e.id == Track.EventID.Data:
            self._cur_track = Track()
            self._cur_track.parse_event(e)
            self._tracks.append(self._cur_track)

    def _save(self) -> List[_EventType]:
        events = list(super()._save())

        if self.playlist:
            events.extend(list(self.playlist._save()))

        if self.timemarkers:
            for timemarker in self.timemarkers:
                events.extend(list(timemarker._save()))

        if self.tracks:
            for track in self.tracks:
                events.extend(list(track._save()))

        return events
