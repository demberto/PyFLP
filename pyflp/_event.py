# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

import abc
import enum
from typing import Generic, TypeVar

import colour
from bytesioex import Bool, Byte, Int, SByte, Short, UInt, UShort

from pyflp._utils import buflen_to_varint
from pyflp.constants import BYTE, DATA, DATA_TEXT_EVENTS, DWORD, TEXT, WORD
from pyflp.exceptions import Error

EventIDType = TypeVar("EventIDType", enum.IntEnum, int)
VT = TypeVar("VT")


class EventIDOutOfRangeError(Error, ValueError):
    def __init__(self, id_: EventIDType, min_: int, max_: int) -> None:
        super().__init__(f"Expected ID in {min_}-{max_}; got {id_} instead")


class InvalidEventChunkSizeError(Error, TypeError):
    def __init__(self, expected: int, got: int) -> None:
        super().__init__(f"Expected a bytes object of length {expected}; got {got}")


class EventBase(abc.ABC, Generic[VT]):
    """Abstract base class representing an event."""

    def __init__(self, id: EventIDType, data: bytes) -> None:
        """
        Args:
            id (EventID): An event ID from **0** to **255**.
            data (bytes): A `bytes` object.
        """
        self.id_ = id
        self.data = data

    def __repr__(self) -> str:
        rid = iid = int(self.id_)
        if isinstance(self.id_, enum.IntEnum):
            rid = f"{str(self.id_)!r}, {iid!r}"
        return f"<{type(self).__name__!r} id={rid!r}, value={self.value}>"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            raise TypeError(f"Cannot compare equality between an event and {type(o)!r}")
        return self.id_ == o.id_ and self.data == o.data

    def __ne__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            raise TypeError(
                f"Cannot compare inequality between an event and {type(o)!r}"
            )
        return self.id_ != o.id_ or self.data != o.data

    @property
    @abc.abstractmethod
    def size(self) -> int:
        """Raw event size in bytes."""

    @property
    @abc.abstractmethod
    def value(self) -> VT:
        """Deserialized event-type specific value."""

    @abc.abstractmethod
    def dump(self, value: VT) -> None:
        """Converts Python types into bytes objects and stores it."""

    def to_raw(self) -> bytes:
        return int.to_bytes(self.id_, 1, "little") + self.data


EventType = TypeVar("EventType", bound=EventBase)


class ByteEventBase(EventBase[VT], abc.ABC):
    """Represents a byte-sized event."""

    @property
    def size(self) -> int:
        return 2

    def __init__(self, id_: EventIDType, data: bytes):
        """
        Args:
            id_ (EventID): An event ID from **0** to **63**.
            data (bytes): A 1 byte sized `bytes` object.

        Raises:
            ValueError: When `id_` is not in range of 0-63.
            TypeError: When size of `data` is not 1.
        """
        if id_ not in range(BYTE, WORD):
            raise EventIDOutOfRangeError(id_, BYTE, WORD)
        if len(data) != 1:
            raise InvalidEventChunkSizeError(1, len(data))
        super().__init__(id_, data)


class BoolEvent(ByteEventBase[bool]):
    @property
    def value(self) -> bool:
        return Bool.unpack(self.data)[0]

    def dump(self, value: bool):
        self.data = Bool.pack(value)


class I8Event(ByteEventBase[int]):
    @property
    def value(self) -> int:
        return SByte.unpack(self.data)[0]

    def dump(self, value: int):
        self.data = SByte.pack(value)


class U8Event(ByteEventBase[int]):
    @property
    def value(self) -> int:
        return Byte.unpack(self.data)[0]

    def dump(self, value: int):
        self.data = Byte.pack(value)


class WordEventBase(EventBase[int], abc.ABC):
    """Represents a 2 byte event."""

    @property
    def size(self) -> int:
        return 3

    def __init__(self, id_: EventIDType, data: bytes) -> None:
        """
        Args:
            id_ (EventID): An event ID from **64** to **127**.
            data (bytes): A `bytes` object of size 2.

        Raises:
            ValueError: When `id_` is not in range of 64-127.
            TypeError: When size of `data` is not 2.
        """
        if id_ not in range(WORD, DWORD):
            raise EventIDOutOfRangeError(id_, WORD, DWORD)
        if len(data) != 2:
            raise InvalidEventChunkSizeError(2, len(data))
        super().__init__(id_, data)


class I16Event(WordEventBase):
    @property
    def value(self) -> int:
        return Short.unpack(self.data)[0]

    def dump(self, value: int) -> None:
        self.data = Short.pack(value)


class U16Event(WordEventBase):
    @property
    def value(self) -> int:
        return UShort.unpack(self.data)[0]

    def dump(self, value: int) -> None:
        self.data = UShort.pack(value)


class DWordEventBase(EventBase[int]):
    """Represents a 4 byte event."""

    @property
    def size(self) -> int:
        return 5

    def __init__(self, id_: EventIDType, data: bytes) -> None:
        """
        Args:
            id_ (EventID): An event ID from **128** to **191**.
            data (bytes): A `bytes` object of size 4.

        Raises:
            ValueError: When `id_` is not in range of 128-191.
            TypeError: When size of `data` is not 4.
        """
        if id_ not in range(DWORD, TEXT):
            raise EventIDOutOfRangeError(id_, DWORD, TEXT)
        if len(data) != 4:
            raise InvalidEventChunkSizeError(4, len(data))
        super().__init__(id_, data)


class I32Event(DWordEventBase):
    @property
    def value(self) -> int:
        return Int.unpack(self.data)[0]

    def dump(self, value: int) -> None:
        self.data = Int.pack(value)


class U32Event(DWordEventBase):
    @property
    def value(self) -> int:
        return UInt.unpack(self.data)[0]

    def dump(self, value: int) -> None:
        self.data = UInt.pack(value)


class ColorEvent(DWordEventBase):
    """Represents a 4 byte event which stores a color."""

    @property
    def value(self) -> colour.Color:
        r, g, b = (c / 255 for c in self.data[:3])
        return colour.Color(rgb=(r, g, b))

    def dump(self, value: colour.Color) -> None:
        """Dumps a `colour.Color` to event data.

        Args:
            value (colour.Color): The color to be dumped into the event.
        """

        self.data = bytes((int(c * 255) for c in value.rgb)) + b"\x00"


class VariableSizedEventBase(EventBase[VT], abc.ABC):
    """Implements `Event.size` and `Event.to_raw` for `TextEvent` and `DataEvent`."""

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        iid = int(self.id_)
        if isinstance(self.id_, enum.IntEnum):
            return f"<{cls!r} id={self.id_.name!r} ({iid!r}), size={self.size!r}>"
        return f"<{cls!r} id={iid!r}, size={self.size!r}>"

    @property
    def size(self) -> int:
        if self.data:
            return 1 + len(buflen_to_varint(self.data)) + len(self.data)
        return 2

    def to_raw(self) -> bytes:
        id = int.to_bytes(self.id_, 1, "little")
        length = buflen_to_varint(self.data) if self.data else b"\x00"
        data = self.data
        return id + length + data if self.data else id + length


class TextEvent(VariableSizedEventBase[str]):
    """Represents a variable sized event used for storing strings."""

    @staticmethod
    def as_ascii(buf: bytes) -> str:
        return buf.decode("ascii", errors="ignore").strip("\0")

    @staticmethod
    def as_uf16(buf: bytes) -> str:
        return buf.decode("utf-16", errors="ignore").strip("\0")

    def dump(self, value: str) -> None:
        """Dumps a string to the event data. non UTF-16 data for UTF-16 type
        projects and non ASCII data for older projects will be removed before
        dumping.

        Args:
            value (str): The string to be dumped to event data;

        Raises:
            TypeError: When `value` isn't an `str` object.
        """

        # Version TextEvent (ID: 199) is always ASCII
        if self._uses_unicode and self.id_ != 199:
            self.data = value.encode("utf-16-le") + b"\0\0"
        else:
            self.data = value.encode("ascii") + b"\0"

    @property
    def value(self) -> str:
        if self._uses_unicode and self.id_ != 199:
            return self.as_uf16(self.data)
        return self.as_ascii(self.data)

    def __init__(self, id: EventIDType, data: bytes, uses_unicode: bool = True):
        """
        Args:
            id (EventID): An event ID from
                **192** to **207** or in `DATA_TEXT_EVENTS`.
            data (bytes): A `bytes` object.

        Raises:
            ValueError: When `id` is not in range of 192-207 or in `DATA_TEXT_EVENTS`.
        """

        if id not in range(TEXT, DATA) and id not in DATA_TEXT_EVENTS:
            raise ValueError(f"Unexpected ID: {id!r}")
        self._uses_unicode = uses_unicode
        super().__init__(id, data)


class DataEvent(VariableSizedEventBase[bytes]):
    """Represents a variable sized event used for storing a blob of data, consists
    of a collection of POD types like int, bool, float, sometimes ASCII strings.
    Its size is determined by the event and also FL version sometimes.
    The task of parsing is completely handled by one of the FLObject subclasses,
    hence no `to_*` conversion method is provided."""

    CHUNK_SIZE = None
    """Parsing is not done if size of `data` argument is not equal to this."""

    def dump(self, value: bytes):
        """Dumps a blob of bytes to event data as is; no conversions of any-type.
        This method is used instead of directly dumping to event data for type-safety.

        Raises:
            TypeError: When `value` isn't a `bytes` object."""

        # * Changing the length of a data event is rarely needed. Maybe only for
        # * event-in-event type of events (e.g. InsertParamsEvent, Playlist events)
        # ? Maybe make a VariableDataEvent subclass for these events?
        # * This way event data size restrictions can be enforced below.

        if not isinstance(value, bytes):
            raise TypeError(f"Expected a bytes object; got a {type(value)!r} object")
        self.data = value

    def __init__(self, id_: EventIDType, data: bytes):
        """
        Args:
            id_ (EventID): An event ID in from **208** to **255**.
            data (bytes): A `bytes` object.

        Raises:
            ValueError: When `id_` is not in the range of 208-255.
        """
        if id_ < DATA:
            raise EventIDOutOfRangeError(id_, DATA, 255)
        super().__init__(id_, data)
        if self.CHUNK_SIZE is not None:  # pragma: no cover
            if len(data) != self.CHUNK_SIZE:
                return
