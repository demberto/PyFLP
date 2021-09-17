from typing import Optional
from pyflp.flobject.plugin.plugin import EffectPlugin
from pyflp.event import DataEvent

__all__ = ['FBalance']

class FBalance(EffectPlugin):
    """Implements Fruity Balance."""

    #region Properties
    @property
    def pan(self) -> Optional[int]:
        """Linear. Min: -128, Max: 127, Default: 0 (0.50, Centred)"""
        return getattr(self, '_pan', None)

    @pan.setter
    def pan(self, value: int):
        assert value in range(-128, 127)
        self._data.seek(0)
        self._data.write_uint32(value)
        self._pan = value

    @property
    def volume(self) -> Optional[int]:
        """Logarithmic. Min: 0, Max: 320, Default: 256 (0.80, 0dB)"""
        return getattr(self, '_volume', None)

    @volume.setter
    def volume(self, value: int):
        assert value in range(0, 321)
        self._data.seek(4)
        self._data.write_uint32(value)
        self._volume = value
    #endregion

    def _parse_data_event(self, event: DataEvent) -> None:
        super()._parse_data_event(event)
        if len(event.data) != 8:
            self._log.error("Cannot parse plugin data, expected a size of 8 bytes; got {} bytes instead")
        self._pan = self._data.read_uint32()
        self._volume = self._data.read_uint32()

    def __init__(self):
        super().__init__()