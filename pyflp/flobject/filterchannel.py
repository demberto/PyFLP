import enum
from typing import Optional

from pyflp.flobject.flobject import *
from pyflp.utils import *

class FilterChannelEventID(enum.IntEnum):
    Name = TEXT + 39

class FilterChannel(FLObject):
    _count = 0

    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    
    def _parse_text_event(self, event: TextEvent):
        if event.id == FilterChannelEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()
    
    def __init__(self):
        FilterChannel._count += 1
        super().__init__()
        self._log.info(f"__init__(), count: {self._count}")