import enum

from pyflp.utils import (
    WORD,
    DWORD,
    TEXT,
    DATA
)

__all__ = ['PatternEventID']

@enum.unique
class PatternEventID(enum.IntEnum):
    New = WORD + 1
    #_Data = WORD + 4
    Color = DWORD + 22
    Name = TEXT + 1
    #_157 = DWORD + 29   # FL 12.5+
    #_158 = DWORD + 30   # default: -1
    #_164 = DWORD + 36   # default: 0
    #Controllers = DATA + 15
    Notes = DATA + 16