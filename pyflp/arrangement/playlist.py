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

import abc
import dataclasses
import enum
import warnings
from typing import TYPE_CHECKING, Dict, List, TypeVar

from bytesioex import BytesIOEx

from pyflp._event import DataEventType
from pyflp._flobject import _FLObject
from pyflp._utils import FLVersion
from pyflp.constants import DATA

if TYPE_CHECKING:
    from pyflp.project import Project


@dataclasses.dataclass
class _PlaylistItem(abc.ABC):
    """ABC for `ChannelPlaylistItem` and `PatternPlaylistItem`."""

    position: int
    length: int
    start_offset: int
    end_offset: int
    muted: bool


@dataclasses.dataclass
class ChannelPlaylistItem(_PlaylistItem):
    channel: int  # TODO


@dataclasses.dataclass
class PatternPlaylistItem(_PlaylistItem):
    pattern: int  # TODO


PlaylistItemType = TypeVar("PlaylistItemType", bound=_PlaylistItem)


class Playlist(_FLObject):
    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `Playlist`."""

        # _LoopBar = WORD + 20
        # _LoopEndBar = WORD + 26
        # _Item = DWORD + 1

        Events = DATA + 25
        """See `Playlist.items`."""

    # * Properties
    @property
    def items(self) -> Dict[int, List[PlaylistItemType]]:
        return self._items

    # * Parsing logic
    def _parse_data_event(self, event: DataEventType):
        if event.id_ == Playlist.EventID.Events:
            self._events["event"] = event

            # Validation
            if not len(event.data) % 32 == 0:
                warnings.warn(
                    "Playlist event is not divisible into 32 byte chunks", UserWarning
                )
                return
            self._r = r = BytesIOEx(event.data)
            while True:
                position = r.read_I()  # 4
                if position is None:
                    break
                pattern_base = r.read_H()  # 6
                item_idx = r.read_H()  # 8
                length = r.read_I()  # 12
                track = r.read_i()  # 16
                if FLVersion(self._project.misc.version).major >= 20:
                    track = 499 - track
                else:
                    track = 198 - track
                r.seek(2, 1)  # 18
                item_flags = r.read_H()  # 20
                r.seek(4, 1)  # 24
                muted = True if (item_flags & 0x2000) > 0 else False

                # Init the list if not
                track_events = self.items.get(track)
                if not track_events:
                    track_events = []

                if item_idx <= pattern_base:
                    ppq = self._project.misc.ppq
                    start_offset = int(r.read_f() * ppq)  # 28
                    end_offset = int(r.read_f() * ppq)  # 32

                    # Cannot access tracks from here; handled by Parser
                    track_events.append(
                        ChannelPlaylistItem(
                            position,
                            length,
                            start_offset,
                            end_offset,
                            muted,
                            channel=item_idx,
                        )
                    )
                else:
                    start_offset = r.read_i()  # 28
                    end_offset = r.read_i()  # 32

                    track_events.append(
                        PatternPlaylistItem(
                            position,
                            length,
                            start_offset,
                            end_offset,
                            muted,
                            pattern=item_idx - pattern_base - 1,
                        )
                    )

    def __init__(self, project: "Project") -> None:
        super().__init__(project, None)
        self._items: Dict[int, List[PlaylistItemType]] = {}
