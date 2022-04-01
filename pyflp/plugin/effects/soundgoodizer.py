import enum

from pyflp.event import _DataEventType
from pyflp.plugin.plugin import _EffectPlugin
from pyflp.properties import _EnumProperty, _UIntProperty, _UIntValidator

__all__ = ["Soundgoodizer"]


class Soundgoodizer(_EffectPlugin):
    """Implements Soundgoodizer. 2 knobs. 12 bytes

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Soundgoodizer.htm)
    """

    _chunk_size = 12

    class Mode(enum.IntEnum):
        """One of the Soundgoodizer modes. Used by `Soundgoodizer.mode`."""

        A = 0
        B = 1
        C = 2
        D = 3

    def _setprop(self, n, v):
        r = self._r
        if n == "mode":
            r.seek(4)
        elif n == "amount":
            r.seek(8)
        r.write_I(v)

    mode: Mode = _EnumProperty(Mode)
    """See `Mode`. Default: `Mode.A`"""

    amount: int = _UIntProperty(_UIntValidator(1000))
    """Amount. Min: 0, Max: 1000, Default: 600. Logarithmic."""

    def _parse_data_event(self, e: _DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        r.seek(4)  # 3, 0, 0, 0
        self._mode = r.read_I()
        self._amount = r.read_I()

    def __init__(self):
        super().__init__()
