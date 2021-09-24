import enum
from typing import Optional, Any

from pyflp.event import WordEvent, DWordEvent
from pyflp.flobject import FLObject
from pyflp.flobject.channel.event_id import ChannelFXEventID

__all__ = ['ChannelFX']

class ChannelFXReverb(FLObject):
    """Sampler -> Pre-computed effects -> Reverb.
    
    Used by `ChannelFX.reverb`.
    """
    
    def setprop(self, name: str, value: Any):
        if name == 'kind':
            pass
        elif name == 'mix':
            pass
    
    @enum.unique
    class ReverbKind(enum.IntEnum):
        """Used by `kind`."""
        A = 1
        B = 2
    
    @property
    def kind(self) -> Optional[ReverbKind]:
        return getattr(self, '_kind', None)
    
    @kind.setter
    def kind(self, value: ReverbKind):
        self.setprop('kind', value)

    @property
    def mix(self) -> Optional[int]:
        return getattr(self, '_mix', None)
    
    @mix.setter
    def mix(self, value: int):
        self.setprop('mix', value)
    
    def _parse_dword_event(self, event: DWordEvent) -> None:
        if event.id == ChannelFXEventID.Reverb:
            self._events['reverb'] = event
            raise NotImplementedError

class ChannelFX(FLObject):
    """Contains FX properties related to a Sampler/Audio channel.
        
    Used by `pyflp.flobject.channel.channel.Channel.fx`.
    """
    
    @property
    def pre_amp(self) -> Optional[int]:
        """Sampler -> Pre-computed effects -> Boost."""
        return getattr(self, '_pre_amp', None)
    
    @pre_amp.setter
    def pre_amp(self, value: int):
        self.setprop('pre_amp', value)
    
    @property
    def stereo_delay(self) -> Optional[int]:
        """Sampler -> Pre-computed effects -> Stereo Delay."""
        return getattr(self, '_stereo_delay', None)
    
    @stereo_delay.setter
    def stereo_delay(self, value: int):
        self.setprop('stereo_delay', value)
    
    @property
    def reverb(self) -> Optional[ChannelFXReverb]:
        """Sampler -> Pre-computed effects -> Reverb."""
        return getattr(self, '_reverb', None)
    
    @reverb.setter
    def reverb(self, value: ChannelFXReverb):
        self._reverb = value
    
    def _parse_word_event(self, event: WordEvent) -> None:
        data = event.to_uint16()
        
        if event.id == ChannelFXEventID.PreAmp:
            self._events['pre_amp'] = event
            self._pre_amp = data
        elif event.id == ChannelFXEventID.StereoDelay:
            self._events['stereo_delay'] = event
            self._stereo_delay = data
    
    def _parse_dword_event(self, event: DWordEvent) -> None:
        if event.id == ChannelFXEventID.Reverb:
            self._reverb = ChannelFXReverb()
            self._reverb.parse(event)
    
    def __init__(self):
        super().__init__()