from typing import Optional

from pyflp.flobject.flobject import FLObject
from pyflp.event import ByteEvent, DWordEvent, TextEvent

from .enums import TimeMarkerEvent

__all__ = ["TimeMarker"]


class TimeMarker(FLObject):
    @property
    def name(self) -> Optional[str]:
        """Name of the timemarker, e.g `4/4`, `3/4`"""
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self._setprop("name", value)

    @property
    def position(self) -> Optional[int]:
        """Position of the timemarker in the playlist,
        from the start and proportional to PPQ"""
        return getattr(self, "_position", None)

    @position.setter
    def position(self, value: int):
        self._setprop("position", value)

    @property
    def numerator(self) -> Optional[int]:
        """Possible values: 1-16"""
        return getattr(self, "_numerator", None)

    @numerator.setter
    def numerator(self, value: int):
        assert value in range(1, 17)
        self._setprop("numerator", value)

    @property
    def denominator(self) -> Optional[int]:
        """Possible values: 2, 4, 8, 16"""
        return getattr(self, "_numerator", None)

    @denominator.setter
    def denominator(self, value: int):
        assert value in (2, 4, 8, 16)
        self._setprop("denominator", value)

    # * Parsing logic
    def _parse_byte_event(self, e: ByteEvent):
        if e.id == TimeMarkerEvent.Numerator:
            self._parse_uint8_prop(e, "numerator")
        elif e.id == TimeMarkerEvent.Denominator:
            self._parse_uint8_prop(e, "denominator")

    def _parse_dword_event(self, e: DWordEvent):
        if e.id == TimeMarkerEvent.Position:
            self._parse_uint32_prop(e, "position")

    def _parse_text_event(self, e: TextEvent):
        if e.id == TimeMarkerEvent.Name:
            self._parse_str_prop(e, "name")

    def __init__(self):
        super().__init__()
