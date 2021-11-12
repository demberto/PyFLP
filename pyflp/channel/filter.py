import enum

from pyflp.constants import TEXT
from pyflp.event import TextEvent
from pyflp.flobject import _FLObject
from pyflp.properties import _StrProperty


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

    def _parse_text_event(self, e: TextEvent):
        if e.id == Filter.EventID.Name:
            self._parse_s(e, "name")
