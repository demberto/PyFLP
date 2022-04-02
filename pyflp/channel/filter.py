import enum

from pyflp._event import _TextEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _StrProperty
from pyflp.constants import TEXT

__all__ = ["Filter"]


class Filter(_FLObject):
    """Channel display filter. Default: 'Unsorted', 'Audio'
    and 'Automation'. Used by `Channel.filter_channel`."""

    @enum.unique
    class EventID(enum.IntEnum):
        """Event IDs used by `FilterChannel`."""

        Name = TEXT + 39
        """See `FilterChannel.name`."""

    name: str = _StrProperty()
    """Name of the filter channel."""

    def _parse_text_event(self, e: _TextEvent):
        if e.id == Filter.EventID.Name:
            self._parse_s(e, "name")
