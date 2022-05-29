import enum

from pyflp._event import DataEventType
from pyflp._properties import _EnumProperty, _IntProperty, _UIntProperty
from pyflp.plugin._plugin import _EffectPlugin


class FStereoEnhancer(_EffectPlugin):
    """Implements Fruity Stereo Enhancer. 6 knobs. 24 bytes.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Stereo%20Enhancer.htm)
    """

    CHUNK_SIZE = 24

    class EffectPosition(enum.IntEnum):
        """Pre or post effect position. Used by `effect_position`."""

        PRE = 0
        POST = 1

    class PhaseInversion(enum.IntEnum):
        """None, left, right phase inversion. Used by `phase_inversion`."""

        NONE = 0
        LEFT = 1
        RIGHT = 2

    def _setprop(self, n, v):
        r = self._r
        if n == "pan":
            r.seek(0)
        if n == "volume":
            r.seek(4)
        elif n == "stereo_separation":
            r.seek(8)
        elif n == "phase_offset":
            r.seek(12)
        elif n == "effect_position":
            r.seek(16)
        elif n == "phase_inversion":
            r.seek(20)
        r.write_I(v)

    # * Properties
    pan: int = _IntProperty(min_=-128, max_=127)
    """Min: -128, Max: 127, Default: 0 (0.50, Centred). Linear."""

    volume: int = _UIntProperty(max_=320)
    """Min: 0, Max: 320, Default: 256 (0.80, 0dB). Logarithmic."""

    stereo_separation: int = _IntProperty(min_=-96, max_=96)
    """Min: -96 (100% separation), Max: 96 (100% merged), Default: 0. Linear."""

    phase_offset: int = _IntProperty(min_=-512, max_=512)
    """Min: -512 (500ms L), Max: 512 (500ms R), Default: 0 (no offset). Linear."""

    phase_inversion: PhaseInversion = _EnumProperty(PhaseInversion)
    """0: none, 1: left, 2: right Default: 0. Linear. Stepped."""

    effect_position: EffectPosition = _EnumProperty(EffectPosition)
    """0: pre, 1: post , Default: 0. Linear. Stepped."""

    # * Parsing logic
    def _parse_data_event(self, e: DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        self._pan = r.read_i()
        self._volume = r.read_I()
        self._stereo_separation = r.read_i()
        self._phase_offset = r.read_i()
        self._effect_position = self.EffectPosition(r.read_I())
        self._phase_inversion = self.PhaseInversion(r.read_I())
