import enum
from typing import List, Optional, ValuesView

from pyflp.flobject.flobject import FLObject
from pyflp.event import DataEvent, TextEvent, Event
from pyflp.flobject.playlist import _PlaylistItem
from pyflp.utils import TEXT, DATA
from pyflp.bytesioex import (
    BytesIOEx,
    UInt,
    Bool,
    Float
)

@enum.unique
class TrackEventID(enum.IntEnum):
    Name = TEXT + 47
    Data = DATA + 30

# No need for getattr in properties, they are automatically set to None if not found
class Track(FLObject):
    _count = 0
    max_count = 500 # TODO
    
    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    
    @property
    def index(self) -> Optional[int]:
        return self._index

    @index.setter
    def index(self, value: int):
        self._events_data.seek(0)
        self._events_data.write(UInt.pack(value))
        self._index = value
    
    @property
    def color(self) -> Optional[int]:
        return self._color

    @color.setter
    def color(self, value: int):
        self._events_data.seek(4)
        self._events_data.write(UInt.pack(value))
        self._color = value
    
    @property
    def icon(self) -> Optional[int]:
        return self._icon

    @icon.setter
    def icon(self, value: int):
        self._events_data.seek(8)
        self._events_data.write(UInt.pack(value))
        self._icon = value
    
    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._events_data.seek(12)
        self._events_data.write(Bool.pack(value))
        self._enabled = value
    
    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float):
        self._events_data.seek(13)
        self._events_data.write(Float.pack(value))
        self._height = value
    
    @property
    def locked_height(self) -> float:
        return self._locked_height

    @locked_height.setter
    def locked_height(self, value: float):
        self._events_data.seek(17)
        self._events_data.write(Float.pack(value))
        self._locked_height = value

    @property
    def locked_to_content(self) -> bool:
        return self._locked_to_content

    @locked_to_content.setter
    def locked_to_content(self, value: bool):
        self._events_data.seek(21)
        self._events_data.write(Bool.pack(value))
        self._locked_to_content = value
    
    @property
    def motion(self) -> Optional[int]:
        return self._motion

    @motion.setter
    def motion(self, value: int):
        self._events_data.seek(22)
        self._events_data.write(UInt.pack(value))
        self._motion = value
    
    @property
    def press(self) -> Optional[int]:
        return self._press

    @press.setter
    def press(self, value: int):
        self._events_data.seek(26)
        self._events_data.write(UInt.pack(value))
        self._press = value
    
    @property
    def trigger_sync(self) -> Optional[int]:
        return self._trigger_sync

    @trigger_sync.setter
    def trigger_sync(self, value: int):
        self._events_data.seek(30)
        self._events_data.write(UInt.pack(value))
        self._trigger_sync = value
    
    @property
    def queued(self) -> Optional[int]:
        return self._queued

    @queued.setter
    def queued(self, value: int):
        self._events_data.seek(34)
        self._events_data.write(UInt.pack(value))
        self._queued = value
    
    @property
    def tolerant(self) -> Optional[int]:
        return self._tolerant

    @tolerant.setter
    def tolerant(self, value: int):
        self._events_data.seek(38)
        self._events_data.write(UInt.pack(value))
        self._tolerant = value
    
    @property
    def position_sync(self) -> Optional[int]:
        return self._position_sync

    @position_sync.setter
    def position_sync(self, value: int):
        self._events_data.seek(42)
        self._events_data.write(UInt.pack(value))
        self._position_sync = value
    
    @property
    def grouped_with_above(self) -> Optional[bool]:
        return self._grouped_with_above

    @grouped_with_above.setter
    def grouped_with_above(self, value: bool):
        self._events_data.seek(46)
        self._events_data.write(Bool.pack(value))
        self._grouped_with_above = value
    
    @property
    def locked(self) -> Optional[bool]:
        return self._locked

    @locked.setter
    def locked(self, value: bool):
        self._events_data.seek(47)
        self._events_data.write(Bool.pack(value))
        self._locked = value
    
    @property
    def items(self) -> List[_PlaylistItem]:
        return getattr(self, '_items', [])
    
    @items.setter
    def items(self, value: List[_PlaylistItem]):
        self._items = value
    
    def _parse_text_event(self, event: TextEvent):
        if event.id == TrackEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()

    def _parse_data_event(self, event: DataEvent):
        if event.id == TrackEventID.Data:
            self._events['data'] = event
            self._events_data = BytesIOEx(event.data)
            self._index = self._events_data.read_uint32()              # 4
            self._color = self._events_data.read_int32()               # 8
            self._icon = self._events_data.read_int32()                # 12
            self._enabled = self._events_data.read_bool()              # 13
            self._height = self._events_data.read_float()              # 17
            self._locked_height = self._events_data.read_float()       # 21
            self._locked_to_content = self._events_data.read_bool()    # 22
            self._motion = self._events_data.read_uint32()             # 26
            self._press = self._events_data.read_uint32()              # 30
            self._trigger_sync = self._events_data.read_uint32()       # 34
            self._queued = self._events_data.read_uint32()             # 38
            self._tolerant = self._events_data.read_uint32()           # 42
            self._position_sync = self._events_data.read_uint32()      # 46
            self._grouped_with_above = self._events_data.read_bool()   # 47
            self._locked = self._events_data.read_bool()               # 48
            self._u2 = self._events_data.read(1)                       # 49
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        self._events_data.seek(0)
        self._events['data'].dump(self._events_data.read())
        return super().save()
    
    def __init__(self):
        super().__init__()
        Track._count += 1
        self._log.info(f"__init__(), count: {self._count}")  