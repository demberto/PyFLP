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

from __future__ import annotations

import enum
import sys
from typing import Any, ClassVar, Dict, Generic, TypeVar, cast

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable

from ._base import (
    DATA,
    DWORD,
    TEXT,
    AnyEvent,
    ColorEvent,
    DataEventBase,
    EventEnum,
    ModelReprMixin,
    SingleEventModel,
    StructBase,
    StructEventBase,
    StructProp,
    U32Event,
    U64DataEvent,
    UnknownDataEvent,
)


class BooBassStruct(StructBase):
    PROPS = dict.fromkeys(("_u1", "bass", "mid", "high"), "I")  # _u1 = [1, 0, 0, 0]


class FruityBalanceStruct(StructBase):
    PROPS = {"pan": "I", "volume": "I"}


class FruityFastDistStruct(StructBase):
    PROPS = dict.fromkeys(("pre", "threshold", "kind", "mix", "post"), "I")


class FruitySendStruct(StructBase):
    PROPS = dict.fromkeys(("pan", "dry", "volume", "send_to"), "I")


class FruitySoftClipperStruct(StructBase):
    PROPS = {"threshold": "I", "post": "I"}


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


class SoundgoodizerStruct(StructBase):
    PROPS = dict.fromkeys(("_u1", "mode", "amount"), "I")


class BooBassEvent(StructEventBase):
    STRUCT = BooBassStruct


class FruityBalanceEvent(StructEventBase):
    STRUCT = FruityBalanceStruct


class FruityFastDistEvent(StructEventBase):
    STRUCT = FruityFastDistStruct


class FruityNotebook2Event(DataEventBase):
    def __init__(self, id: int, data: bytes) -> None:
        super().__init__(id, data)
        self._props: dict[str, Any] = {}
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


class FruitySendEvent(StructEventBase):
    STRUCT = FruitySendStruct


class FruitySoftClipperEvent(StructEventBase):
    STRUCT = FruitySoftClipperStruct


class FruityStereoEnhancerEvent(StructEventBase):
    STRUCT = FruityStereoEnhancerStruct


class SoundgoodizerEvent(StructEventBase):
    STRUCT = SoundgoodizerStruct


@enum.unique
class VSTPluginEventID(enum.IntEnum):
    def __new__(cls, id: int, key: str | None = None):
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


# TODO Try implementing __getitem__ and __setitem__


class VSTPluginEvent(DataEventBase):
    VST_MARKERS = (8, 10)

    def __init__(self, id: int, data: bytes) -> None:
        super().__init__(id, data)
        self._events: list[U64DataEvent] = []
        self._props: dict[str | int, Any] = {}

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
    InternalName = TEXT + 9
    Name = TEXT + 11
    # Plugin wrapper data, windows pos of plugin etc, currently
    # selected plugin wrapper page; minimized, closed or not
    Wrapper = (DATA + 4, UnknownDataEvent)  # TODO
    Data = (DATA + 5, UnknownDataEvent)  # ? 1.6.5+


@runtime_checkable
class IPlugin(Protocol):
    INTERNAL_NAME: ClassVar[str]
    """The name used internally by FL to decide the type of plugin data."""


_PE_co = TypeVar("_PE_co", bound=AnyEvent, covariant=True)


class PluginBase(SingleEventModel, Generic[_PE_co]):
    def __init__(self, event: _PE_co, **kw: Any):
        super().__init__(event, **kw)


AnyPlugin = PluginBase[AnyEvent]  # TODO bind to IPlugin + PluginBase (both)


class PluginIOInfo(SingleEventModel):
    mixer_offset = StructProp[int]()
    flags = StructProp[int]()


class VSTPlugin(PluginBase[VSTPluginEvent], IPlugin):
    """Represents a VST2 or a VST3 generator or effect.

    *New in FL Studio v1.5.23*: VST2 support (beta).
    *New in FL Studio v9.0.3*: VST3 support.
    """

    INTERNAL_NAME = "Fruity Wrapper"
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
    """Factory name of the plugin."""

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


class BooBass(PluginBase[BooBassEvent], IPlugin, ModelReprMixin):
    INTERNAL_NAME = "BooBass"
    bass = StructProp[int]()
    """Volume of the bass region.

    | Type    | Value |
    | ------- | :---: |
    | Min     | 0     |
    | Max     | 65535 |
    | Default | 32767 |
    """

    high = StructProp[int]()
    """Volume of the high region.

    | Type    | Value |
    | ------- | :---: |
    | Min     | 0     |
    | Max     | 65535 |
    | Default | 32767 |
    """

    mid = StructProp[int]()
    """Volume of the mid region.

    | Type    | Value |
    | ------- | :---: |
    | Min     | 0     |
    | Max     | 65535 |
    | Default | 32767 |
    """


class FruityBalance(PluginBase[FruityBalanceEvent], IPlugin, ModelReprMixin):
    INTERNAL_NAME = "Fruity Balance"
    pan = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    volume = StructProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | 0     | 0.00 / -INFdB  |
    | Max     | 320   | 1.25 / 5.6dB   |
    | Default | 256   | 1.00 / 0.0dB   |
    """


@enum.unique
class FruityFastDistKind(enum.IntEnum):
    A = 0
    B = 1


class FruityFastDist(PluginBase[FruityFastDistEvent], IPlugin, ModelReprMixin):
    INTERNAL_NAME = "Fruity Fast Dist"
    kind = StructProp[FruityFastDistKind]()
    mix = StructProp[int]()
    """Linear. Defaults to maximum value.

    | Type    | Value | Mix (wet) |
    | ------- | :---: | --------- |
    | Min     | 0     | 0%        |
    | Max     | 128   | 100%      |
    """

    post = StructProp[int]()
    """Linear. Defaults to maximum value.

    | Type    | Value | Mix (wet) |
    | ------- | :---: | --------- |
    | Min     | 0     | 0%        |
    | Max     | 128   | 100%      |
    """

    pre = StructProp[int]()
    """Linear.

    | Type    | Value | Percentage |
    | ------- | :---: | ---------- |
    | Min     | 64    | 33%        |
    | Max     | 192   | 100%       |
    | Default | 128   | 67%        |
    """

    threshold = StructProp[int]()
    """Linear, Stepped. Defaults to maximum value.

    | Type    | Value | Percentage |
    | ------- | :---: | ---------- |
    | Min     | 1     | 10%        |
    | Max     | 10    | 100%       |
    """


class FruityNotebook2(PluginBase[FruityNotebook2Event], IPlugin, ModelReprMixin):
    INTERNAL_NAME = "Fruity NoteBook 2"
    active_page = StructProp[int]()
    """Active page number of the notebook. Min: 0, Max: 100."""

    editable = StructProp[bool]()
    """Whether the notebook is marked as editable or read-only.

    This attribute is just a visual marker used by FL Studio.
    """

    pages = StructProp[Dict[int, str]]()
    """A dict of page numbers to their contents."""


class FruitySend(PluginBase[FruitySendEvent], IPlugin, ModelReprMixin):
    INTERNAL_NAME = "Fruity Send"
    dry = StructProp[int]()
    """Linear. Defaults to maximum value.

    | Type    | Value | Mix (wet) |
    | ------- | :---: | --------- |
    | Min     | 0     | 0%        |
    | Max     | 256   | 100%      |
    """

    pan = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

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


class FruitySoftClipper(PluginBase[FruitySoftClipperEvent], IPlugin, ModelReprMixin):
    INTERNAL_NAME = "Fruity Soft Clipper"
    post = StructProp[int]()
    """Linear.

    | Type    | Value | Mix (wet) |
    | ------- | :---: | --------- |
    | Min     | 0     | 0%        |
    | Max     | 160   | 100%      |
    | Default | 128   | 80%       |
    """

    threshold = StructProp[int]()
    """Logarithmic.

    | Type     | Value | Representation |
    | -------- | :---: | :------------: |
    | Min      | 1     | -INFdB / 0.00  |
    | Max      | 127   | 0.0dB / 1.00   |
    | Default  | 100   | -4.4dB / 0.60  |
    """


@enum.unique
class SoundgoodizerMode(enum.IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3


class Soundgoodizer(PluginBase[SoundgoodizerEvent], IPlugin, ModelReprMixin):
    INTERNAL_NAME = "Soundgoodizer"
    amount = StructProp[int]()
    """Logarithmic.

    | Type    | Value |
    | ------- | :---: |
    | Min     | 0     |
    | Max     | 1000  |
    | Default | 600   |
    """

    mode = StructProp[SoundgoodizerMode]()
    """4 preset modes (A, B, C and D)."""


@enum.unique
class StereoEnhancerEffectPosition(enum.IntEnum):
    Pre = 0
    Post = 1


@enum.unique
class StereoEnhancerPhaseInversion(enum.IntEnum):
    None_ = 0
    Left = 1
    Right = 2


class FruityStereoEnhancer(
    PluginBase[FruityStereoEnhancerEvent], IPlugin, ModelReprMixin
):
    INTERNAL_NAME = "Fruity Stereo Enhancer"
    effect_position = StructProp[StereoEnhancerEffectPosition]()
    """Default: StereoEnhancerEffectPosition.Post."""

    pan = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    phase_inversion = StructProp[StereoEnhancerPhaseInversion]()
    """Default: StereoEnhancerPhaseInversion.None_."""

    phase_offset = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -512  | 500ms L        |
    | Max     | 512   | 500ms R        |
    | Default | 0     | No offset      |
    """

    stereo_separation = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    | ------- | :---: | -------------- |
    | Min     | -96   | 100% separated |
    | Max     | 96    | 100% merged    |
    | Default | 0     | No effect      |
    """

    volume = StructProp[int]()
    """Logarithmic.

    | Type     | Value | Representation |
    | -------- | :---: | :------------: |
    | Min      | 0     | -INFdB / 0.00  |
    | Max      | 320   | 5.6dB / 1.90   |
    | Default  | 256   | 0.0dB / 1.00   |
    """
