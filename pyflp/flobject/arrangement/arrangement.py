from typing import List, Optional

from pyflp.flobject import FLObject
from pyflp.event import Event, WordEvent, DWordEvent, TextEvent, DataEvent

from .timemarker import TimeMarker
from .playlist import Playlist
from .track import Track
from .enums import ArrangementEvent, TimeMarkerEvent, TrackEvent, PlaylistEvent

__all__ = ["Arrangement"]


class Arrangement(FLObject):
    """Represents an arrangement.
    FL 12.89 introduced support for multiple arrangements. Every arrangement
    has its own `Track` and `TimeMarker` objects as well as a `Playlist`."""

    # * Properties
    @property
    def name(self) -> Optional[str]:
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self._setprop("name", value)

    @property
    def index(self) -> Optional[int]:
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        self._setprop("index", value)

    @property
    def tracks(self) -> List[Track]:
        """A list of `Track` objects of an arrangement contains."""
        return getattr(self, "_tracks", [])

    @tracks.setter
    def tracks(self, value: List[Track]):
        if super().fl_version.as_float() >= 12.9:
            if not len(value) == 500:
                raise Exception("Track count must be 500 when FL version >= 12.9")
        self._tracks = value

    @property
    def playlist(self) -> Optional[Playlist]:
        """The `Playlist` of an arrangement."""
        return getattr(self, "_playlist", None)

    @playlist.setter
    def playlist(self, value: Playlist):
        self._playlist = value

    @property
    def timemarkers(self) -> List[TimeMarker]:
        """A list of `TimeMarker` objects an arrangement contains."""
        return getattr(self, "_timemarkers", [])

    @timemarkers.setter
    def timemarkers(self, value: List[TimeMarker]):
        self._timemarkers = value

    # * Parsing logic
    def parse_event(self, e: Event) -> None:
        if e.id in PlaylistEvent.__members__.values():
            if not hasattr(self, "_playlist"):
                self._playlist = Playlist()
            self._playlist.parse_event(e)
        elif e.id in (
            TimeMarkerEvent.Numerator,
            TimeMarkerEvent.Denominator,
            TimeMarkerEvent.Name,
        ):
            self._cur_timemarker.parse_event(e)
        elif e.id == TrackEvent.Name:
            self._cur_track.parse_event(e)
        else:
            return super().parse_event(e)

    def _parse_word_event(self, e: WordEvent):
        if e.id == ArrangementEvent.New:
            self._parse_uint16_prop(e, "index")

    def _parse_dword_event(self, e: DWordEvent):
        if e.id == TimeMarkerEvent.Position:
            self._cur_timemarker = TimeMarker()
            self._timemarkers.append(self._cur_timemarker)
            self._cur_timemarker.parse_event(e)

    def _parse_text_event(self, e: TextEvent):
        if e.id == ArrangementEvent.Name:
            self._parse_str_prop(e, "name")

    def _parse_data_event(self, e: DataEvent):
        if e.id == TrackEvent.Data:
            self._cur_track = Track()
            self._cur_track.parse_event(e)
            self._tracks.append(self._cur_track)

    def save(self) -> List[Event]:  # type: ignore
        events = list(super().save())

        if self.playlist:
            events.extend(list(self.playlist.save()))
        else:
            self._log.error(f"No playlist events found for arrangement {self._idx}")

        if self.timemarkers:
            for timemarker in self.timemarkers:
                events.extend(list(timemarker.save()))
        else:
            self._log.info(f"No timemarker events found for arrangement {self._idx}")

        if self.tracks:
            for track in self.tracks:
                events.extend(list(track.save()))
        else:
            self._log.error(f"No track events found for arrangement {self._idx}")

        return events

    def __init__(self):
        super().__init__()
        self._timemarkers = []
        self._tracks = []

        Playlist._count = 0
        TimeMarker._count = 0
        Track._count = 0
