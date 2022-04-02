import enum

from pyflp._event import _DataEventType
from pyflp._properties import _EnumProperty, _IntProperty, _UIntProperty
from pyflp.plugin._plugin import _EffectPlugin

__all__ = ["FFastDist"]


class FFastDist(_EffectPlugin):
    """Implements Fruity Fast Dist. 5 knobs. 20 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Fast%20Dist.htm)
    """

    _chunk_size = 20

    class Kind(enum.IntEnum):
        """One of the distortion types. Used by `kind`."""

        A = 0
        B = 1

    def _setprop(self, n, v):
        r = self._r
        if n == "pre":
            r.seek(0)
        elif n == "threshold":
            r.seek(4)
        elif n == "kind":
            r.seek(8)
        elif n == "mix":
            r.seek(12)
        elif n == "post":
            r.seek(16)
        r.write_I(v)

    # * Properties
    pre: int = _IntProperty(min_=64, max_=192)
    """Pre amp. Min: 64 (33%), Max: 192 (100%), Default: 128 (67%). Linear."""

    threshold: int = _IntProperty(min_=1, max_=10)
    """Threshold. Min: 1 (10%), Max: 10 (100%), Default: 10 (100%). Linear. Stepped."""

    kind: Kind = _EnumProperty(Kind)
    """Distortion type. Default: `Kind.A`. See `Kind`."""

    mix: int = _UIntProperty(max_=128)
    """Mix. Min: 0 (0%), Max: 128 (100%), Default: 128 (100%). Linear."""

    post: int = _UIntProperty(max_=128)
    """Post gain. Min: 0 (0%), Max: 128 (100%), Default: 128 (100%). Linear."""

    # * Parsing logic
    def _parse_data_event(self, e: _DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        self._pre = r.read_I()
        self._threshold = r.read_I()
        self._kind = self.Kind(r.read_I())
        self._mix = r.read_I()
        self._post = r.read_I()
