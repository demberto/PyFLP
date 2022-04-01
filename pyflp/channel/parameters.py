from bytesioex import BytesIOEx

from pyflp.channel.arp import ChannelArp
from pyflp.event import DataEvent
from pyflp.flobject import _FLObject

__all__ = ["ChannelParameters", "ChannelParametersEvent"]


class ChannelParametersEvent(DataEvent):
    """Implements `Channel.EventID.Parameters`."""

    def __init__(self, data: bytes):
        from pyflp.channel.channel import Channel

        super().__init__(Channel.EventID.Parameters, data)
        c = ChannelParameters()
        arp = c.arp = self.arp = ChannelArp()

        # The size of the event has increased over the years
        self.__r = r = BytesIOEx(data)
        r.seek(40)
        arp.direction = ChannelArp.Direction(r.read_I())
        arp.range = r.read_I()
        arp.chord = r.read_I()
        arp.time = r.read_f() + 1.0
        arp.gate = r.read_f()
        arp.slide = r.read_bool()
        r.seek(31, 1)
        arp.repeat = r.read_I()

    def __repr__(self) -> str:
        return f"<ChannelParametersEvent size={len(self.data)}>"


class ChannelParameters(_FLObject):
    def __init__(self):
        super().__init__()
        self.arp = ChannelArp()

    def _save(self) -> ChannelParametersEvent:
        e = tuple(self._events.values())[0]
        oldlen = len(e.data)
        r = BytesIOEx(e.data)
        if oldlen > 40:
            r.seek(40)
            arp = self.arp
            r.write_I(arp.direction)
            r.write_I(arp.range)
            r.write_I(arp.chord)
            r.write_f(arp.time - 1.0)
            r.write_f(arp.gate)
            r.write_bool(arp.slide)

        # Prevent writing more data than previously was since write_* methods
        # can add more data than actually was, possibly making the FLP unopenable.
        r.seek(0)
        newbuf = r.read(oldlen)
        r.seek(0)
        r.write(newbuf)
