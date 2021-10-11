import abc
import dataclasses
from typing import Dict, List

from pyflp.event import DataEvent
from pyflp.flobject.flobject import FLObject

from .enums import PlaylistEvent

from bytesioex import BytesIOEx

__all__ = ["Playlist"]


@dataclasses.dataclass
class _PlaylistItem(abc.ABC):
    """ABC for ChannelPlaylistItem and PatternPlaylistItem"""

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


class Playlist(FLObject):
    ppq = 0
    max_count = 1

    # * Properties
    @property
    def items(self) -> Dict[int, List[_PlaylistItem]]:
        return getattr(self, "__items", {})

    @items.setter
    def items(self, value: Dict[int, List[_PlaylistItem]]):
        self.__items = value

    # * Parsing logic
    def _parse_data_event(self, event: DataEvent):
        if event.id == PlaylistEvent.Events:
            self._events["event"] = event

            # Validation
            if not len(event.data) % 32 == 0:
                self._log.error("Cannot parse these playlist events, contact me!")
            self._events_data = BytesIOEx(event.data)
            while True:
                position = self._events_data.read_I()  # 4
                if not position:
                    break
                pattern_base = self._events_data.read_I()  # 6
                pattern_id = self._events_data.read_I()  # 8
                length = self._events_data.read_I()  # 12
                track = self._events_data.read_i()  # 16
                if self.fl_version.major >= 20:
                    track = 499 - track
                else:
                    track = 198 - track
                self._events_data.seek(2, 1)  # 18
                item_flags = self._events_data.read_H()  # 20
                self._events_data.seek(4, 1)  # 24
                muted = True if (item_flags & 0x2000) > 0 else False

                # Init the list if not
                track_events = self.items.get(track)
                if not track_events:
                    track_events = []

                if pattern_id <= pattern_base:
                    start_offset = int(self._events_data.read_f() * Playlist.ppq)  # 28
                    end_offset = int(self._events_data.read_f() * Playlist.ppq)  # 32

                    # Cannot access tracks from here, ProjectParser
                    # or Arrangement must assign self._events to tracks
                    track_events.append(
                        ChannelPlaylistItem(
                            position,
                            length,
                            start_offset,
                            end_offset,
                            muted,
                            pattern_id,
                        )
                    )
                else:
                    start_offset = self._events_data.read_i()  # 28
                    end_offset = self._events_data.read_i()  # 32

                    track_events.append(
                        PatternPlaylistItem(
                            position,
                            length,
                            start_offset,
                            end_offset,
                            muted,
                            pattern_id - pattern_base - 1,
                        )
                    )

    def __init__(self):
        super().__init__()
        self.items: Dict[int, List[_PlaylistItem]] = {}
