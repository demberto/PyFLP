import enum

from pyflp.utils import *

class EventID(enum.IntEnum):
    """Unparsed/unimplemented/TODO events"""
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
    
    tMidiCtrls = TEXT + 16