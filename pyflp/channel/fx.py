# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

import enum
from typing import Optional

from pyflp._event import DWordEventType, _WordEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _EnumProperty, _IntProperty, _UIntProperty
from pyflp.constants import DWORD, WORD

__all__ = ["ChannelFX", "ChannelFXReverb"]


# TODO Cleanup
class ChannelFXReverb(_FLObject):
    """Sampler/Audio -> Pre-computed effects -> Reverb. Used by `ChannelFX.reverb`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_sampler.htm#channelsampler_Precomputed)
    """

    class _Mix(_UIntProperty):
        def __set__(self, obj: "ChannelFXReverb", value) -> None:

            # Update obj._kind and obj._mix
            super().__set__(obj, value)

            buf = (obj._kind + obj._mix).to_bytes(4, "little")
            obj._events["reverb"].dump(buf)

    class _Kind(_EnumProperty):
        def __set__(self, obj: "ChannelFXReverb", value) -> None:

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

    mix: Optional[int] = _Mix(max_=256)
    """Reverb mix (dry/wet). Min: 0, Max: 256, Default: 0."""

    def _parse_dword_event(self, e: DWordEventType) -> None:
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

    cutoff: Optional[int] = _UIntProperty(max_=1024)
    """Filter Mod X. Min = 0, Max = 1024, Default = 1024."""

    fade_in: Optional[int] = _UIntProperty(max_=1024)
    """Quick fade-in. Min = 0, Max = 1024, Default = 0."""

    fade_out: Optional[int] = _UIntProperty(max_=1024)
    """Quick fade-out. Min = 0, Max = 1024, Default = 0."""

    pre_amp: Optional[int] = _UIntProperty(max_=256)
    """Boost. Min: 0, Max: 256, Default: 0."""

    resonance: Optional[int] = _UIntProperty(max_=1024)
    """Filter Mod Y. Min = 0, Max = 1024, Default = 0."""

    @property
    def reverb(self) -> Optional[ChannelFXReverb]:
        """See `ChannelFXReverb`."""
        return getattr(self, "_reverb", None)

    stereo_delay: Optional[int] = _IntProperty()

    def _parse_word_event(self, e: _WordEvent) -> None:
        if e.id_ == ChannelFX.EventID.CutOff:
            self._parse_H(e, "cutoff")
        elif e.id_ == ChannelFX.EventID.PreAmp:
            self._parse_H(e, "pre_amp")
        elif e.id_ == ChannelFX.EventID.FadeOut:
            self._parse_H(e, "fade_out")
        elif e.id_ == ChannelFX.EventID.Resonance:
            self._parse_H(e, "resonance")
        elif e.id_ == ChannelFX.EventID.FadeIn:
            self._parse_H(e, "fade_in")
        elif e.id_ == ChannelFX.EventID.StereoDelay:
            self._parse_H(e, "stereo_delay")

    def _parse_dword_event(self, e: DWordEventType) -> None:
        if e.id_ == ChannelFX.EventID.Reverb:
            self._parse_flobject(e, "reverb", ChannelFXReverb())
