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

HEADER_MAGIC = b"FLhd"
HEADER_SIZE = 6
DATA_MAGIC = b"FLdt"

VALID_PPQS = (24, 48, 72, 96, 120, 144, 168, 192, 384, 768, 960)
