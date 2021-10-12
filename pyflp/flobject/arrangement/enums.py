import enum

from pyflp.utils import TEXT, WORD, DATA, DWORD

__all__ = ["ArrangementEvent", "PlaylistEvent", "TimeMarkerEvent", "TrackEvent"]


@enum.unique
class ArrangementEvent(enum.IntEnum):
    Name = TEXT + 49
    New = WORD + 35


@enum.unique
class PlaylistEvent(enum.IntEnum):
    # _LoopBar = WORD + 20
    # _LoopEndBar = WORD + 26
    # _Item = DWORD + 1
    Events = DATA + 25


@enum.unique
class TimeMarkerEvent(enum.IntEnum):
    Position = DWORD + 20
    Numerator = 33
    Denominator = 34
    Name = TEXT + 13


@enum.unique
class TrackEvent(enum.IntEnum):
    Name = TEXT + 47
    Data = DATA + 30
