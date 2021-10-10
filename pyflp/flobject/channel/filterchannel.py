from typing import Optional

from pyflp.flobject import FLObject
from pyflp.event import TextEvent

from .enums import FilterChannelEvent

__all__ = ["FilterChannel"]


class FilterChannel(FLObject):
    """Channel display filter. Default: 'Unsorted', 'Audio' and 'Automation'.

    Used by `pyflp.flobject.channel.channel.Channel.filter_channel`.
    """

    @property
    def name(self) -> Optional[str]:
        """Name of the filter channel."""
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self.setprop("name", value)

    def _parse_text_event(self, event: TextEvent):
        if event.id == FilterChannelEvent.Name:
            self.parse_str_prop(event, "name")

    def __init__(self):
        super().__init__()
