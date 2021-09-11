import enum

from pyflp.utils import *

class EventID(enum.IntEnum):
    """Parsed directly by ProjectParser/Unparsed/unimplemented/TODO events"""
    bNoteOn = 1
    bMidiChan = 4
    bMidiNote = 5
    bMidiPatch = 6
    bMidiBank = 7
    _Pitchable = 14
    bDelayFlags = 16
    bLoopType = 20

    _RandChan = WORD + 17
    _MixerChannel = WORD + 18
    
    dReserved = DWORD + 8
    _SsNote = DWORD + 13
    _dPatternAutoMode = DWORD + 23
    
    dMidiCtrls = DATA
    
    # Parsed directly by ProjectParser
    InsertParams = DATA + 15    # This event occurs only once

@enum.unique
class InsertParamEventID(enum.IntEnum):
    """Events inside event, nice design IL"""
    SlotEnabled = 0
    # SlotVolume = 1
    SlotMix = 1
    SendLevelStart = 64     # 64 - 191 are send level events
    Volume = 192
    Pan = 193
    StereoSeparation = 194
    LowLevel = 208
    BandLevel = 209
    HighLevel = 210
    LowFreq = 216
    BandFreq = 217
    HighFreq = 218
    LowQ = 224
    BandQ = 225
    HighQ = 226