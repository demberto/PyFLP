from typing import Optional
from pyflp.flobject.plugin.plugin import EffectPlugin
from pyflp.event import DataEvent

__all__ = ["Soundgoodizer"]


class Soundgoodizer(EffectPlugin):
    """Implements Soundgoodizer."""

    @property
    def mode(self) -> Optional[int]:
        """A = 0, B = 1, C = 2, D = 3"""
        return getattr(self, "_mode", None)

    @mode.setter
    def mode(self, value: int):
        assert value in range(0, 4)
        self._data.seek(4)
        self._data.write_uint32(value)
        self._mode = value

    @property
    def amount(self) -> Optional[int]:
        """Logarithmic. Min: 0, Max: 1000, Default: 600"""
        return getattr(self, "_amount", None)

    @amount.setter
    def amount(self, value: int):
        assert value in range(0, 1001)
        self._data.seek(8)
        self._data.write_uint32(value)
        self._amount = value

    def _parse_data_event(self, event: DataEvent) -> None:
        super()._parse_data_event(event)
        if len(event.data) != 12:
            self._log.error(
                "Cannot parse plugin data, expected a size of 12 bytes; got {} bytes instead"
            )
        self._data.seek(4)  # TODO: Always == 3?
        self._mode = self._data.read_uint32()
        self._amount = self._data.read_uint32()

    def __init__(self):
        super().__init__()
