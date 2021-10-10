import enum
from typing import Union

from pyflp.event.event import VariableSizedEvent
from pyflp.utils import TEXT, DATA, DATA_TEXT_EVENTS

__all__ = ["TextEvent"]


class TextEvent(VariableSizedEvent):
    """Represents a variable sized event used for storing strings."""

    uses_unicode = True  # Parser can change this

    @staticmethod
    def as_ascii(buf: bytes):
        return buf.decode("ascii", errors="ignore").strip("\0")

    @staticmethod
    def as_uf16(buf: bytes):
        return buf.decode("utf-16", errors="ignore").strip("\0")

    def dump(self, new_text: str):
        """Dumps a string to the event data. non UTF-16 data for UTF-16 type
        projects and non ASCII data for older projects will be removed before
        dumping.

        Args:
            new_text (str): The string to be dumped to event data;

        Raises:
            TypeError: When `new_data` isn't an `str` object.
        """

        if not isinstance(new_text, str):
            raise TypeError(f"Expected an str object; got {type(new_text)}")
        # Version event (199) is always ASCII
        if TextEvent.uses_unicode and self.id != 199:
            self.data = new_text.encode("utf-16", errors="ignore") + b"\0\0"
        else:
            self.data = new_text.encode("ascii", errors="ignore") + b"\0"

    def to_str(self) -> str:
        if TextEvent.uses_unicode and self.id != 199:
            return self.as_uf16(self.data)
        return self.as_ascii(self.data)

    def __repr__(self) -> str:
        return f"{super().__repr__()}, String: {self.to_str()}"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id not in range(TEXT, DATA) and id not in DATA_TEXT_EVENTS:
            raise ValueError(f"Unexpected ID: {id}")
        super().__init__(id, data)
