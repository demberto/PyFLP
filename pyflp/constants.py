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

try:
    from typing import Final
except ImportError:
    from typing_extensions import Final

BYTE: Final = 0
WORD: Final = 64
DWORD: Final = 128
TEXT: Final = 192
DATA: Final = 208

HEADER_MAGIC: Final = b"FLhd"
HEADER_SIZE: Final = 6
DATA_MAGIC: Final = b"FLdt"
VALID_PPQS: Final = (24, 48, 72, 96, 120, 144, 168, 192, 384, 768, 960)

DATA_TEXT_EVENTS: Final = (
    TEXT + 49,  # Arrangement.EventID.Name
    TEXT + 39,  # FilterChannel.EventID.Name
    TEXT + 47,  # Track.EventID.Name
)
"""`TextEvent`s occupying event ID space used by `DataEvent`s"""
