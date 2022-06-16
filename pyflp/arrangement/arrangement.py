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
from typing import TYPE_CHECKING, List, Optional

from pyflp._event import DataEventType, EventType, TextEventType, WordEventType
from pyflp._flobject import _FLObject
from pyflp._properties import _StrProperty, _UIntProperty
from pyflp.arrangement.playlist import Playlist
from pyflp.arrangement.timemarker import TimeMarker
from pyflp.arrangement.track import Track
from pyflp.constants import TEXT, WORD

if TYPE_CHECKING:
    from pyflp.project import Project

__all__ = ["Arrangement"]


class Arrangement(_FLObject):
    """Represents an arrangement. FL 12.89 introduced support for multiple
    arrangements. Every arrangement has its own `Track` and `TimeMarker`
    objects as well as a `Playlist`."""

    _props = ("name", "index", "")

    def __init__(self, project: "Project") -> None:
        super().__init__(project, None)
        self._playlist: Optional[Playlist] = None
        self._timemarkers: List[TimeMarker] = []
        self._tracks: List[Track] = []

    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `Arrangement`."""

        Name = TEXT + 49
        """See `Arrangement.name`. Default event stores **Arrangement**."""

        New = WORD + 35
        """Marks the beginning of an arrangement. See `Arrangement.index`."""

    # * Properties
    name: Optional[str] = _StrProperty()

    index: Optional[int] = _UIntProperty()

    @property
    def tracks(self) -> List[Track]:
        """A list of `Track` objects of an arrangement contains."""
        return self._tracks

    @property
    def playlist(self) -> Optional[Playlist]:
        """The `Playlist` of an arrangement."""
        return self._playlist

    @property
    def timemarkers(self) -> List[TimeMarker]:
        """A list of `TimeMarker` objects an arrangement contains."""
        return getattr(self, "_timemarkers", [])

    # * Parsing logic
    def parse_event(self, e: EventType) -> None:
        if e.id_ in Playlist.EventID.__members__.values():
            if not self._playlist:
                self._playlist = Playlist(self._project)
            self._playlist.parse_event(e)
        elif e.id_ == Track.EventID.Name:
            self._cur_track.parse_event(e)
        # * TimeMarkers get parsed by Parser.
        else:
            super().parse_event(e)

    def _parse_word_event(self, e: WordEventType) -> None:
        if e.id_ == Arrangement.EventID.New:
            self._parse_H(e, "index")

    def _parse_text_event(self, e: TextEventType) -> None:
        if e.id_ == Arrangement.EventID.Name:
            self._parse_s(e, "name")

    def _parse_data_event(self, e: DataEventType) -> None:
        if e.id_ == Track.EventID.Data:
            self._cur_track = Track()
            self._cur_track.parse_event(e)
            self._tracks.append(self._cur_track)

    def _save(self) -> List[EventType]:
        events = super()._save()

        if self.playlist:
            events.extend(self.playlist._save())

        if self.timemarkers:
            for timemarker in self.timemarkers:
                events.extend(timemarker._save())

        if self.tracks:
            for track in self.tracks:
                events.extend(track._save())

        return events
