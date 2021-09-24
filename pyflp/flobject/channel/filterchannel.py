from typing import Optional, ValuesView

from pyflp.flobject.flobject import FLObject
from pyflp.event import Event, TextEvent
from pyflp.flobject.channel.event_id import FilterChannelEventID

__all__ = ['FilterChannel']

class FilterChannel(FLObject):
    """Channel display filter. Default: 'Unsorted', 'Audio' and 'Automation'.
    
    Used by `pyflp.flobject.channel.channel.Channel.filter_channel`.
    """

    @property
    def name(self) -> Optional[str]:
        """Name of the filter channel."""
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    
    def _parse_text_event(self, event: TextEvent):
        if event.id == FilterChannelEventID.Name:
            self.parse_str_prop(event, 'name')
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()
    
    def __init__(self):
        super().__init__()