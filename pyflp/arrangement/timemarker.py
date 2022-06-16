# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

import enum
from typing import Any

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pyflp._event import ByteEventType, DWordEventType, TextEventType
from pyflp._flobject import _FLObject
from pyflp._properties import _EnumProperty, _IntProperty, _StrProperty, _UIntProperty
from pyflp._validators import _OneOfValidator
from pyflp.constants import DWORD, TEXT

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

    def _setprop(self, n: str, v: Any) -> None:
        if n == "kind":
            if v == TimeMarker.Kind.Marker and self.kind == TimeMarker.Kind.Signature:
                self.position -= TimeMarker.Kind.Signature
            elif v == TimeMarker.Kind.Signature and self.kind == TimeMarker.Kind.Marker:
                self.position += TimeMarker.Kind.Signature
        super()._setprop(n, v)

    kind: Kind = _EnumProperty(Kind)
    """Type of timemarker. See `Kind`."""

    name: str = _StrProperty()
    """Name; e.g. `4/4` could be time signature, `Chorus` could be marker."""

    position: int = _UIntProperty()
    """Position in the playlist, from the start and proportional to PPQ."""

    numerator: int = _IntProperty(min_=1, max_=16)
    """Min: 1, Max: 16."""

    denominator: Literal[2, 4, 8, 16] = _UIntProperty(_OneOfValidator((2, 4, 8, 16)))

    # * Parsing logic
    def _parse_byte_event(self, e: ByteEventType) -> None:
        if e.id_ == TimeMarker.EventID.Numerator:
            self._parse_B(e, "numerator")
        elif e.id_ == TimeMarker.EventID.Denominator:
            self._parse_B(e, "denominator")

    def _parse_dword_event(self, e: DWordEventType) -> None:
        if e.id_ == TimeMarker.EventID.Position:
            pos = e.to_uint32()
            if pos >= TimeMarker.Kind.Signature:
                self._kind = TimeMarker.Kind.Signature
                pos -= TimeMarker.Kind.Signature
            else:
                self._kind = TimeMarker.Kind.Marker
            self._parseprop(e, "position", pos)

    def _parse_text_event(self, e: TextEventType) -> None:
        if e.id_ == TimeMarker.EventID.Name:
            self._parse_s(e, "name")
