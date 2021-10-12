from typing import Any, Optional

from pyflp.event import DataEvent
from pyflp.flobject import FLObject

from bytesioex import BytesIOEx  # type: ignore

from .enums import ChannelEvent

__all__ = ["ChannelDelay"]


class ChannelDelay(FLObject):
    """Implements `ChannelEvent.Delay`, used by `Channel.delay`."""

    def __setprop(self, n: str, v: Any):
        assert isinstance(v, int), f"ChannelDelay.{n} must be an int"
        if n == "feedback":
            self.__r.seek(0)
        elif n == "pan":
            self.__r.seek(4)
        elif n == "pitch_shift":
            self.__r.seek(8)
        elif n == "echo":
            self.__r.seek(12)
        elif n == "time":
            self.__r.seek(16)
        self.__r.write_I(v)
        self.__r.seek(0)
        self._events["delay"].dump(self.__r.read())
        setattr(self, "_" + n, v)

    @property
    def feedback(self) -> Optional[int]:
        """Feedback"""
        return getattr(self, "_feedback", None)

    @feedback.setter
    def feedback(self, value: int):
        self.__setprop("feedback", value)

    @property
    def pan(self) -> Optional[int]:
        """Pan"""
        return getattr(self, "_pan", None)

    @pan.setter
    def pan(self, value: int):
        self.__setprop("pan", value)

    @property
    def pitch_shift(self) -> Optional[int]:
        return getattr(self, "_pitch_shift", None)

    @pitch_shift.setter
    def pitch_shift(self, value: int):
        """Pitch-shift"""
        self.__setprop("pitch_shift", value)

    @property
    def echo(self) -> Optional[int]:
        """Echo"""
        return getattr(self, "_echo", None)

    @echo.setter
    def echo(self, value: int):
        self.__setprop("echo", value)

    @property
    def time(self) -> Optional[int]:
        """TIme"""
        return getattr(self, "_time", None)

    @time.setter
    def time(self, value: int):
        self.__setprop("time", value)

    def _parse_data_event(self, ev: DataEvent) -> None:
        assert ev.id == ChannelEvent.Delay
        self._events["delay"] = ev
        if len(ev.data) != 20:
            self._log.error(
                f"Unexpected ChannelDelay data size. Expected 20; got {len(ev.data)}"
            )
        self.__r = BytesIOEx(ev.data)
        self._feedback = self.__r.read_I()  # type: ignore
        self._pan = self.__r.read_I()  # type: ignore
        self._pitch_shift = self.__r.read_I()  # type: ignore
        self._echo = self.__r.read_I()  # type: ignore
        self._time = self.__r.read_I()  # type: ignore
