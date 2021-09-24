from typing import Optional, ValuesView

from pyflp.flobject.flobject import FLObject
from pyflp.flobject.arrangement.event_id import TimeMarkerEventID
from pyflp.event import (
    Event,
    ByteEvent,
    DWordEvent,
    TextEvent
)

__all__ = ['TimeMarker']

class TimeMarker(FLObject):

    #region Properties
    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str):
        self.setprop('name', value)

    @property
    def position(self) -> Optional[int]:
        return getattr(self, '_position', None)

    @position.setter
    def position(self, value: int):
        self.setprop('position', value)

    @property
    def numerator(self) -> Optional[int]:
        """Possible values: 1-16"""
        return getattr(self, '_numerator', None)

    @numerator.setter
    def numerator(self, value: int):
        assert value in range(1, 17)
        self.setprop('numerator', value)

    @property
    def denominator(self) -> Optional[int]:
        """Possible values: 2, 4, 8, 16"""
        return getattr(self, '_numerator', None)

    @denominator.setter
    def denominator(self, value: int):
        assert value in (2, 4, 8, 16)
        self.setprop('denominator', value)
    #endregion

    #region Parsing logic
    def _parse_byte_event(self, event: ByteEvent):
        if event.id == TimeMarkerEventID.Numerator:
            self.parse_uint8_prop(event, 'numerator')
        elif event.id == TimeMarkerEventID.Denominator:
            self.parse_uint8_prop(event, 'denominator')

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == TimeMarkerEventID.Position:
            self.parse_uint32_prop(event, 'position')

    def _parse_text_event(self, event: TextEvent):
        if event.id == TimeMarkerEventID.Name:
            self.parse_str_prop(event, 'name')
    #endregion

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()

    def __init__(self):
        super().__init__()