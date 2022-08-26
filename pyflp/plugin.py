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

"""
pyflp.plugin
============

Contains the types used by native and VST plugins.
"""

import enum
import sys
from typing import Any, ClassVar, Dict, List, Optional, Union, cast

if sys.version_info >= (3, 8):
    from typing import Protocol, final, runtime_checkable
else:
    from typing_extensions import final, Protocol, runtime_checkable

from ._base import (
    DATA,
    DWORD,
    TEXT,
    ColorEvent,
    DataEventBase,
    EventEnum,
    ModelReprMixin,
    MultiEventModel,
    SingleEventModel,
    StructBase,
    StructEventBase,
    StructProp,
    U32Event,
    U64DataEvent,
    UnknownDataEvent,
)


@final
class BooBassStruct(StructBase):
    PROPS = dict.fromkeys(("_u1", "bass", "mid", "high"), "I")  # _u1 = [1, 0, 0, 0]


@final
class FruityBalanceStruct(StructBase):
    PROPS = {"pan": "I", "volume": "I"}


@final
class FruityFastDistStruct(StructBase):
    PROPS = dict.fromkeys(("pre", "threshold", "kind", "mix", "post"), "I")


@final
class FruitySendStruct(StructBase):
    PROPS = dict.fromkeys(("pan", "dry", "volume", "send_to"), "I")


@final
class FruitySoftClipperStruct(StructBase):
    PROPS = {"threshold": "I", "post": "I"}


@final
class FruityStereoEnhancerStruct(StructBase):
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


@final
class SoundgoodizerStruct(StructBase):
    PROPS = dict.fromkeys(("_u1", "mode", "amount"), "I")


@final
class BooBassEvent(StructEventBase):
    STRUCT = BooBassStruct


@final
class FruityBalanceEvent(StructEventBase):
    STRUCT = FruityBalanceStruct


@final
class FruityFastDistEvent(StructEventBase):
    STRUCT = FruityFastDistStruct


@final
class FruityNotebook2Event(DataEventBase):
    def __init__(self, id: int, data: bytes) -> None:
        super().__init__(id, data)
        self._props: Dict[str, Any] = {}
        pages = self._props["pages"] = {}

        self._stream.seek(4)
        self._props["active_page"] = self._stream.read_I()
        while True:
            page_num = self._stream.read_i()
            if page_num == -1:
                break

            num_chars = self._stream.read_v()
            if num_chars is None:
                break

            num_bytes = num_chars * 2
            raw = self._stream.read(num_bytes)
            page = raw.decode("utf-16-le")
            pages[page_num] = page
        self._props["editable"] = self._stream.read_bool()


@final
class FruitySendEvent(StructEventBase):
    STRUCT = FruitySendStruct


@final
class FruitySoftClipperEvent(StructEventBase):
    STRUCT = FruitySoftClipperStruct


@final
class FruityStereoEnhancerEvent(StructEventBase):
    STRUCT = FruityStereoEnhancerStruct


@final
class SoundgoodizerEvent(StructEventBase):
    STRUCT = SoundgoodizerStruct


@enum.unique
class VSTPluginEventID(enum.IntEnum):
    def __new__(cls, id: int, key: Optional[str] = None):
        obj = int.__new__(cls, id)
        obj._value_ = id
        setattr(obj, "key", key)
        return obj

    MIDI = 1
    Flags = 2
    IO = 30
    Inputs = 31
    Outputs = 32
    PluginInfo = 50
    FourCC = (51, "fourcc")  # Not present for Waveshells
    GUID = (52, "guid")
    State = (53, "state")
    Name = (54, "name")
    PluginPath = (55, "plugin_path")
    Vendor = (56, "vendor")
    _57 = 57  # TODO, not present for Waveshells


@final
class VSTPluginEvent(DataEventBase):
    VST_MARKERS = (8, 10)

    def __init__(self, id: int, data: bytes) -> None:
        super().__init__(id, data)
        self._events: List[U64DataEvent] = []
        self._props: Dict[Union[str, int], Any] = {}

        kind = self._props["kind"] = self._stream.read_I()
        if kind in VSTPluginEvent.VST_MARKERS:
            while self._stream.tell() < self._stream_len:
                subid = cast(int, self._stream.read_I())
                length = cast(int, self._stream.read_Q())
                subdata = self._stream.read(length)

                isascii = False
                if subid in (
                    VSTPluginEventID.FourCC,
                    VSTPluginEventID.Name,
                    VSTPluginEventID.PluginPath,
                    VSTPluginEventID.Vendor,
                ):
                    isascii = True
                subevent = U64DataEvent(subid, subdata, isascii)
                subkey = getattr(VSTPluginEventID(subid), "key") or subid
                self._props[subkey] = subdata
                self._events.append(subevent)

    def __bytes__(self) -> bytes:
        self._stream.seek(0)
        for event in self._events:
            try:
                key = getattr(VSTPluginEventID(event.id), "key")
            except ValueError:
                key = event.id
            event.value = self._props[key]
            self._stream.write(bytes(event))
        return super().__bytes__()


@enum.unique
class PluginID(EventEnum):
    """Event IDs shared by `Channel` and `Slot`."""

    Color = (DWORD, ColorEvent)
    Icon = (DWORD + 27, U32Event)
    DefaultName = TEXT + 9
    Name = TEXT + 11
    # Plugin wrapper data, windows pos of plugin etc, currently
    # selected plugin wrapper page; minimized, closed or not
    Wrapper = (DATA + 4, UnknownDataEvent)  # TODO
    Data = (DATA + 5, UnknownDataEvent)


@runtime_checkable
class IPlugin(Protocol):
    DEFAULT_NAME: ClassVar[str]


@final
class PluginIOInfo(MultiEventModel):
    mixer_offset = StructProp[int]()
    flags = StructProp[int]()


@final
class VSTPlugin(SingleEventModel, IPlugin):
    DEFAULT_NAME = "Fruity Wrapper"
    fourcc = StructProp[str]()
    """A unique four character code identifying the plugin.

    A database can be found on Steinberg's developer portal.
    """

    guid = StructProp[bytes]()  # See issue #8
    midi_in = StructProp[int]()
    """MIDI Input Port. Min: 0, Max: 255."""

    midi_out = StructProp[int]()
    """MIDI Output Port. Min: 0, Max: 255."""

    name = StructProp[str]()
    """Name of the plugin."""

    num_inputs = StructProp[int]()
    """Number of inputs the plugin supports."""

    num_outputs = StructProp[int]()
    """Number of outputs the plugin supports."""

    pitch_bend = StructProp[int]()
    """Pitch bend range (in semitones)."""

    plugin_path = StructProp[str]()
    """The absolute path to the plugin binary."""

    state = StructProp[bytes]()
    """Plugin specific preset data blob."""

    vendor = StructProp[int]()
    """Plugin developer (vendor) name."""

    vst_number = StructProp[int]()  # TODO


@final
class BooBass(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "BooBass"
    bass = StructProp[int]()
    """Min: 0, Max: 65535, Default: 32767."""

    high = StructProp[int]()
    """Min: 0, Max: 65535, Default: 32767."""

    mid = StructProp[int]()
    """Min: 0, Max: 65535, Default: 32767."""


@final
class FruityBalance(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "Fruity Balance"
    pan = StructProp[int]()
    """Min: -128, Max: 127, Default: 0 (0.50, Centred). Linear."""

    volume = StructProp[int]()
    """Min: 0, Max: 320, Default: 256 (0.80, 0dB). Logarithmic."""


@enum.unique
class FruityFastDistKind(enum.IntEnum):
    A = 0
    B = 1


@final
class FruityFastDist(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "Fruity Fast Dist"
    kind = StructProp[FruityFastDistKind]()
    mix = StructProp[int]()
    """Min: 0 (0%), Max: 128 (100%), Default: 128 (100%). Linear."""

    post = StructProp[int]()
    """Min: 0 (0%), Max: 128 (100%), Default: 128 (100%). Linear."""

    pre = StructProp[int]()
    """Min: 64 (33%), Max: 192 (100%), Default: 128 (67%). Linear."""

    threshold = StructProp[int]()
    """Min: 1 (10%), Max: 10 (100%), Default: 10 (100%). Linear. Stepped."""


@final
class FruityNotebook2(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "Fruity NoteBook 2"
    active_page = StructProp[int]()
    """Active page number of the notebook. Min: 0, Max: 100."""

    editable = StructProp[bool]()
    """Whether the notebook is marked as editable or read-only.

    This attribute is just a visual marker used by FL Studio.
    """

    pages = StructProp[Dict[int, str]]()
    """A dict of page numbers to their contents."""


@final
class FruitySend(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "Fruity Send"
    dry = StructProp[int]()
    """Min: 0 (0%), Max: 256 (100%), Default: 256 (100%). Linear."""

    pan = StructProp[int]()
    """Min: -128 (100% left), Max: 127 (100% right), Default: 0 (Centred). Linear."""

    send_to = StructProp[int]()
    """Target insert index; depends on insert routing. Default: -1 (Master)."""

    volume = StructProp[int]()
    """Logarithmic.

    | Type     | Value | Representation |
    | -------- | :---: | :------------: |
    | Min      | 0     | -INFdB / 0.00  |
    | Max      | 320   | 5.6dB / 1.90   |
    | Default  | 256   | 0.0dB / 1.00   |
    """


@final
class FruitySoftClipper(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "Fruity Soft Clipper"
    post = StructProp[int]()
    """Min: 0, Max: 160, Default: 128 (80%). Linear."""

    threshold = StructProp[int]()
    """Min: 1, Max: 127, Default: 100 (0.60, -4.4dB). Logarithmic."""


@enum.unique
class SoundgoodizerMode(enum.IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3


@final
class Soundgoodizer(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "Soundgoodizer"
    amount = StructProp[int]()
    """Min: 0, Max: 1000, Default: 600. Logarithmic."""

    mode = StructProp[SoundgoodizerMode]()


@enum.unique
class StereoEnhancerEffectPosition(enum.IntEnum):
    Pre = 0
    Post = 1


@enum.unique
class StereoEnhancerPhaseInversion(enum.IntEnum):
    None_ = 0
    Left = 1
    Right = 2


@final
class FruityStereoEnhancer(MultiEventModel, IPlugin, ModelReprMixin):
    DEFAULT_NAME = "Fruity Stereo Enhancer"

    effect_position = StructProp[StereoEnhancerEffectPosition]()
    """Default: StereoEnhancerEffectPosition.Post."""

    pan = StructProp[int]()
    """Min: -128, Max: 127, Default: 0 (0.50, Centred). Linear."""

    phase_inversion = StructProp[StereoEnhancerPhaseInversion]()
    """Default: StereoEnhancerPhaseInversion.None_."""

    phase_offset = StructProp[int]()
    """Min: -512 (500ms L), Max: 512 (500ms R), Default: 0 (no offset). Linear."""

    stereo_separation = StructProp[int]()
    """Min: -96 (100% separation), Max: 96 (100% merged), Default: 0. Linear."""

    volume = StructProp[int]()
    """Min: 0, Max: 320, Default: 256 (0.80, 0dB). Logarithmic."""
