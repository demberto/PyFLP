from bytesioex import BytesIOEx

from pyflp._event import _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _IntProperty

__all__ = ["ChannelLevels", "ChannelLevelsEvent"]


class ChannelLevelsEvent(_DataEvent):
    """Implements `Channel.EventID.Levels`."""

    _chunk_size = 24

    def __init__(self, data: bytes):
        from pyflp.channel.channel import Channel

        super().__init__(Channel.EventID.Levels, data)
        self.__r = r = BytesIOEx(data)
        self.pan = r.read_i()
        self.volume = r.read_i()
        self.pitch_shift = r.read_i()
        self._u1 = r.read_i()
        self._u2 = r.read_i()
        self._u3 = r.read_i()

    def __repr__(self) -> str:
        return "<ChannelLevelsEvent {}, {}, {}>".format(
            f"pan={self.pan}",
            f"volume={self.volume}",
            f"pitch_shift={self.pitch_shift}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "pan":
            r.seek(0)
        elif n == "volume":
            r.seek(4)
        elif n == "pitch_shift":
            r.seek(8)
        elif n == "_u1":
            r.seek(12)
        elif n == "_u2":
            r.seek(16)
        elif n == "_u3":
            r.seek(20)
        r.write_i(v)
        r.seek(0)
        super().dump(r.read())


class ChannelLevels(_FLObject):
    """Used by `Channel.levels`."""

    def _setprop(self, n, v):
        self.__cle.dump(n, v)
        super()._setprop(n, v)

    pan = _IntProperty()

    volume = _IntProperty()

    pitch_shift = _IntProperty()
    """Pitch shift (in cents)."""

    def _parse_data_event(self, e: ChannelLevelsEvent) -> None:
        self.__cle = self._events["levels"] = e
        self._pan = e.pan
        self._volume = e.volume
        self._pitch_shift = e.pitch_shift
