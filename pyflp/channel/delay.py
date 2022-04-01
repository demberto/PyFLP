from typing import Any, Optional

from bytesioex import BytesIOEx

from pyflp.event import DataEvent
from pyflp.flobject import _FLObject
from pyflp.properties import _IntProperty

__all__ = ["ChannelDelay", "ChannelDelayEvent"]


class ChannelDelayEvent(DataEvent):
    """Implements `Channel.EventID.Delay`."""

    _chunk_size = 20

    def __init__(self, data: bytes):
        from pyflp.channel.channel import Channel

        super().__init__(Channel.EventID.Delay, data)
        self.__r = r = BytesIOEx(data)
        self.feedback = r.read_I()
        self.pan = r.read_I()
        self.pitch_shift = r.read_I()
        self.echo = r.read_I()
        self.time = r.read_I()

    def __repr__(self) -> str:
        return "<ChannelDelayEvent {}, {}, {}, {}, {}>".format(
            f"feedback={self.feedback}",
            f"pan={self.pan}",
            f"pitch_shift={self.pitch_shift}",
            f"echo={self.echo}",
            f"time={self.time}",
        )

    def dump(self, n, v):
        r = self.__r
        if n == "feedback":
            r.seek(0)
        elif n == "pan":
            r.seek(4)
        elif n == "pitch_shift":
            r.seek(8)
        elif n == "echo":
            r.seek(12)
        elif n == "time":
            r.seek(16)
        r.write_I(v)
        r.seek(0)
        super().dump(r.read())


class ChannelDelay(_FLObject):
    """Used by `Channel.delay`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_misc.htm#EchoDelay)
    """

    def _setprop(self, n: str, v: Any):
        self.__cde.dump(n, v)
        super()._setprop(n, v)

    feedback: Optional[int] = _IntProperty()

    pan: Optional[int] = _IntProperty()

    pitch_shift: Optional[int] = _IntProperty()

    echo: Optional[int] = _IntProperty()

    time: Optional[int] = _IntProperty()

    def _parse_data_event(self, e: ChannelDelayEvent) -> None:
        self.__cde = self._events["delay"] = e
        self._feedback = e.feedback
        self._pan = e.pan
        self._pitch_shift = e.pitch_shift
        self._echo = e.echo
        self._time = e.time
