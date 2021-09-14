import enum
import abc
import dataclasses
from typing import (
    Dict,
    List,
    Optional,
    ValuesView
)

from pyflp.bytesioex import BytesIOEx
from pyflp.event import DataEvent, Event
from pyflp.flobject.flobject import FLObject
from pyflp.utils import DATA

@enum.unique
class PlaylistEventID(enum.IntEnum):
    #_LoopBar = WORD + 20
    #_LoopEndBar = WORD + 26
    #_Item = DWORD + 1
    Events = DATA + 25

@dataclasses.dataclass
class _PlaylistItem(abc.ABC):
    """ABC for ChannelPlaylistItem and PatternPlaylistItem"""
    position: int
    length: int
    start_offset: int
    end_offset: int
    muted: bool

@dataclasses.dataclass
class ChannelPlaylistItem(_PlaylistItem):
    channel: int    # TODO

@dataclasses.dataclass
class PatternPlaylistItem(_PlaylistItem):
    pattern: int    # TODO

class Playlist(FLObject):
    _count = 0
    ppq = 0
    # TODO: max_count
    
    @property
    def _playlist_events(self) -> Dict[int, List[_PlaylistItem]]:
        return getattr(self, '_playlist_events_value', {})

    @_playlist_events.setter
    def _playlist_events(self, value: Dict[int, List[_PlaylistItem]]):
        self._playlist_events_value = value
    
    def _parse_data_event(self, event: DataEvent):
        if event.id == PlaylistEventID.Events:
            self._events['playlist_events'] = event
            
            # Validation
            if not len(event.data) % 32 == 0:
                self._log.error("Cannot parse these playlist events, contact me!")
            self._events_data = BytesIOEx(event.data)
            while True:
                position = self._events_data.read_uint32()      # 4
                if not position:
                    break
                pattern_base = self._events_data.read_uint16()  # 6
                pattern_id = self._events_data.read_uint16()    # 8
                length = self._events_data.read_int32()         # 12
                track = self._events_data.read_int32()          # 16
                if self.fl_version.major >= 20:
                    track = 499 - track
                else:
                    track = 198 - track
                self._events_data.seek(2, 1)                    # 18
                item_flags = self._events_data.read_uint16()    # 20
                self._events_data.seek(4, 1)                    # 24
                muted =  True if (item_flags & 0x2000) > 0 else False
                
                # Init the list if not
                track_events = self._playlist_events.get(track)
                if not track_events:
                    track_events = []
                
                if pattern_id <= pattern_base:
                    start_offset = int(self._events_data.read_float() * Playlist.ppq)    # 28
                    end_offset = int(self._events_data.read_float() * Playlist.ppq)      # 32
                    
                    # Cannot access tracks from here, ProjectParser
                    # or Arrangement must assign self._events to tracks
                    track_events.append(
                        ChannelPlaylistItem(
                            position,
                            length,
                            start_offset,
                            end_offset,
                            muted,
                            pattern_id
                        )
                    )
                else:
                    start_offset = self._events_data.read_int32()   # 28
                    end_offset = self._events_data.read_int32()     # 32
                    
                    track_events.append(
                        PatternPlaylistItem(
                            position,
                            length,
                            start_offset,
                            end_offset,
                            muted,
                            pattern_id - pattern_base - 1
                        )
                    )
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()
    
    def __init__(self):
        super().__init__()
        self._log.info("__init__()")
        self._playlist_events: Dict[int, List[_PlaylistItem]] = {}