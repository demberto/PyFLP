from pyflp.event import _DataEventType
from pyflp.properties import _UIntProperty, _IntProperty
from pyflp.validators import _IntValidator, _UIntValidator
from pyflp.plugin.plugin import _EffectPlugin


class FSend(_EffectPlugin):
    """Implements Fruity Send. 4 knobs. 16 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Send.htm)
    """

    _chunk_size = 16

    def _setprop(self, n, v):
        r = self._r
        if n == "dry":
            r.seek(0)
        elif n == "pan":
            r.seek(4)
        elif n == "volume":
            r.seek(8)
        elif n == "send_to":
            r.seek(12)
        r.write_i(v)

    # * Properties
    dry: int = _UIntProperty(_UIntValidator(256))
    """Dry/wet. Min: 0 (0%), Max: 256 (100%), Default: 256 (100%). Linear."""

    pan: int = _IntProperty(_IntValidator(-128, 127))
    """Pan. Min: -128 (100% left), Max: 127 (100% right),
    Default: 0 (Centred). Linear."""

    volume: int = _UIntProperty(_UIntValidator(320))
    """Volume. Min: 0 (-INF db, 0.00), Max: 320 (5.6 dB, 1.90),
    Default: 256 (0.0 dB, 1.00). Logarithmic."""

    send_to: int = _IntProperty()
    """Target insert index; depends on insert routing. Default: -1 (Master)."""

    # * Parsing logic
    def _parse_data_event(self, e: _DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        self._pan = r.read_I()
        self._dry = r.read_I()
        self._volume = r.read_I()
        self._send_to = r.read_i()
