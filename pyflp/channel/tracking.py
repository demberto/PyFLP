from bytesioex import BytesIOEx

from pyflp.event import DataEvent
from pyflp.flobject import _FLObject
from pyflp.properties import _IntProperty

__all__ = ["ChannelTracking", "ChannelTrackingEvent"]


class ChannelTrackingEvent(DataEvent):
    """Implements `Channel.EventID.Tracking`."""

    _chunk_size = 16

    def __init__(self, data: bytes):
        from pyflp.channel.channel import Channel

        super().__init__(Channel.EventID.Tracking, data)
        self.__r = r = BytesIOEx(data)
        self.middle_value = r.read_i()
        self.pan = r.read_i()
        self.mod_x = r.read_i()
        self.mod_y = r.read_i()

    def __repr__(self) -> str:
        return "<ChannelTrackingEvent {}, {}, {}, {}>".format(
            f"middle_value={self.middle_value}",
            f"pan={self.pan}",
            f"mod_x={self.mod_x}",
            f"mod_y={self.mod_y}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "middle_value":
            r.seek(0)
        elif n == "pan":
            r.seek(4)
        elif n == "mod_x":
            r.seek(8)
        elif n == "mod_y":
            r.seek(12)
        r.write_i(v)
        r.seek(0)
        super().dump(r.read())


class ChannelTracking(_FLObject):
    """Used by `Channel.tracking`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#Tracking)
    """

    def _setprop(self, n, v):
        self.__cte.dump(n, v)
        super()._setprop(n, v)

    middle_value: int = _IntProperty()

    pan: int = _IntProperty()

    mod_x: int = _IntProperty()

    mod_y: int = _IntProperty()

    def _parse_data_event(self, e: ChannelTrackingEvent) -> None:
        self.__cte = self._events["levels"] = e
        self._middle_value = e.middle_value
        self._pan = e.pan
        self._mod_x = e.mod_x
        self._mod_y = e.mod_y
