# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

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
