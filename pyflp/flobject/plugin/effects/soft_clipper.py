from typing import Optional
from pyflp.flobject.plugin.plugin import EffectPlugin
from pyflp.event import DataEvent

__all__ = ["FSoftClipper"]


class FSoftClipper(EffectPlugin):
    Default = bytearray((100, 0, 0, 0, 128, 0, 0, 0))

    # * Properties
    @property
    def threshold(self) -> Optional[int]:
        """Logarithmic. Min: 1, Max: 127, Default: 100 (0.60, -4.4dB)"""
        return getattr(self, "_threshold", None)

    @threshold.setter
    def threshold(self, value: int):
        assert value in range(1, 128)
        self._data.seek(0)
        self._data.write_I(value)
        self._threshold = value

    @property
    def post_gain(self) -> Optional[int]:
        """Linear. Min: 0, Max: 160, Default: 128 (80%)"""
        return getattr(self, "_post_gain", None)

    @post_gain.setter
    def post_gain(self, value: int):
        assert value in range(161)
        self._data.seek(4)
        self._data.write_I(value)
        self._post_gain = value

    def _parse_data_event(self, event: DataEvent) -> None:
        super()._parse_data_event(event)
        if len(event.data) != 8:
            self._log.error(
                "Cannot parse plugin data, expected a size of "
                f"8 bytes; got {len(event.data)} bytes instead"
            )
        self._threshold = self._data.read_I()
        self._post_gain = self._data.read_I()

    def __init__(self):
        super().__init__()
