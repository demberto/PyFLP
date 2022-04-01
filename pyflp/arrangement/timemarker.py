import enum

from pyflp.constants import DWORD, TEXT
from pyflp.event import ByteEvent, TextEvent, _DWordEventType
from pyflp.flobject import _FLObject
from pyflp.properties import _EnumProperty, _StrProperty, _UIntProperty
from pyflp.validators import _IntValidator, _OneOfValidator

__all__ = ["TimeMarker"]


class TimeMarker(_FLObject):
    """Represents a time marker or a time signature stamp."""

    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `TimeMarker`"""

        Position = DWORD + 20
        """See `TimeMarker.position`."""

        Numerator = 33
        """See `TimeMarker.numerator`."""

        Denominator = 34
        """See `TimeMarker.denominator`."""

        Name = TEXT + 13
        """See `TimeMarker.name`."""

    @enum.unique
    class Kind(enum.IntEnum):
        """Used by `TimeMarker.kind`."""

        Marker = 0
        """Normal text marker."""

        Signature = 134217728
        """Specifies a change in the time signature."""

    def _setprop(self, n, v):
        if n == "kind":
            if v == TimeMarker.Kind.Marker and self.kind == TimeMarker.Kind.Signature:
                self.position -= TimeMarker.Kind.Signature
            elif v == TimeMarker.Kind.Signature and self.kind == TimeMarker.Kind.Marker:
                self.position += TimeMarker.Kind.Signature
        super()._setprop(n, v)

    kind: Kind = _EnumProperty(Kind)
    """Type of timemarker. See `Kind`."""

    name: str = _StrProperty()
    """Name; e.g. `4/4`, `Chorus`, etc."""

    position: int = _UIntProperty()
    """Position in the playlist, from the start and proportional to PPQ."""

    numerator: int = _UIntProperty(_IntValidator(1, 16))
    """Min: 1, Max: 16."""

    denominator: int = _UIntProperty(_OneOfValidator((2, 4, 8, 16)))
    """Possible values: 2, 4, 8, 16."""

    # * Parsing logic
    def _parse_byte_event(self, e: ByteEvent):
        if e.id == TimeMarker.EventID.Numerator:
            self._parse_B(e, "numerator")
        elif e.id == TimeMarker.EventID.Denominator:
            self._parse_B(e, "denominator")

    def _parse_dword_event(self, e: _DWordEventType):
        if e.id == TimeMarker.EventID.Position:
            pos = e.to_uint32()
            if pos >= TimeMarker.Kind.Signature:
                self._kind = TimeMarker.Kind.Signature
                pos -= TimeMarker.Kind.Signature
            else:
                self._kind = TimeMarker.Kind.Marker
            self._parseprop(e, "position", pos)

    def _parse_text_event(self, e: TextEvent):
        if e.id == TimeMarker.EventID.Name:
            self._parse_s(e, "name")

    def __init__(self):
        super().__init__()
