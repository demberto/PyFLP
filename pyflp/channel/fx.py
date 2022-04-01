import enum
from typing import Optional

from pyflp.constants import DWORD, WORD
from pyflp.event import WordEvent, _DWordEventType
from pyflp.flobject import _FLObject
from pyflp.properties import _EnumProperty, _IntProperty, _UIntProperty
from pyflp.validators import _UIntValidator

__all__ = ["ChannelFX", "ChannelFXReverb"]


# TODO Cleanup
class ChannelFXReverb(_FLObject):
    """Sampler/Audio -> Pre-computed effects -> Reverb. Used by `ChannelFX.reverb`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_sampler.htm#channelsampler_Precomputed)
    """

    class _Mix(_UIntProperty):
        def __set__(self, obj, value):

            # Update obj._kind and obj._mix
            super().__set__(obj, value)

            buf = (obj._kind + obj._mix).to_bytes(4, "little")
            obj._events["reverb"].dump(buf)

    class _Kind(_EnumProperty):
        def __set__(self, obj, value):

            # Update obj._kind and obj._mix
            super().__set__(obj, value)

            buf = (obj._kind + obj._mix).to_bytes(4, "little")
            obj._events["reverb"].dump(buf)

    class Kind(enum.IntEnum):
        """Sampler/Audio Reverb type (A or B). Used by `kind`."""

        A = 0
        B = 65536

        @classmethod
        def default(cls):
            return cls.B

    kind: Optional[Kind] = _Kind(Kind)
    """See `Kind`."""

    mix: Optional[int] = _Mix(_UIntValidator(256))
    """Reverb mix (dry/wet). Min: 0, Max: 256, Default: 0."""

    def _parse_dword_event(self, e: _DWordEventType) -> None:
        self._events["reverb"] = e
        value = e.to_uint32()
        default = self.Kind.default()
        if value >= default:
            self._kind = self.Kind.B
            self._mix = value - default
        else:
            self._kind = self.Kind.A
            self._mix = value


class ChannelFX(_FLObject):
    """Sampler/Audio -> Pre-computed effects. Used by `Channel.fx`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_sampler.htm#channelsampler_Precomputed)
    """

    @enum.unique
    class EventID(enum.IntEnum):
        """Event IDs used by `ChannelFX`."""

        CutOff = WORD + 7
        """See `ChannelFX.cutoff`."""

        PreAmp = WORD + 10
        """See `ChannelFX.boost`."""

        FadeOut = WORD + 11
        """See `ChannelFX.fade_out`."""

        FadeIn = WORD + 12
        """See `ChannelFX.fade_in`."""

        Resonance = WORD + 19
        """See `ChannelFX.resonance`."""

        StereoDelay = WORD + 21
        """See `ChannelFX.stereo_delay`."""

        Reverb = DWORD + 11
        """See `ChannelFX.reverb` and `ChannelFXReverb`."""

    cutoff: Optional[int] = _UIntProperty(_UIntValidator(1024))
    """Filter Mod X. Min = 0, Max = 1024, Default = 1024."""

    fade_in: Optional[int] = _UIntProperty(_UIntValidator(1024))
    """Quick fade-in. Min = 0, Max = 1024, Default = 0."""

    fade_out: Optional[int] = _UIntProperty(_UIntValidator(1024))
    """Quick fade-out. Min = 0, Max = 1024, Default = 0."""

    pre_amp: Optional[int] = _UIntProperty(_UIntValidator(256))
    """Boost. Min: 0, Max: 256, Default: 0."""

    resonance: Optional[int] = _UIntProperty(_UIntValidator(1024))
    """Filter Mod Y. Min = 0, Max = 1024, Default = 0."""

    @property
    def reverb(self) -> Optional[ChannelFXReverb]:
        """See `ChannelFXReverb`."""
        return getattr(self, "_reverb", None)

    stereo_delay: Optional[int] = _IntProperty()

    def _parse_word_event(self, e: WordEvent) -> None:
        if e.id == ChannelFX.EventID.CutOff:
            self._parse_H(e, "cutoff")
        elif e.id == ChannelFX.EventID.PreAmp:
            self._parse_H(e, "pre_amp")
        elif e.id == ChannelFX.EventID.FadeOut:
            self._parse_H(e, "fade_out")
        elif e.id == ChannelFX.EventID.Resonance:
            self._parse_H(e, "resonance")
        elif e.id == ChannelFX.EventID.FadeIn:
            self._parse_H(e, "fade_in")
        elif e.id == ChannelFX.EventID.StereoDelay:
            self._parse_H(e, "stereo_delay")

    def _parse_dword_event(self, e: _DWordEventType) -> None:
        if e.id == ChannelFX.EventID.Reverb:
            self._parse_flobject(e, "reverb", ChannelFXReverb())
