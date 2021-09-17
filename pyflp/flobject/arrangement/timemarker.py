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
    _count = 0

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
            self._events['numerator'] = event
            self._numerator = event.to_uint8()
        elif event.id == TimeMarkerEventID.Denominator:
            self._events['denominator'] = event
            self._denominator = event.to_uint8()

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == TimeMarkerEventID.Position:
            self._events['position'] = event
            self._position = event.to_uint32()

    def _parse_text_event(self, event: TextEvent):
        if event.id == TimeMarkerEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()
    #endregion

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        return super().save()

    def __init__(self):
        self.idx = TimeMarker._count
        TimeMarker._count += 1
        super().__init__()