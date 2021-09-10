import enum
from typing import Optional

from bytesioex import BytesIOEx
from flobject.flobject import *
from utils import *

@enum.unique
class PlaylistEventID(enum.IntEnum):
    #_LoopBar = WORD + 20
    #_LoopEndBar = WORD + 26
    #_Item = DWORD + 1
    Events = DATA + 24
    WindowHeight = DWORD + 5
    WindowWidth = DWORD + 6

class Playlist(FLObject):
    _count = 0
    # TODO: max_count = 1 if not self._uses_arrangements
    
    @property
    def window_height(self) -> Optional[int]:
        return getattr(self, '_window_height', None)

    @window_height.setter
    def window_height(self, value: int):
        self.setprop('window_height', value)
    
    @property
    def window_width(self) -> Optional[int]:
        return getattr(self, '_window_width', None)

    @window_width.setter
    def window_width(self, value: int):
        self.setprop('window_width', value)
    
    def _parse_dword_event(self, event: DWordEvent):
        if event.id == PlaylistEventID.WindowHeight:
            self._events['window_height'] = event
            self._window_height = event.to_uint32()
        elif event.id == PlaylistEventID.WindowWidth:
            self._events['window_width'] = event
            self._window_width = event.to_uint32()
    
    def _parse_data_event(self, event: DataEvent):
        if event.id == PlaylistEventID.Events:
            self._events['events'] = event
            self._events_data = BytesIOEx(event.data)
            # TODO: Parsing
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()
    
    def __init__(self):
        super().__init__()
        self._log.info("__init__()")