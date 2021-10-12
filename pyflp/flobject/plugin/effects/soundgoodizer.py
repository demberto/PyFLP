from typing import Optional
from pyflp.flobject.plugin.plugin import EffectPlugin
from pyflp.event import DataEvent

from bytesioex import BytesIOEx  # type: ignore

__all__ = ["Soundgoodizer"]


class Soundgoodizer(EffectPlugin):
    """Implements Soundgoodizer."""

    @property
    def mode(self) -> Optional[int]:
        """A = 0, B = 1, C = 2, D = 3."""
        return getattr(self, "_mode", None)

    @mode.setter
    def mode(self, value: int):
        assert value in range(0, 4)
        self._data.seek(4)
        self._data.write_I(value)
        self._mode = value

    @property
    def amount(self) -> Optional[int]:
        """Logarithmic. Possible values: 0-1000, Default: 600."""
        return getattr(self, "_amount", None)

    @amount.setter
    def amount(self, value: int):
        assert value in range(0, 1001)
        self._data.seek(8)
        self._data.write_I(value)
        self._amount = value

    def _parse_data_event(self, event: DataEvent) -> None:
        self._data = BytesIOEx(event.data)
        if len(event.data) != 12:
            self._log.error(
                "Cannot parse plugin data, expected a size of 12 bytes; got {} bytes instead"
            )
        self._data.seek(4)  # TODO: Always == 3?
        self._mode = self._data.read_I()
        self._amount = self._data.read_I()

    def __init__(self):
        super().__init__()
