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

from abc import ABC, abstractmethod
from enum import IntEnum, unique
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
    Sized,
    SupportsBytes,
    Tuple,
    TypeVar,
    Union,
)
from warnings import warn

from bytesioex import (
    Bool,
    Byte,
    BytesIOEx,
    Float,
    Int,
    SByte,
    Short,
    UInt,
    ULong,
    UShort,
)
from colour import Color

__all__ = [
    "AsciiEvent",
    "BooBassEvent",
    "BoolEvent",
    "BYTE",
    "ColorEvent",
    "DATA",
    "DataArrayEvent",
    "DataEventBase",
    "DWORD",
    "Error",
    "EventID",
    "EventType",
    "F32Event",
    "FixedSizeEventBase",
    "FruityBalanceEvent",
    "FruityFastDistEvent",
    "FruityNotebook2Event",
    "FruitySendEvent",
    "FruitySoftClipperEvent",
    "FruityStereoEnhancerEvent",
    "I8Event",
    "I16Event",
    "I32Event",
    "NEW_TEXT_IDS",
    "PluginEvent",
    "SoundgoodizerEvent",
    "StrEventBase",
    "StructEventBase",
    "TEXT",
    "U8Event",
    "U16Event",
    "U16TupleEvent",
    "U32Event",
    "U64VariableEvent",
    "UnicodeEvent",
    "UnknownDataEvent",
    "WORD",
]

BYTE = 0
WORD = 64
DWORD = 128
TEXT = 192
DATA = 208
NEW_TEXT_IDS = (
    TEXT + 49,  # Arrangement.EventID.Name
    TEXT + 39,  # FilterChannel.EventID.Name
    TEXT + 47,  # Track.EventID.Name
)

_T = TypeVar("_T")


class Error(Exception):
    """Base class for PyFLP exceptions."""


class EventIDOutOfRangeError(Error, ValueError):
    def __init__(self, id, min_i, max_e):
        super().__init__(f"Expected ID in {min_i}-{max_e - 1}; got {id} instead")


class InvalidEventChunkSizeError(Error, TypeError):
    def __init__(self, expected, got):
        super().__init__(f"Expected a bytes object of length {expected}; got {got}")


class UnexpectedTypeError(Error, TypeError):
    def __init__(self, expected, got):
        super().__init__(f"Expected a {expected} object; got a {got} object instead")


class EventBase(ABC, Generic[_T], Sized, SupportsBytes):
    """Abstract base class representing an event."""

    def __init__(self, id: int, data: bytes) -> None:
        self.id = id
        self._raw = data

    def __eq__(self, o: "EventBase") -> bool:
        return self.id == o.id and self._raw == o._raw

    def __ne__(self, o: "EventBase") -> bool:
        return self.id != o.id or self._raw != o._raw

    @abstractmethod
    def __bytes__(self) -> bytes:
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Raw event size in bytes."""

    @property
    def value(self) -> _T:
        """Deserialized event-type specific value."""
        return self._raw

    @value.setter
    def value(self, value: _T) -> None:
        """Converts Python types into bytes/bytes objects and stores it."""
        self._raw = value


EventType = TypeVar("EventType", bound=EventBase)


class FixedSizeEventBase(EventBase[_T], ABC):
    def __bytes__(self) -> bytes:
        return Byte.pack(self.id) + self._raw

    def __repr__(self) -> str:
        rid = iid = int(self.id)
        if isinstance(self.id, IntEnum):
            rid = f"{self.id!r}, {iid!r}"
        return f"<{type(self).__name__!r} id={rid!r}, value={self.value}>"


class ByteEventBase(FixedSizeEventBase[_T], ABC):
    """Represents a byte-sized event."""

    def __init__(self, id: int, data) -> None:
        """
        Args:
            id (int): An event ID from **0** to **63**.
            data (bytes): A 1 byte sized `bytes` object.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 0-63.
            InvalidEventChunkSizeError: When size of `data` is not 1.
        """
        if id not in range(BYTE, WORD):
            raise EventIDOutOfRangeError(id, BYTE, WORD)

        if len(data) != 1:
            raise InvalidEventChunkSizeError(1, len(data))

        super().__init__(id, data)

    def __len__(self) -> int:
        return 2


class BoolEvent(ByteEventBase[bool]):
    @property
    def value(self) -> bool:
        return Bool.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[bool]) -> None:
        if value is not None:
            self._raw = Bool.pack(value)


class I8Event(ByteEventBase[int]):
    @property
    def value(self) -> int:
        return SByte.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = SByte.pack(value)


class U8Event(ByteEventBase[int]):
    @property
    def value(self) -> int:
        return Byte.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = Byte.pack(value)


class WordEventBase(FixedSizeEventBase[_T], ABC):
    """Represents a 2 byte event."""

    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID from **64** to **127**.
            data (bytes): A `bytes` object of size 2.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 64-127.
            InvalidEventChunkSizeError: When size of `data` is not 2.
        """
        if id not in range(WORD, DWORD):
            raise EventIDOutOfRangeError(id, WORD, DWORD)

        if len(data) != 2:
            raise InvalidEventChunkSizeError(2, len(data))

        super().__init__(id, data)

    def __len__(self) -> int:
        return 3


class I16Event(WordEventBase[int]):
    @property
    def value(self) -> int:
        return Short.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = Short.pack(value)


class U16Event(WordEventBase[int]):
    @property
    def value(self) -> int:
        return UShort.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = UShort.pack(value)


class DWordEventBase(FixedSizeEventBase[_T], ABC):
    """Represents a 4 byte event."""

    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID from **128** to **191**.
            data (bytes): A `bytes` object of size 4.

        Raises:
            EventIDOutOfRangeError: When `id` is not in range of 128-191.
            InvalidEventChunkSizeError: When size of `data` is not 4.
        """
        if id not in range(DWORD, TEXT):
            raise EventIDOutOfRangeError(id, DWORD, TEXT)

        if len(data) != 4:
            raise InvalidEventChunkSizeError(4, len(data))

        super().__init__(id, data)

    def __len__(self) -> int:
        return 5


class F32Event(DWordEventBase[float]):
    @property
    def value(self) -> float:
        return Float.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[float]) -> None:
        if value is not None:
            self._raw = Float.pack(value)


class I32Event(DWordEventBase[int]):
    @property
    def value(self) -> int:
        return Int.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = Int.pack(value)


class U32Event(DWordEventBase[int]):
    @property
    def value(self) -> int:
        return UInt.unpack(self._raw)[0]

    @value.setter
    def value(self, value: Optional[int]) -> None:
        if value is not None:
            self._raw = UInt.pack(value)


class U16TupleEvent(DWordEventBase[Tuple[int, int]]):
    @property
    def value(self) -> Tuple[int, int]:
        return UInt.unpack(self._raw)

    @value.setter
    def value(self, value: Tuple[int, int]) -> None:
        self._raw = UInt.pack(*value)


class ColorEvent(DWordEventBase[Color]):
    """Represents a 4 byte event which stores a color."""

    @property
    def value(self) -> Color:
        r, g, b = (c / 255 for c in self._raw[:3])
        return Color(rgb=(r, g, b))

    @value.setter
    def value(self, value: Color) -> None:
        self._raw = bytes((int(c * 255) for c in value.rgb)) + b"\x00"


class VariableSizedEventBase(EventBase[_T], ABC):
    @staticmethod
    def _to_varint(buffer: bytes) -> bytearray:
        ret = bytearray()
        buflen = len(buffer)
        while True:
            towrite = buflen & 0x7F
            buflen >>= 7
            if buflen > 0:
                towrite |= 0x80
            ret.append(towrite)
            if buflen <= 0:
                break
        return ret

    def __len__(self) -> int:
        if self._raw is not None:
            return 1 + len(self._to_varint(self._raw)) + len(self._raw)
        return 2

    def __bytes__(self) -> bytes:
        id = Byte.pack(self.id)

        if self._raw != b"":
            return id + self._to_varint(self._raw) + self._raw
        return id + b"\x00"


class U64VariableEvent(VariableSizedEventBase):
    def __len__(self):
        if self._raw:
            return 9 + len(self._raw)
        return 9


#     @property
#     def data(self, value):
#         self._raw = value.encode("ascii") if isinstance(value, str) else value

#     def __bytes__(self):
#         id = UInt.pack(self.id)
#         length = ULong.pack(len(self._raw))  # 8 bytes for denoting size, IL?
#         return id + length + self._raw if self._raw else id + length


class StrEventBase(VariableSizedEventBase[str], ABC):
    """Represents a variable sized event used for storing strings."""

    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID from **192** to **207** or in `NEW_TEXT_EVENTS`.
            data (bytes): Event data.

        Raises:
            ValueError: When `id` is not in range of 192-207 or in `NEW_TEXT_EVENTS`.
        """
        if id not in {*range(TEXT, DATA), *NEW_TEXT_IDS}:
            raise ValueError(f"Unexpected ID: {id!r}")

        super().__init__(id, data)

    def __repr__(self):
        return f"<{type(self).__name__} id={self.id!r}, string={self.value!r}>"


class AsciiEvent(StrEventBase):
    @property
    def value(self) -> str:
        return self._raw.decode("ascii").rstrip("\0")

    @value.setter
    def value(self, value: Optional[str]) -> None:
        if value is not None:
            self._raw = value.encode("ascii") + b"\0"


class UnicodeEvent(StrEventBase):
    @property
    def value(self) -> str:
        return self._raw.decode("utf-16-le").rstrip("\0")

    @value.setter
    def value(self, value: Optional[str]) -> None:
        if value is not None:
            self._raw = value.encode("utf-16-le") + b"\0\0"


class DataEventBase(VariableSizedEventBase[bytes], ABC):
    def __init__(self, id: int, data: bytes) -> None:
        """
        Args:
            id (int): An event ID in from **208** to **255**.
            data (bytes): Event data.

        Raises:
            ValueError: When `id` is not in the range of 208-255.
        """
        if id < DATA:
            raise EventIDOutOfRangeError(id, DATA, 255)

        self.stream_len = len(data)
        self.stream = BytesIOEx(data)
        super().__init__(id, data)

    def __bytes__(self) -> bytes:
        self._raw = self.stream.getvalue()
        return super().__bytes__()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id!r}, size={self.stream_len}>"


class DataArrayEvent(DataEventBase):
    pass


class UnknownDataEvent(DataEventBase):
    pass


class StructEventBase(DataEventBase, ABC):
    """Represents an event used for storing fixed size structured data.

    Consists of a collection of POD types like int, bool, float, but not strings.
    Its size is determined by the event and also FL version sometimes.
    """

    SIZE: int = 0
    PROPS: dict[str, Union[str, int]] = {}

    def __init__(self, id: int, data: bytes, truncate=True) -> None:
        super().__init__(id, data)
        self.props: Dict[str, Any] = {}
        self._truncate = truncate

        if self.SIZE != 0 and len(data) != self.SIZE:
            warn(f"Expected chunk size {self.SIZE} for {id}; got {len(data)}")

        for name, type_or_size in self.PROPS.items():
            if isinstance(type_or_size, str):
                readfunc = getattr(self.stream, "read_" + type_or_size)
                self.props[name] = readfunc()
            else:
                self.props[name] = self.stream.read(type_or_size)

    def __bytes__(self) -> bytes:
        self.stream.seek(0)
        if self._truncate:
            self.stream.truncate(self.stream_len)  # Prevent accidental oversizing

        for name, type_or_size in self.PROPS.items():
            value = self.props[name]
            if isinstance(type_or_size, str) and value is not None:
                writefunc = getattr(self.stream, "write_" + type_or_size)
                writefunc(value)
            else:
                self.stream.write(value)
        return super().__bytes__()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id!r}, size={self.stream_len}, props={self.props!r}>"  # noqa


class ChannelDelayEvent(StructEventBase):
    SIZE = 20
    PROPS = dict.fromkeys(("feedback", "pan", "pitch_shift", "echoes", "time"), "I")


class ChannelEnvelopeLFOEvent(StructEventBase):
    SIZE = 68
    PROPS = {
        "flags": "i",  # 4
        "envelope.enabled": "i",  # 8
        "envelope.predelay": "i",  # 12
        "envelope.attack": "i",  # 16
        "envelope.hold": "i",  # 20
        "envelope.decay": "i",  # 24
        "envelope.sustain": "i",  # 28
        "envelope.release": "i",  # 32
        "_u20": 20,  # 52
        "lfo.shape": "i",  # 56
        "envelope.attack_tension": "i",  # 60
        "envelope.sustain_tension": "i",  # 64
        "envelope.release_tension": "i",  # 68
    }


class ChannelLevelAdjustsEvent(StructEventBase):
    SIZE = 20
    PROPS = {"pan": "I", "volume": "I", "_u4": 4, "mod_x": "I", "mod_y": "I"}


class ChannelLevelsEvent(StructEventBase):
    SIZE = 24
    PROPS = {"pan": "I", "volume": "I", "pitch_shift": "I", "_u12": 12}


class ChannelParametersEvent(StructEventBase):
    PROPS = {
        "_u40": 40,  # 40
        "arp.direction": "I",  # 44
        "arp.range": "I",  # 48
        "arp.chord": "I",  # 52
        "arp.time": "f",  # 56
        "arp.gate": "f",  # 60
        "arp.slide": "bool",  # 61
        "_u31": 31,  # 92
        "arp.repeat": "I",  # 96
    }


class ChannelPolyphonyEvent(StructEventBase):
    SIZE = 9
    PROPS = {"max": "I", "slide": "I", "flags": "B"}


class ChannelTrackingEvent(StructEventBase):
    SIZE = 16
    PROPS = {"middle_value": "i", "pan": "i", "mod_x": "i", "mod_y": "i"}


class InsertFlagsEvent(StructEventBase):
    SIZE = 12
    PROPS = {"_u1": "I", "flags": "I", "_u2": "I"}


class InsertParametersEventItem:
    SIZE = 12
    PROPS = {
        "_u4": 4,  # 4
        "index": "b",  # 5
        "_u1": 1,  # 6
        "channel_data": "H",  # 8
        "msg": "i",  # 12
    }


class PlaylistEventItem:
    SIZE = 32
    PROPS = {
        "position": "I",  # 4
        "pattern_base": "H",  # 6
        "item_index": "H",  # 8
        "length": "I",  # 12
        "track_index": "i",  # 16
        "_u2": 2,  # 18
        "item_flags": "H",  # 20
        "_u4": 4,  # 24
        "start_offset": "i",  # 28
        "end_offset": "i",  # 32
    }


class PatternContollerEventItem:
    SIZE = 12
    PROPS = {
        "position": "I",  # 4
        "_u1": 1,  # 5
        "_u2": 1,  # 6
        "channel": "B",  # 7
        "_flags": "B",  # 8
        "value": "f",  # 12
    }


class PatternNotesEventItem:
    SIZE = 24
    PROPS = {
        "position": "I",  # 4
        "flags": "H",  # 6
        "rack_channel": "H",  # 8
        "duration": "I",  # 12
        "key": "I",  # 16
        "fine_pitch": "b",  # 17
        "_u1": 1,  # 18
        "release": "B",  # 19
        "midi_channel": "B",  # 20
        "pan": "b",  # 21
        "velocity": "B",  # 22
        "mod_x": "B",  # 23
        "mod_y": "B",  # 24
    }


class TimestampEvent(StructEventBase):
    SIZE = 16
    PROPS = dict.fromkeys(("created_on", "work_time"), "d")


class TrackEvent(StructEventBase):
    PROPS = {
        "index": "I",  # 4
        "color": "i",  # 8
        "icon": "i",  # 12
        "enabled": "bool",  # 13
        "height": "f",  # 17
        "locked_height": "f",  # 21
        "locked_to_content": "bool",  # 22
        "motion": "I",  # 26
        "press": "I",  # 30
        "trigger_sync": "I",  # 34
        "queued": "I",  # 38
        "tolerant": "I",  # 42
        "position_sync": "I",  # 46
        "grouped": "bool",  # 47
        "locked": "bool",  # 48
    }


class RemoteControllerEvent(StructEventBase):
    SIZE = 20
    PROPS = {
        "_u1": 2,  # 2
        "_u2": 1,  # 3
        "_u3": 1,  # 4
        "parameter_data": "H",  # 6
        "destination_data": "h",  # 8
        "_u4": 8,  # 16
        "_u5": 4,  # 20
    }


class PluginEvent(StructEventBase):
    def __init__(self, data: bytes, truncate=True) -> None:
        super().__init__(DATA + 5, data, truncate)


class BooBassEvent(PluginEvent):
    SIZE = 16
    PROPS = dict.fromkeys(("_u1", "bass", "mid", "high"), "I")  # _u1 = [1, 0, 0, 0]


class FruityBalanceEvent(PluginEvent):
    SIZE = 8
    PROPS = {"pan": "I", "volume": "I"}


class FruityFastDistEvent(PluginEvent):
    SIZE = 20
    PROPS = dict.fromkeys(("pre", "threshold", "kind", "mix", "post"), "I")


class FruityNotebook2Event(PluginEvent):
    def __init__(self, data: bytes) -> None:
        super().__init__(data, False)
        self.props = {}
        pages = self.props["pages"] = {}

        self.stream.seek(4)
        self.props["active_page"] = self.stream.read_I()
        while True:
            page_num = self.stream.read_i()
            if page_num == -1:
                break

            strlen = self.stream.read_v() * 2
            raw = self.stream.read(strlen)
            page = raw.decode("utf-16-le")
            pages[page_num] = page
        self.props["editable"] = self.stream.read_bool()


class FruitySendEvent(PluginEvent):
    SIZE = 16
    PROPS = dict.fromkeys(("pan", "dry", "volume", "send_to"), "I")


class FruitySoftClipperEvent(PluginEvent):
    SIZE = 8
    PROPS = {"threshold": "I", "post": "I"}


class FruityStereoEnhancerEvent(PluginEvent):
    SIZE = 24
    PROPS = dict.fromkeys(
        (
            "pan",
            "volume",
            "stereo_separation",
            "phase_offset",
            "effect_position",
            "phase_inversion",
        ),
        "I",
    )


class SoundgoodizerEvent(PluginEvent):
    SIZE = 12
    PROPS = dict.fromkeys(("_u1", "mode", "amount"), "I")


@unique
class VSTPluginEventID(IntEnum):
    MIDI = 1
    Flags = 2
    IO = 30
    Inputs = 31
    Outputs = 32
    PluginInfo = 50
    FourCC = 51  # Not present for Waveshells
    GUID = 52
    State = 53
    Name = 54
    PluginPath = 55
    Vendor = 56
    _57 = 57  # TODO, not present for Waveshells


@unique
class EventID(IntEnum):
    """IDs used by events stored in an FLP-esque format.

    Event values are stored as a tuple of event ID and its designated type.
    The types are used to serialise/deserialise events by the parser.

    Event naming conventions:
    - Arr: `Arrangement`
    - Ch: `Channel`
    - Ins: `Insert`
    - Pat: `Pattern`
    - Plug: Event IDs shared by `Channel` and `InsertSlot`
    - Proj: `Project`
    - Slot: `InsertSlot`
    - TM: `TimeMarker`

    All event names prefixed with an underscore (_) are deprecated w.r.t to
    the latest version of FL Studio, *to the best of my knowledge*.
    """

    def __new__(cls, id, type=None):
        obj = int.__new__(cls, id)
        obj._value_ = id
        obj.type = type
        return obj

    # def __hash__(cls, id) -> int:
    #     return hash(cls(id).value)

    ChIsEnabled = (0, BoolEvent)
    _ChVolByte = (2, U8Event)
    _ChPanByte = (3, U8Event)
    ProjLoopActive = (9, BoolEvent)
    ProjShowInfo = (10, BoolEvent)
    ProjSwing = (11, U8Event)
    _ProjVolume = (12, U8Event)
    _ProjFitToSteps = (13, U8Event)
    ChZipped = (15, BoolEvent)
    ProjTimeSigNum = (17, U8Event)
    ProjTimeSigBeat = (18, U8Event)
    ChUsesLoopPoints = (19, BoolEvent)
    ChType = (21, U8Event)
    ChRoutedTo = (22, I8Event)
    ProjPanLaw = (23, U8Event)
    # ChFXProperties = 27
    ProjRegistered = (28, BoolEvent)
    ProjPlayTruncatedNotes = (30, BoolEvent)
    ChIsLocked = (32, BoolEvent)  # FL12.3+
    TMNumerator = (33, U8Event)
    TMDenominator = (34, U8Event)

    ChNew = (WORD, U16Event)
    PatNew = (WORD + 1, U16Event)  # Marks the beginning of a new pattern, twice.
    # _Tempo = WORD + 2
    ProjCurPatIdx = (WORD + 3, U16Event)
    # Fx = WORD + 5
    # FadeStereo = WORD + 6
    ChCutoff = (WORD + 7, U16Event)
    _ChVolWord = (WORD + 8, U16Event)
    _ChPanWord = (WORD + 9, U16Event)
    ChPreamp = (WORD + 10, U16Event)
    ChFadeOut = (WORD + 11, U16Event)
    ChFadeIn = (WORD + 12, U16Event)
    # DotNote = WORD + 13
    # DotPitch = WORD + 14
    # DotMix = WORD + 15
    ProjPitch = (WORD + 16, I16Event)
    ChResonance = (WORD + 19, U16Event)
    # _LoopBar = WORD + 20
    ChStereoDelay = (WORD + 21, U16Event)
    # Fx3 = WORD + 22
    # DotReso = WORD + 23
    # DotCutOff = WORD + 24
    # ShiftDelay = WORD + 25
    # _LoopEndBar = WORD + 26
    # Dot = WORD + 27
    # _TempoFine = WORD + 29
    # DotRel = WORD + 32
    # DotShift = WORD + 28
    ChChildren = (WORD + 30, U16Event)
    InsIcon = (WORD + 31, I16Event)
    ChSwing = (WORD + 33, U16Event)
    SlotIndex = (WORD + 34, U16Event)
    ArrNew = (WORD + 35, U16Event)

    PlugColor = (DWORD, ColorEvent)
    # _PlaylistItem = DWORD + 1
    # Echo = DWORD + 2
    # FxSine = DWORD + 3
    ChCutGroup = (DWORD + 4, U16TupleEvent)
    ChRootNote = (DWORD + 7, U32Event)
    # _MainResoCutOff = DWORD + 9
    # DelayModXY = DWORD + 10
    ChReverb = (DWORD + 11, U32Event)
    ChStretchTime = (DWORD + 12, F32Event)
    ChFineTune = (DWORD + 14, I32Event)
    ChSamplerFlags = (DWORD + 15, U32Event)
    ChLayerFlags = (DWORD + 16, U32Event)
    ChGroupNum = (DWORD + 17, I32Event)
    ProjCurGroupId = (DWORD + 18, I32Event)
    InsOutput = (DWORD + 19, I32Event)
    TMPosition = (DWORD + 20, U32Event)
    InsColor = (DWORD + 21, ColorEvent)
    PatColor = (DWORD + 22, ColorEvent)
    ProjLoopPos = (DWORD + 24, U32Event)
    ChAUSampleRate = (DWORD + 25, U32Event)
    InsInput = (DWORD + 26, I32Event)
    PlugIcon = (DWORD + 27, U32Event)
    ProjTempo = (DWORD + 28, U32Event)
    # _157 = DWORD + 29   # FL 12.5+
    # _158 = DWORD + 30   # default: -1
    ProjVerBuild = (DWORD + 31, U32Event)
    # _164 = DWORD + 36   # default: 0

    PatName = TEXT + 1
    ProjTitle = TEXT + 2
    ProjComments = TEXT + 3
    ChSamplePath = TEXT + 4
    ProjUrl = TEXT + 5
    _ProjRTFComments = TEXT + 6
    ProjFLVersion = (TEXT + 7, AsciiEvent)
    ProjRegisteredTo = TEXT + 8
    PlugDefaultName = TEXT + 9
    ProjDataPath = TEXT + 10
    PlugName = TEXT + 11
    InsName = TEXT + 12
    TMName = TEXT + 13
    ProjGenre = TEXT + 14
    ProjArtists = TEXT + 15
    GroupName = TEXT + 39
    TrackName = TEXT + 47
    ArrName = TEXT + 49

    ChDelay = (DATA + 1, ChannelDelayEvent)
    # Plugin wrapper data, windows pos of plugin etc, currently
    # selected plugin wrapper page; minimized, closed or not
    PlugWrapper = (DATA + 4, UnknownDataEvent)  # TODO
    PlugData = (DATA + 5, PluginEvent)
    ChParameters = (DATA + 7, ChannelParametersEvent)
    ChEnvelopeLFO = (DATA + 10, ChannelEnvelopeLFOEvent)
    ChLevels = (DATA + 11, ChannelLevelsEvent)
    # _ChFilter = DATA + 12
    ChPolyphony = (DATA + 13, ChannelPolyphonyEvent)
    PatControllers = (DATA + 15, DataArrayEvent)
    PatNotes = (DATA + 16, DataArrayEvent)
    InsParameters = (DATA + 17, DataArrayEvent)
    RemoteController = (DATA + 19, RemoteControllerEvent)
    ChTracking = (DATA + 20, ChannelTrackingEvent)
    ChLevelAdjusts = (DATA + 21, ChannelLevelAdjustsEvent)
    PlaylistData = (DATA + 25, DataArrayEvent)
    InsRouting = (DATA + 27, DataArrayEvent)
    InsFlags = (DATA + 28, InsertFlagsEvent)
    ProjTimestamp = (DATA + 29, TimestampEvent)
    TrackData = (DATA + 30, TrackEvent)
