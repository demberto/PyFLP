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
    has its own `Track` and `TimeMarker` objects as well as a `Playlist`.
    """

    # * Properties
    @property
    def name(self) -> Optional[str]:
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self.setprop("name", value)

    @property
    def index(self) -> Optional[int]:
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        self.setprop("index", value)

    @property
    def tracks(self) -> List[Track]:
        return getattr(self, "_tracks", [])

    @tracks.setter
    def tracks(self, value: List[Track]):
        if super().fl_version.as_float() >= 12.9:
            if not len(value) == 500:
                raise Exception("Track count must be 500 when FL version >= 12.9")
        self._tracks = value

    @property
    def playlist(self) -> Optional[Playlist]:
        return getattr(self, "_playlist", None)

    @playlist.setter
    def playlist(self, value: Playlist):
        self._playlist = value

    @property
    def timemarkers(self) -> List[TimeMarker]:
        return getattr(self, "_timemarkers", [])

    @timemarkers.setter
    def timemarkers(self, value: List[TimeMarker]):
        for timemarker in value:
            if timemarker.denominator:
                assert timemarker.denominator % 4 == 0
            if timemarker.numerator:
                assert timemarker.numerator in range(1, 17)
        self._timemarkers = value

    # * Parsing logic
    def parse_event(self, event: Event) -> None:
        if event.id in PlaylistEvent.__members__.values():
            if not hasattr(self, "_playlist"):
                self._playlist = Playlist()
            self._playlist.parse_event(event)
        elif event.id in (
            TimeMarkerEvent.Numerator,
            TimeMarkerEvent.Denominator,
            TimeMarkerEvent.Name,
        ):
            if not hasattr(self, "_cur_timemarker"):
                raise Exception(
                    f"Got {event.id.name} event when timemarker "  # type: ignore
                    "did not get initialised."
                )
            else:
                self._cur_timemarker.parse_event(event)
        elif event.id == TrackEvent.Name:
            self._cur_track.parse_event(event)
        else:
            return super().parse_event(event)

    def _parse_word_event(self, event: WordEvent):
        if event.id == ArrangementEvent.Index:
            self.parse_uint16_prop(event, "index")

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == TimeMarkerEvent.Position:
            self._cur_timemarker = TimeMarker()
            self._timemarkers.append(self._cur_timemarker)
            self._cur_timemarker.parse_event(event)

    def _parse_text_event(self, event: TextEvent):
        if event.id == ArrangementEvent.Name:
            self.parse_str_prop(event, "name")

    def _parse_data_event(self, event: DataEvent):
        if event.id == TrackEvent.Data:
            self._cur_track = Track()
            self._cur_track.parse_event(event)
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
