from typing import List, Optional, ValuesView

from pyflp.flobject import FLObject
from pyflp.event import DataEvent, TextEvent, Event
from pyflp.bytesioex import BytesIOEx, UInt, Bool, Float

from .playlist import _PlaylistItem
from .enums import TrackEvent

__all__ = ["Track"]


class Track(FLObject):
    max_count = 500  # TODO

    # * Properties
    @property
    def name(self) -> Optional[str]:
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self.setprop("name", value)

    @property
    def index(self) -> Optional[int]:
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        self._events_data.seek(0)
        self._events_data.write(UInt.pack(value))
        self._index = value

    @property
    def color(self) -> Optional[int]:
        return getattr(self, "_color", None)

    @color.setter
    def color(self, value: int):
        self._events_data.seek(4)
        self._events_data.write(UInt.pack(value))
        self._color = value

    @property
    def icon(self) -> Optional[int]:
        return getattr(self, "_icon", None)

    @icon.setter
    def icon(self, value: int):
        self._events_data.seek(8)
        self._events_data.write(UInt.pack(value))
        self._icon = value

    @property
    def enabled(self) -> Optional[bool]:
        return getattr(self, "_enabled", None)

    @enabled.setter
    def enabled(self, value: bool):
        self._events_data.seek(12)
        self._events_data.write(Bool.pack(value))
        self._enabled = value

    @property
    def height(self) -> Optional[float]:
        return getattr(self, "_height", None)

    @height.setter
    def height(self, value: float):
        self._events_data.seek(13)
        self._events_data.write(Float.pack(value))
        self._height = value

    @property
    def locked_height(self) -> float:
        return getattr(self, "_locked_height", None)

    @locked_height.setter
    def locked_height(self, value: float):
        self._events_data.seek(17)
        self._events_data.write(Float.pack(value))
        self._locked_height = value

    @property
    def locked_to_content(self) -> bool:
        return getattr(self, "_locked_to_content", None)

    @locked_to_content.setter
    def locked_to_content(self, value: bool):
        self._events_data.seek(21)
        self._events_data.write(Bool.pack(value))
        self._locked_to_content = value

    @property
    def motion(self) -> Optional[int]:
        return getattr(self, "_motion", None)

    @motion.setter
    def motion(self, value: int):
        self._events_data.seek(22)
        self._events_data.write(UInt.pack(value))
        self._motion = value

    @property
    def press(self) -> Optional[int]:
        return getattr(self, "_press", None)

    @press.setter
    def press(self, value: int):
        self._events_data.seek(26)
        self._events_data.write(UInt.pack(value))
        self._press = value

    @property
    def trigger_sync(self) -> Optional[int]:
        return getattr(self, "_trigger_sync", None)

    @trigger_sync.setter
    def trigger_sync(self, value: int):
        self._events_data.seek(30)
        self._events_data.write(UInt.pack(value))
        self._trigger_sync = value

    @property
    def queued(self) -> Optional[int]:
        return getattr(self, "_queued", None)

    @queued.setter
    def queued(self, value: int):
        self._events_data.seek(34)
        self._events_data.write(UInt.pack(value))
        self._queued = value

    @property
    def tolerant(self) -> Optional[int]:
        return getattr(self, "_tolerant", None)

    @tolerant.setter
    def tolerant(self, value: int):
        self._events_data.seek(38)
        self._events_data.write(UInt.pack(value))
        self._tolerant = value

    @property
    def position_sync(self) -> Optional[int]:
        return getattr(self, "_position_sync", None)

    @position_sync.setter
    def position_sync(self, value: int):
        self._events_data.seek(42)
        self._events_data.write(UInt.pack(value))
        self._position_sync = value

    @property
    def grouped_with_above(self) -> Optional[bool]:
        return getattr(self, "_grouped_with_above", None)

    @grouped_with_above.setter
    def grouped_with_above(self, value: bool):
        self._events_data.seek(46)
        self._events_data.write(Bool.pack(value))
        self._grouped_with_above = value

    @property
    def locked(self) -> Optional[bool]:
        return getattr(self, "_locked", None)

    @locked.setter
    def locked(self, value: bool):
        self._events_data.seek(47)
        self._events_data.write(Bool.pack(value))
        self._locked = value

    @property
    def items(self) -> List[_PlaylistItem]:
        return getattr(self, "_items", [])

    @items.setter
    def items(self, value: List[_PlaylistItem]):
        self._items = value

    # * Parsing logic
    def _parse_text_event(self, event: TextEvent):
        if event.id == TrackEvent.Name:
            self.parse_str_prop(event, "name")

    def _parse_data_event(self, event: DataEvent):
        if event.id == TrackEvent.Data:
            self._events["data"] = event
            self._events_data = BytesIOEx(event.data)
            self._index = self._events_data.read_uint32()  # 4
            self._color = self._events_data.read_int32()  # 8
            self._icon = self._events_data.read_int32()  # 12
            self._enabled = self._events_data.read_bool()  # 13
            self._height = self._events_data.read_float()  # 17
            self._locked_height = self._events_data.read_float()  # 21
            self._locked_to_content = self._events_data.read_bool()  # 22
            self._motion = self._events_data.read_uint32()  # 26
            self._press = self._events_data.read_uint32()  # 30
            self._trigger_sync = self._events_data.read_uint32()  # 34
            self._queued = self._events_data.read_uint32()  # 38
            self._tolerant = self._events_data.read_uint32()  # 42
            self._position_sync = self._events_data.read_uint32()  # 46
            self._grouped_with_above = self._events_data.read_bool()  # 47
            self._locked = self._events_data.read_bool()  # 48
            self._u2 = self._events_data.read(1)  # 49

    def save(self) -> ValuesView[Event]:
        self._events_data.seek(0)
        self._events["data"].dump(self._events_data.read())
        return super().save()

    def __init__(self):
        super().__init__()
