import enum
from typing import NoReturn, Optional

from pyflp.flobject import _FLObject
from pyflp.properties import _BoolProperty, _EnumProperty, _FloatProperty, _UIntProperty


class ChannelArp(_FLObject):
    """Miscellaneous settings -> Arp section.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#Arp)
    """

    class Direction(enum.IntEnum):
        """Arpeggio direction. Used by `ChannelArp.direction`."""

        Off = 0
        Up = 1
        Down = 2
        UpDownBounce = 3
        UpDownSticky = 4
        Random = 5

    # * Properties
    direction: Direction = _EnumProperty(Direction)
    """See `Direction`."""

    range: Optional[int] = _UIntProperty()
    """Range (in octaves)."""

    chord: Optional[int] = _UIntProperty()
    """Index of the selected arpeggio chord."""

    repeat: Optional[int] = _UIntProperty()
    """Number of times a note is repeated."""

    time: Optional[float] = _FloatProperty()
    """Delay between two successive notes played."""

    gate: Optional[float] = _FloatProperty()
    """Results in a more staccato sound."""

    slide: Optional[bool] = _BoolProperty()
    """Whether arpeggio will slide between notes."""

    def _save(self) -> NoReturn:
        """Implemented in `ChannelParametersEvent`."""
        raise NotImplementedError
