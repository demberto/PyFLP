import enum
from typing import Any, List, Optional

import colour
from bytesioex import BytesIOEx

from pyflp.arrangement.playlist import _PlaylistItem
from pyflp.constants import DATA, TEXT
from pyflp.event import DataEvent, TextEvent
from pyflp.flobject import _FLObject
from pyflp.properties import (
    _BoolProperty,
    _ColorProperty,
    _EnumProperty,
    _FloatProperty,
    _IntProperty,
    _StrProperty,
    _UIntProperty,
)
from pyflp.validators import _FloatValidator, _IntValidator


# TODO Track data events are as big as 66 bytes
class TrackDataEvent(DataEvent):
    """Implements `TrackEventID.Data` for `Track`."""

    def __init__(self, data: bytes):
        super().__init__(Track.EventID.Data, data)
        self.__r = r = BytesIOEx(data)
        self.number = r.read_I()  # 4
        self.color = r.read_i()  # 8
        self.icon = r.read_i()  # 12
        self.enabled = r.read_bool()  # 13
        self.height = r.read_f()  # 17
        self.locked_height = r.read_i()  # 21
        self.locked_to_content = r.read_bool()  # 22
        self.motion = Track.Motion(r.read_I())  # 26
        self.press = Track.Press(r.read_I())  # 30
        self.trigger_sync = Track.Sync(r.read_I())  # 34
        self.queued = bool(r.read_I())  # 38
        self.tolerant = bool(r.read_I())  # 42
        self.position_sync = Track.Sync(r.read_I())  # 46
        self.grouped = r.read_bool()  # 47
        self.locked = r.read_bool()  # 48
        self._u2 = r.read(1)  # 49

    def dump(self, n: str, v: Any) -> None:
        r = self.__r
        if isinstance(v, colour.Color):
            v = bytes((int(c * 255) for c in v.rgb)) + b"\x00"
        else:
            v = int(v)
        if n == "number":
            r.seek(0)
            r.write_I(v)
        elif n == "color":
            r.seek(4)
            r.write(v)
        elif n == "icon":
            r.seek(8)
            r.write_i(v)
        elif n == "enabled":
            r.seek(12)
            r.write_bool(v)
        elif n == "height":
            r.seek(13)
            r.write_f(v)
        elif n == "locked_height":
            r.seek(17)
            r.write_f(v)
        elif n == "locked_to_content":
            r.seek(21)
            r.write_bool(v)
        elif n == "motion":
            r.seek(22)
            r.write_I(v)
        elif n == "press":
            r.seek(26)
            r.write_I(v)
        elif n == "trigger_sync":
            r.seek(30)
            r.write_I(v)
        elif n == "queued":
            r.seek(34)
            r.write_I(v)
        elif n == "tolerant":
            r.seek(38)
            r.write_I(v)
        elif n == "position_sync":
            r.seek(42)
            r.write_I(v)
        elif n == "grouped":
            r.seek(46)
            r.write_bool(v)
        elif n == "locked":
            r.seek(47)
            r.write_bool(v)
        r.seek(0)
        super().dump(r.read())


class Track(_FLObject):
    max_count = 500

    def _setprop(self, n: str, v: Any):
        if not n == "name":
            self.__tde.dump(n, v)
        setattr(self, "_" + n, v)

    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `Track`."""

        Name = TEXT + 47
        """See `Track.name`. Default event does not exist."""

        Data = DATA + 30
        """See `TrackDataEvent`."""

    @enum.unique
    class Press(enum.IntEnum):
        """Used by `Track.press`."""

        Retrigger = 0
        HoldStop = 1
        HoldMotion = 2
        Latch = 3

    @enum.unique
    class Motion(enum.IntEnum):
        """Used by `Track.motion`."""

        Stay = 0
        OneShot = 1
        MarchWrap = 2
        MarchStay = 3
        MarchStop = 4
        Random = 5
        ExclusiveRandom = 6

    @enum.unique
    class Sync(enum.IntEnum):
        """Used by `Track.position_sync` and `Track.trigger_sync`."""

        Off = 0
        QuarterBeat = 1
        HalfBeat = 2
        Beat = 3
        TwoBeats = 4
        FourBeats = 5
        Auto = 6

    # * Properties
    name: Optional[str] = _StrProperty()

    number: Optional[int] = _UIntProperty(_IntValidator(1, 500))
    """Index. Part of `TrackDataEvent`. Min: 1, Max: 500.
    A prior version of FL 20 didn't dump unused tracks."""

    color: Optional[colour.Color] = _ColorProperty()

    icon: Optional[int] = _IntProperty()

    enabled: Optional[bool] = _BoolProperty()
    """Whether in enabled state or not."""

    height: Optional[float] = _FloatProperty(_FloatValidator(0.0, 18.4))
    """Min: 0.0 (0%), Max: 18.4 (1840%), Default: 1.0 (100%)."""

    # TODO: What value this stores exactly is unclear yet.
    locked_height: Optional[int] = _IntProperty()

    locked_to_content: Optional[bool] = _BoolProperty()

    motion: Optional[Motion] = _EnumProperty(Motion)
    """Performance settings -> Motion. See `Motion`. Default: `Motion.Stay`."""

    press: Optional[Press] = _EnumProperty(Press)
    """Performance settings -> Press. See `Press`. Default: `Press.Retrigger`."""

    trigger_sync: Optional[Sync] = _EnumProperty(Sync)
    """Performance settings -> Trigger sync. See `Sync`. Default: `Sync.Off`."""

    queued: Optional[bool] = _BoolProperty()
    """Performance settings -> Queued. Default: False."""

    tolerant: Optional[bool] = _BoolProperty()
    """Performance settings -> Tolerant. Default: True."""

    position_sync: Optional[Sync] = _EnumProperty(Sync)
    """Performance settings -> Position sync. See `Sync`. Default: `Sync.FourBeats`."""

    grouped: Optional[bool] = _BoolProperty()
    """Whether grouped with above or not. Default: False."""

    locked: Optional[bool] = _BoolProperty()
    """Whether in locked state or not. Default: False."""

    @property
    def items(self) -> List[_PlaylistItem]:
        return getattr(self, "_items", [])

    # * Parsing logic
    def _parse_text_event(self, event: TextEvent):
        if event.id == Track.EventID.Name:
            self._parse_s(event, "name")

    def _parse_data_event(self, e: TrackDataEvent):
        self.__tde = self._events["data"] = e
        self._number = e.number
        self._color = e.color
        self._icon = e.icon
        self._enabled = e.enabled
        self._height = e.height
        self._locked_height = e.locked_height
        self._locked_to_content = e.locked_to_content
        self._motion = e.motion
        self._press = e.press
        self._trigger_sync = e.trigger_sync
        self._queued = e.queued
        self._tolerant = e.tolerant
        self._position_sync = e.position_sync
        self._grouped = e.grouped
        self._locked = e.locked
