from pyflp.event import _DataEventType
from pyflp.plugin.plugin import _EffectPlugin
from pyflp.properties import _IntProperty, _IntValidator


class FBalance(_EffectPlugin):
    """Implements Fruity Balance. 2 knobs. 8 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Balance.htm)
    """

    _chunk_size = 8

    def _setprop(self, n, v):
        r = self._r
        if n == "pan":
            r.seek(0)
        elif n == "volume":
            r.seek(4)
        r.write_i(v)

    # * Properties
    pan: int = _IntProperty(_IntValidator(-128, 127))
    """Panning. Min: -128, Max: 127, Default: 0 (0.50, Centred). Linear."""

    volume: int = _IntProperty(_IntValidator(0, 320))
    """Volume. Min: 0, Max: 320, Default: 256 (0.80, 0dB). Logarithmic."""

    def _parse_data_event(self, e: _DataEventType) -> None:
        super()._parse_data_event(e)
        self._pan = self._r.read_I()
        self._volume = self._r.read_I()
