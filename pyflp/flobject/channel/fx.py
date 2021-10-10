import enum
from typing import Optional, Any, ValuesView

from pyflp.event import Event, WordEvent, DWordEvent
from pyflp.flobject import FLObject
from .enums import ChannelFXEvent

__all__ = ["ChannelFX"]


class ChannelFXReverb(FLObject):
    """Sampler -> Pre-computed effects -> Reverb.

    Used by `ChannelFX.reverb`.
    """

    def setprop(self, name: str, value: Any):
        if name == "kind":
            pass
        elif name == "mix":
            pass

    @enum.unique
    class ReverbKind(enum.IntEnum):
        """Used by `kind`."""

        A = 0
        B = 16384

    @property
    def kind(self) -> Optional[ReverbKind]:
        return getattr(self, "_kind", None)

    @kind.setter
    def kind(self, value: ReverbKind):
        self._kind = value

    @property
    def mix(self) -> Optional[int]:
        return getattr(self, "_mix", None)

    @mix.setter
    def mix(self, value: int):
        self._mix = value

    def save(self) -> ValuesView[Event]:
        event = super().save()

        value = 0
        if self.kind is not None:
            value += self.kind
        if self.mix is not None:
            value += self.mix
        buffer = value.to_bytes(4, "little")
        self._events["reverb"].dump(buffer)

        return event

    def _parse_dword_event(self, event: DWordEvent) -> None:
        if event.id == ChannelFXEvent.Reverb:
            self._events["reverb"] = event
            value = event.to_uint32()
            if value > 16384:
                self._kind = ChannelFXReverb.ReverbKind.B
                self._mix = value - 16384
            else:
                self._kind = ChannelFXReverb.ReverbKind.A
                self._mix = value


class ChannelFX(FLObject):
    """Contains FX properties related to a Sampler/Audio channel.

    Used by `pyflp.flobject.channel.channel.Channel.fx`.
    """

    @property
    def pre_amp(self) -> Optional[int]:
        """Sampler -> Pre-computed effects -> Boost."""
        return getattr(self, "_pre_amp", None)

    @pre_amp.setter
    def pre_amp(self, value: int):
        self.setprop("pre_amp", value)

    @property
    def stereo_delay(self) -> Optional[int]:
        """Sampler -> Pre-computed effects -> Stereo Delay."""
        return getattr(self, "_stereo_delay", None)

    @stereo_delay.setter
    def stereo_delay(self, value: int):
        self.setprop("stereo_delay", value)

    @property
    def reverb(self) -> Optional[ChannelFXReverb]:
        """Sampler -> Pre-computed effects -> Reverb."""
        return getattr(self, "_reverb", None)

    @reverb.setter
    def reverb(self, value: ChannelFXReverb):
        self._reverb = value

    def _parse_word_event(self, event: WordEvent) -> None:
        data = event.to_uint16()

        if event.id == ChannelFXEvent.PreAmp:
            self._events["pre_amp"] = event
            self._pre_amp = data
        elif event.id == ChannelFXEvent.StereoDelay:
            self._events["stereo_delay"] = event
            self._stereo_delay = data

    def _parse_dword_event(self, event: DWordEvent) -> None:
        if event.id == ChannelFXEvent.Reverb:
            self._reverb = ChannelFXReverb()
            self._reverb.parse_event(event)

    def __init__(self):
        super().__init__()
