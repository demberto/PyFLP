from pyflp._event import _DataEventType
from pyflp.plugin._plugin import _SynthPlugin
from pyflp._properties import _UIntProperty, _UIntValidator


class BooBass(_SynthPlugin):
    """Implements BooBass. 3 knobs. 16 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/BooBass.htm)"""

    chunk_size = 16

    def _setprop(self, n: str, v: int):
        r = self._r
        if n == "bass":
            r.seek(4)
        elif n == "mid":
            r.seek(8)
        elif n == "high":
            r.seek(12)
        r.write_I(v)

    bass: int = _UIntProperty(_UIntValidator(65535))
    """Min: 0, Max: 65535, Default: 32767."""

    mid: int = _UIntProperty(_UIntValidator(65535))
    """Min: 0, Max: 65535, Default: 32767."""

    high: int = _UIntProperty(_UIntValidator(65535))
    """Min: 0, Max: 65535, Default: 32767."""

    def _parse_data_event(self, e: _DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        r.seek(4)  # 1, 0, 0, 0
        self._bass = r.read_I()
        self._mid = r.read_I()
        self._high = r.read_I()
