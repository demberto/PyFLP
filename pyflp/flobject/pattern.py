import enum
from typing import Optional

from flobject.flobject import *
from utils import *

@enum.unique
class PatternEventID(enum.IntEnum):
    New = WORD + 1
    #Data = WORD + 4
    Color = DWORD + 22
    Name = TEXT + 1
    #_157 = DWORD + 29   # FL 12.5+
    #_158 = DWORD + 30   # default: -1
    #_164 = DWORD + 36   # default: 0

class Pattern(FLObject):
    _count = 0

    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    
    @property
    def color(self) -> Optional[int]:
        return getattr(self, '_color', None)
    
    @color.setter
    def color(self, value: int):
        self.setprop('color', value)

    @property
    def index(self) -> Optional[int]:
        return getattr(self, '_index', None)
    
    @index.setter
    def index(self, value: int):
        self.setprop('index', value)
    
    def _parse_word_event(self, event: WordEvent):
        if event.id == PatternEventID.New:
            self._events['index'] = event
            self._index = event.to_uint16()
    
    def _parse_dword_event(self, event: DWordEvent):
        if event.id == PatternEventID.Color:
            self._events['color'] = event
            self._color = event.to_uint32()

    def _parse_text_event(self, event: TextEvent):
        if event.id == PatternEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()
    
    def __init__(self):
        super().__init__()
        self.idx = Pattern._count
        Pattern._count += 1
        self._log.info(f"__init__(), index: {self.idx}, count: {self._count}")