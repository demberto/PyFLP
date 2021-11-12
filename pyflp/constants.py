BYTE = 0
WORD = 64
DWORD = 128
TEXT = 192
DATA = 208

DATA_TEXT_EVENTS = (
    TEXT + 49,  # ArrangementEventID.Name
    TEXT + 39,  # FilterChannelEventID.Name
    TEXT + 47,  # TrackEventID.Name
)
"""TextEvents occupying event ID space used by DataEvents"""
