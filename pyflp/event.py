import abc
import enum
from typing import TypeVar, Union

import colour
from bytesioex import Byte, Int, SByte, UInt

from pyflp.constants import BYTE, DATA, DATA_TEXT_EVENTS, DWORD, TEXT, WORD
from pyflp.utils import buflen_to_varint


class Event(abc.ABC):
    """Abstract base class representing an event."""

    _count = 0

    @abc.abstractproperty
    def size(self) -> int:
        """Raw event size in bytes."""

    @property
    def index(self) -> int:
        return self.__index

    @abc.abstractmethod
    def dump(self, new_data):
        """Converts Python data types into bytes
        objects and dumps them to `self.data`."""

    def to_raw(self) -> bytes:
        """Used by Project.save(). Overriden by `_VariabledSizedEvent`."""
        return int.to_bytes(self.id, 1, "little") + self.data

    def __repr__(self) -> str:
        cls = type(self).__name__
        sid = str(self.id)
        iid = int(self.id)
        if isinstance(self.id, enum.IntEnum):
            return f"{cls} id={sid}, {iid}"
        return f"{cls} id={iid}"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            raise TypeError(f"Cannot compare equality between an 'Event' and {type(o)}")
        return self.id == o.id and self.data == o.data

    def __ne__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            raise TypeError(
                f"Cannot compare inequality between an 'Event' and {type(o)}"
            )
        return self.id != o.id or self.data != o.data

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **0** to **255**.
            data (bytes): A `bytes` object.
        """

        self.id = id
        self.data = data
        self.__index = Event._count
        Event._count += 1
        super().__init__()


_EventType = TypeVar("_EventType", bound=Event)


class _VariableSizedEvent(Event):
    """Implements `Event.size` and `Event.to_raw` for `TextEvent` and `DataEvent`."""

    @property
    def size(self) -> int:
        if self.data:
            return 1 + len(buflen_to_varint(self.data)) + len(self.data)
        return 2

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        iid = int(self.id)
        if isinstance(self.id, enum.IntEnum):
            return f"<{cls} id={self.id.name} ({iid}), size={self.size}>"
        return f"<{cls} id={iid}, size={self.size}>"

    def to_raw(self) -> bytes:
        id = int.to_bytes(self.id, 1, "little")
        length = buflen_to_varint(self.data) if self.data else b"\x00"
        data = self.data
        return id + length + data if self.data else id + length


class ByteEvent(Event):
    """Represents a byte-sized event."""

    @property
    def size(self) -> int:
        return 2

    def dump(self, new_data: Union[bytes, int, bool]):
        """Dumps a single byte of data; either a bool, int or a bytes object to event data.

        Args:
            new_data (Union[bytes, int, bool]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_data` is a bytes object and its size isn't equal to 1.
            OverflowError: When an integer is too big to be accumulated in 1 byte.
            TypeError: When `new_data` isn't a bool, int or a bytes object.
        """

        if isinstance(new_data, bytes):
            if len(new_data) != 1:
                raise ValueError(
                    f"Expected a bytes object of 1 byte length; got {new_data}"
                )
            self.data = new_data
        elif isinstance(new_data, int):
            if new_data != abs(new_data):
                if new_data not in range(-128, 128):
                    raise OverflowError(
                        f"Expected a value of -128 to 127; got {new_data}"
                    )
            else:
                if new_data > 255:
                    raise OverflowError(
                        f"Expected a value from 0 to 255; got {new_data}"
                    )
            self.data = new_data.to_bytes(1, "little")
        elif isinstance(new_data, bool):
            data = 1 if new_data else 0
            self.data = data.to_bytes(1, "little")
        else:
            raise TypeError(
                f"Expected a bytes, bool or an int object; got {type(new_data)}"
            )

    def to_uint8(self) -> int:
        return Byte.unpack(self.data)[0]

    def to_int8(self) -> int:
        return SByte.unpack(self.data)[0]

    def to_bool(self) -> bool:
        return self.to_int8() != 0

    def __repr__(self) -> str:
        b = self.to_int8()
        B = self.to_uint8()
        if b == B:
            msg = f"B={B}"
        else:
            msg = f"b={b}, B={B}"
        return f"<{super().__repr__()}, {msg}>"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **0** to **63**.
            data (bytes): A 1 byte sized `bytes` object.

        Raises:
            ValueError: When `id` is not in range of 0-63.
            TypeError: When size of `data` is not 1.
        """

        if not (id < WORD and id >= BYTE):
            raise ValueError(f"Exepcted 0-63; got {id}")
        dl = len(data)
        if dl != 1:
            raise TypeError(f"Unexpected data size; expected 1, got {dl}")
        super().__init__(id, data)


class WordEvent(Event):
    """Represents a 2 byte event."""

    @property
    def size(self) -> int:
        return 3

    def dump(self, new_word: Union[bytes, int]):
        """Dumps 2 bytes of data; either an int or a bytes object to event data.

        Args:
            new_word (Union[bytes, int]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_word` is a bytes object and its size isn't equal to 2.
            OverflowError: When an integer is too big to be accumulated in 2 bytes.
            TypeError: When `new_word` isn't an int or a bytes object.
        """

        if isinstance(new_word, bytes):
            if len(new_word) != 2:
                raise ValueError(
                    f"Expected a bytes object of 2 bytes length; got {new_word}"
                )
            self.data = new_word
        elif isinstance(new_word, int):
            if new_word != abs(new_word):
                if new_word not in range(-32768, 32768):
                    raise OverflowError(
                        f"Expected a value -32768 to 32767; got {new_word}"
                    )
            else:
                if new_word > 65535:
                    raise OverflowError(
                        f"Expected a value of 0 to 65535; got {new_word}"
                    )
            self.data = new_word.to_bytes(2, "little")
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(new_word)}")

    def to_uint16(self) -> int:
        return int.from_bytes(self.data, "little")

    def to_int16(self) -> int:
        return int.from_bytes(self.data, "little", signed=True)

    def __repr__(self) -> str:
        h = self.to_int16()
        H = self.to_uint16()
        if h == H:
            msg = f"H={H}"
        else:
            msg = f"h={h}, H={H}"
        return f"<{super().__repr__()}, {msg}>"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **64** to **127**.
            data (bytes): A `bytes` object of size 2.

        Raises:
            ValueError: When `id` is not in range of 64-127.
            TypeError: When size of `data` is not 2.
        """

        if id not in range(WORD, DWORD):
            raise ValueError(f"Exepcted 64-127; got {id}")
        if len(data) != 2:
            raise TypeError(
                f"Expected a data of 2 bytes; got a data of size {len(data)} instead"
            )
        super().__init__(id, data)


class DWordEvent(Event):
    """Represents a 4 byte event."""

    DWORD_MAX = 4_294_967_295
    """4,294,967,295"""

    INT_MIN = -2_147_483_648
    """-2,147,483,648"""

    INT_MAX = 2_147_483_647
    """2,147,483,647"""

    @property
    def size(self) -> int:
        return 5

    def dump(self, new_dword: Union[bytes, int]):
        """Dumps 4 bytes of data; either an int or a bytes object to event data.

        Args:
            new_dword (Union[bytes, int]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_dword` is a bytes object and its size isn't 4.
            OverflowError: When an integer is too big to be accumulated in 4 bytes.
            TypeError: When `new_dword` isn't an int or a bytes object.
        """

        if isinstance(new_dword, bytes):
            if len(new_dword) != 4:
                raise ValueError(
                    f"Expected a bytes object of 4 bytes length; got {new_dword}"
                )
            self.data = new_dword
        elif isinstance(new_dword, int):
            if new_dword != abs(new_dword):
                if new_dword < self.INT_MIN or new_dword > self.INT_MAX:
                    raise OverflowError(
                        f"Expected a value of {self.INT_MIN} "
                        f"to {self.INT_MAX}; got {new_dword}"
                    )
            elif new_dword > self.DWORD_MAX:
                raise OverflowError(
                    f"Expected a value of 0 to {self.DWORD_MAX}; got {new_dword}"
                )
            self.data = new_dword.to_bytes(4, "little")
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(new_dword)}")

    def to_uint32(self) -> int:
        """Deserializes `self.data` as a 32-bit unsigned integer as an `int`."""
        return UInt.unpack(self.data)[0]

    def to_int32(self) -> int:
        """Deserializes `self.data` as a 32-bit signed integer as an `int`."""
        return Int.unpack(self.data)[0]

    def __repr__(self) -> str:
        i = self.to_int32()
        I = self.to_uint32()
        if i == I:
            msg = f"I={I}"
        else:
            msg = f"i={i}, I={I}"
        return f"<{super().__repr__()}, {msg}>"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **128** to **191**.
            data (bytes): A `bytes` object of size 4.

        Raises:
            ValueError: When `id` is not in range of 128-191.
            TypeError: When size of `data` is not 4.
        """

        if id not in range(DWORD, TEXT):
            raise ValueError(f"Exepcted 128-191; got {id}")
        dl = len(data)
        if dl != 4:
            raise TypeError(f"Unexpected data size; expected 4, got {dl}")
        super().__init__(id, data)


_DWordEventType = TypeVar("_DWordEventType", bound=DWordEvent)


class ColorEvent(DWordEvent):
    """Represents a 4 byte event which stores a color."""

    def dump(self, new_color: colour.Color):
        """Dumps a `colour.Color` to event data.

        Args:
            new_color (colour.Color): The color to be dumped into the event.

        Raises:
            TypeError: When `new_color` isn't a `colour.Color` object."""

        if not isinstance(new_color, colour.Color):
            raise TypeError(f"Expected a colour.Color; got {type(new_color)}")
        self.data = bytes((int(c * 255) for c in new_color.rgb)) + b"\x00"

    def to_color(self) -> colour.Color:
        r, g, b = (c / 255 for c in self.data[:3])
        return colour.Color(rgb=(r, g, b))


class TextEvent(_VariableSizedEvent):
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
        return f'<{super().__repr__()}, s="{self.to_str()}">'

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from \
                **192** to **207** or in `DATA_TEXT_EVENTS`.
            data (bytes): A `bytes` object.

        Raises:
            ValueError: When `id` is not in range of 192-207 or in `DATA_TEXT_EVENTS`.
        """

        if id not in range(TEXT, DATA) and id not in DATA_TEXT_EVENTS:
            raise ValueError(f"Unexpected ID: {id}")
        if not isinstance(data, bytes):
            raise TypeError(f"Expected a bytes object; got {type(data)}")
        super().__init__(id, data)


class DataEvent(_VariableSizedEvent):
    """Represents a variable sized event used for storing a blob of data, consists
    of a collection of POD types like int, bool, float, sometimes ASCII strings.
    Its size is determined by the event and also FL version sometimes.
    The task of parsing is completely handled by one of the FLObject subclasses,
    hence no `to_*` conversion method is provided."""

    _chunk_size = None
    """Used by subclasses. Parsing is cancelled if this is
    not equal to size of bytes passed to `__init__`."""

    def dump(self, new_bytes: bytes):
        """Dumps a blob of bytes to event data as is; no conversions of any-type.
        This method is used instead of directly dumping to event data for type-safety.

        Raises:
            TypeError: When `new_bytes` isn't a `bytes` object."""

        # * Changing the length of a data event is rarely needed. Maybe only for
        # * event-in-event type of events (e.g. InsertParamsEvent, Playlist events)
        # ? Maybe make a VariableDataEvent subclass for these events?
        # * This way event data size restrictions can be enforced below.

        if not isinstance(new_bytes, bytes):
            raise TypeError(f"Expected a bytes object; got a {type(new_bytes)} object")
        self.data = new_bytes

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID in from **208** to **255**.
            data (bytes): A `bytes` object.

        Raises:
            ValueError: When the event ID is not in the range of 208 (`DATA`) to 255.
        """

        if id < DATA:
            raise ValueError(f"Expected an event ID from 209 to 255; got {id}")
        if not isinstance(data, bytes):
            raise TypeError(f"Expected a bytes object; got {type(data)}")
        super().__init__(id, data)
        if self._chunk_size:  # pragma: no cover
            if len(data) != self._chunk_size:
                return


_DataEventType = TypeVar("_DataEventType", bound=DataEvent)
