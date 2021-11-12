from bytesioex import BytesIOEx

from pyflp.event import DataEvent
from pyflp.flobject import _FLObject
from pyflp.properties import _IntProperty


class ChannelLevelOffsetsEvent(DataEvent):
    """Implements `Channel.EventID.LevelOffsets`."""

    _chunk_size = 20

    def __init__(self, data: bytes):
        from pyflp.channel.channel import Channel

        super().__init__(Channel.EventID.LevelOffsets, data)
        self.__r = r = BytesIOEx(data)
        self.pan = r.read_i()
        self.volume = r.read_i()
        self._u1 = r.read_i()
        self.mod_x = r.read_i()
        self.mod_y = r.read_i()

    def __repr__(self):
        return "<ChannelLevelOffsetsEvent {}, {}, {}, {}>".format(
            f"pan={self.pan}",
            f"volume={self.volume}",
            f"mod_x={self.mod_x}",
            f"mod_y={self.mod_y}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "pan":
            r.seek(0)
        elif n == "volume":
            r.seek(4)
        elif n == "_u1":
            r.seek(8)
        elif n == "mod_x":
            r.seek(12)
        elif n == "mod_y":
            r.seek(16)
        r.write_I(v)
        r.seek(0)
        super().dump(r.read())


class ChannelLevelOffsets(_FLObject):
    """Used by `Channel.delay`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#EchoDelay)
    """

    def _setprop(self, n, v):
        self.__cloe.dump(n, v)
        super()._setprop(n, v)

    pan = _IntProperty()

    volume = _IntProperty()

    mod_x = _IntProperty()

    mod_y = _IntProperty()

    def _parse_data_event(self, e: ChannelLevelOffsetsEvent) -> None:
        self.__cloe = self._events["delay"] = e
        self._pan = e.pan
        self._volume = e.volume
        self._mod_x = e.mod_x
        self._mod_y = e.mod_y
