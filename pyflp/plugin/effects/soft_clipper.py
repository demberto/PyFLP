from pyflp.event import _DataEventType
from pyflp.plugin.plugin import _EffectPlugin
from pyflp.properties import _IntValidator, _UIntProperty, _UIntValidator


class FSoftClipper(_EffectPlugin):
    """Implements Fruity Soft Clipper. 2 knobs. 8 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Soft%20Clipper.htm)
    """

    _chunk_size = 8

    def _setprop(self, n, v):
        r = self._r
        if n == "threshold":
            r.seek(0)
        elif n == "post":
            r.seek(4)
        r.write_I(0)

    # * Properties
    threshold: int = _UIntProperty(_IntValidator(1, 127))
    """Threshold. Min: 1, Max: 127, Default: 100 (0.60, -4.4dB). Logarithmic."""

    post: int = _UIntProperty(_UIntValidator(160))
    """Post gain. Min: 0, Max: 160, Default: 128 (80%). Linear."""

    def _parse_data_event(self, e: _DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        self._threshold = r.read_I()
        self._post = r.read_I()

    def __init__(self):
        super().__init__()
