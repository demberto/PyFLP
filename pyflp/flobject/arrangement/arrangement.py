from typing import List, Optional

from pyflp.flobject.arrangement.timemarker import TimeMarker, TimeMarkerEventID
from pyflp.flobject.arrangement.playlist import Playlist, PlaylistEventID
from pyflp.flobject.arrangement.track import Track, TrackEventID
from pyflp.flobject.flobject import FLObject
from pyflp.flobject.arrangement.event_id import ArrangementEventID
from pyflp.event import (
    Event,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)

__all__ = ['Arrangement']

class Arrangement(FLObject):
    _count = 0

    #region Properties
    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str):
        self.setprop('name', value)

    @property
    def index(self) -> Optional[int]:
        return getattr(self, '_index', None)

    @index.setter
    def index(self, value: int):
        self.setprop('index', value)

    @property
    def tracks(self) -> List[Track]:
        return getattr(self, '_tracks', [])

    @tracks.setter
    def tracks(self, value: List[Track]):
        assert len(value) == 500
        self._tracks = value

    @property
    def playlist(self) -> Optional[Playlist]:
        return getattr(self, '_playlist', None)

    @playlist.setter
    def playlist(self, value: Playlist):
        self._playlist = value

    @property
    def timemarkers(self) -> List[TimeMarker]:
        return getattr(self, '_timemarkers', [])

    @timemarkers.setter
    def timemarkers(self, value: List[TimeMarker]):
        for timemarker in value:
            assert timemarker.denominator % 4 == 0
            assert timemarker.numerator in range(1, 17)
        self._timemarkers = value
    #endregion

    #region Parsing logic
    def parse(self, event: Event) -> None:
        if event.id in PlaylistEventID.__members__.values():
            self._playlist.parse(event)
        elif event.id in (
            TimeMarkerEventID.Numerator,
            TimeMarkerEventID.Denominator,
            TimeMarkerEventID.Name
        ):
            self._cur_timemarker.parse(event)
        else:
            return super().parse(event)

    def _parse_word_event(self, event: WordEvent):
        if event.id == ArrangementEventID.Index:
            self._events['index'] = event
            self._index = event.to_uint16()

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == TimeMarkerEventID.Position:
            self._cur_timemarker = TimeMarker()
            self._timemarkers.append(self._cur_timemarker)
            self._cur_timemarker.parse(event)

    def _parse_text_event(self, event: TextEvent):
        if event.id == ArrangementEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()
        elif event.id == TrackEventID.Name:
            self._cur_track.parse(event)

    def _parse_data_event(self, event: DataEvent):
        if event.id == TrackEventID.Data:
            self._cur_track = Track()
            self._cur_track.parse(event)
            self._tracks.append(self._cur_track)
    #endregion

    def save(self) -> Optional[List[Event]]:
        self._log.info(f"save() called, count: {self._count}")
        events = list(super().save())

        if hasattr(self, '_playlist'):
            events.extend(self.playlist.save())
        else:
            self._log.error(f"No playlist events found for arrangement {self._index}")

        if self.timemarkers:
            for timemarker in self.timemarkers:
                events.extend(timemarker.save())
        else:
            self._log.info(f"No timemarker events found for arrangement {self._index}")

        if self.tracks:
            for track in self.tracks:
                events.extend(track.save())
        else:
            self._log.error(f"No track events found for arrangement {self._index}")

        return events

    def __init__(self):
        Arrangement._count += 1
        super().__init__()
        self._tracks = []
        self._playlist = Playlist()
        self._timemarkers = []