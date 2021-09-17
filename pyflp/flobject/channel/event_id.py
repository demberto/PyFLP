import enum

from pyflp.utils import (
    WORD,
    DWORD,
    TEXT,
    DATA
)

__all__ = ['ChannelEventID', 'FilterChannelEventID']

class ChannelEventID(enum.IntEnum):
    """Event IDs used by :class:`Channel`."""
    Enabled = 0
    #_Vol = 2
    #_Pan = 3
    Zipped = 15
    #UseLoopPoints = 19
    Kind = 21
    TargetInsert = 22
    #FXProperties = 27
    Locked = 32
    New = WORD
    #Fx = WORD + 5
    #FadeStereo = WORD + 6
    #CutOff = WORD + 7
    Volume = WORD + 8
    Pan = WORD + 9
    #PreAmp = WORD + 10
    #Decay = WORD + 11
    #Attack = WORD + 12
    #DotNote = WORD + 13
    #DotPitch = WORD + 14
    #DotMix = WORD + 15
    #Resonance = WORD + 19
    #StereoDelay = WORD + 21
    #Fx3 = WORD + 22
    #DotReso = WORD + 23
    #DotCutOff = WORD + 24
    #ShiftDelay = WORD + 25
    #Dot = WORD + 27
    #DotRel = WORD + 32
    #DotShift = WORD + 28
    Layer = WORD + 30
    #Swing = WORD + 33
    Color = DWORD
    #Echo = DWORD + 2
    #FxSine = DWORD + 3
    #CutSelfCutBy = DWORD + 4
    RootNote = DWORD + 7
    #_MainResoCutOff = DWORD + 9
    #DelayModXY = DWORD + 10
    #Reverb = DWORD + 11
    #StretchTime = DWORD + 12
    #FineTune = DWORD + 14
    #SamplerFlags = DWORD + 15
    #LayerFlags = DWORD + 16
    FilterChannelNum = DWORD + 17
    #AUSampleRate = DWORD + 25
    Icon = DWORD + 27
    Name = TEXT
    SamplePath = TEXT + 4
    #GeneratorName = TEXT + 9
    #Delay = DATA + 1
    Plugin = DATA + 5

@enum.unique
class FilterChannelEventID(enum.IntEnum):
    """Event IDs used by :class:`FilterChannel`."""
    Name = TEXT + 39