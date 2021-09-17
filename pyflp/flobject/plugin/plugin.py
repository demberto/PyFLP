import abc
from pyflp.bytesioex import BytesIOEx
from pyflp.event import Event, DataEvent
from typing import Optional, ValuesView

from pyflp.flobject.flobject import FLObject

__all__ = ['Plugin', 'EffectPlugin', 'GeneratorPlugin']

class Plugin(FLObject, abc.ABC):
    """Represents a native or VST2/VST3 effect or instrument"""

    # Not actually used by subclasses but provided for syntax highlighting below
    def _parse_data_event(self, event: DataEvent) -> None:
        self._events['data'] = event
        self._data = BytesIOEx(event.data)
        return super()._parse_data_event(event)

    def save(self) -> Optional[ValuesView[Event]]:
        self._data.seek(0)
        self._events['data'].dump(self._data.read())
        return super().save()

class EffectPlugin(Plugin):
    """Represents a native or VST2/VST3 effect. Used by :class:`InsertSlot`.:param:`plugin`."""
    pass

class GeneratorPlugin(Plugin):
    """Represents a native or VST2/VST3 instrument. Used by :class:`Channel`.:param:`plugin`."""
    pass