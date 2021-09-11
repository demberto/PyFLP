import enum
from typing import List, Optional, ValuesView

from pyflp.flobject.timemarker import TimeMarker, TimeMarkerEventID
from pyflp.flobject.playlist import Playlist, PlaylistEventID
from pyflp.flobject.track import Track, TrackEventID
from pyflp.flobject.flobject import FLObject
from pyflp.event import (
    Event,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)
from pyflp.utils import TEXT, WORD

class ArrangementEventID(enum.IntEnum):
    Name = TEXT + 49
    Index = WORD + 35

class Arrangement(FLObject):
    _count = 0
    
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
            self._cur_track_idx += 1

        if self._cur_track_idx == 499:
            self._log.debug("Assigning playlist events to tracks")
            # The playlist can be empty
            if self.playlist._playlist_events:
                for idx, track in enumerate(self.tracks):
                    track.items = self.playlist._playlist_events[idx]
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()
    
    def __init__(self):
        super().__init__()
        Arrangement._count += 1
        self._log.info(f"__init__(), count: {self._count}")
        self._tracks = []
        self._cur_track_idx = 0
        self._playlist = Playlist()
        self._timemarkers = list()