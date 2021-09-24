import enum

from pyflp.utils import (
    WORD,
    DWORD,
    TEXT,
    DATA
)

__all__ = ['MiscEventID']

@enum.unique
class MiscEventID(enum.IntEnum):
    Version = TEXT + 7
    VersionBuild = DWORD + 31
    LoopActive = 9
    ShowInfo = 10
    Shuffle = 11
    #_MainVol = 12
    #_FitToSteps = 13
    TimeSigNum = 17
    TimeSigBeat = 18
    PanningLaw = 23
    PlayTruncatedNotes = 30
    #_Tempo = WORD + 2
    CurrentPatternNum = WORD + 3
    #_MainPitch = WORD + 16
    #_TempoFine = WORD + 29
    CurrentFilterChannelNum = DWORD + 18
    SongLoopPos = DWORD + 24
    Tempo = DWORD + 28
    Title = TEXT + 2
    Comment = TEXT + 3
    Url = TEXT + 5
    _CommentRtf = TEXT + 6
    RegName = TEXT + 8
    DataPath = TEXT + 10
    Genre = TEXT + 14
    Artists = TEXT + 15
    SaveTimestamp = DATA + 29