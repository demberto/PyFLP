import abc
from pyflp.bytesioex import BytesIOEx
from pyflp.event import Event, DataEvent
from typing import Optional, ValuesView

from pyflp.flobject.flobject import FLObject

class Plugin(FLObject, abc.ABC):
    """Represents a native or VST2/VST3 effect or instrument"""
    def _parse_data_event(self, event: DataEvent) -> None:
        self._events['data'] = event
        self._data = BytesIOEx(event.data)
        return super()._parse_data_event(event)
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._data.seek(0)
        self._events['data'].dump(self._data.read())
        return super().save()

class EffectPlugin(Plugin):
    """Represents a native or VST2/VST3 effect. Used by InsertSlot.plugin"""
    pass

class GeneratorPlugin(Plugin):
    """Represents a native or VST2/VST3 instrument. Used by Channel.plugin"""
    pass