import enum

from pyflp.utils import (
    TEXT,
    WORD,
    DATA,
    DWORD
)

__all__ = ['ArrangementEventID',
           'PlaylistEventID',
           'TimeMarkerEventID',
           'TrackEventID']

@enum.unique
class ArrangementEventID(enum.IntEnum):
    Name = TEXT + 49
    Index = WORD + 35

@enum.unique
class PlaylistEventID(enum.IntEnum):
    #_LoopBar = WORD + 20
    #_LoopEndBar = WORD + 26
    #_Item = DWORD + 1
    Events = DATA + 25

@enum.unique
class TimeMarkerEventID(enum.IntEnum):
    Position = DWORD + 20
    Numerator = 33
    Denominator = 34
    Name = TEXT + 13

@enum.unique
class TrackEventID(enum.IntEnum):
    Name = TEXT + 47
    Data = DATA + 30