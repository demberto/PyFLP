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

"""Contains the types used by native and VST plugins."""

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
    FlagProp,
    ModelReprMixin,
    MultiEventModel,
    RWProperty,
    SingleEventModel,
    StructBase,
    StructEventBase,
    StructProp,
    U32Event,
    U64DataEvent,
    UnknownDataEvent,
)

__all__ = [
    "BooBass",
    "FruityBalance",
    "FruityFastDist",
    "FruityFastDistKind",
    "FruityNotebook2",
    "FruitySend",
    "FruitySoftClipper",
    "FruityStereoEnhancer",
    "PluginIOInfo",
    "Soundgoodizer",
    "VSTPlugin",
    "StereoEnhancerEffectPosition",
    "StereoEnhancerPhaseInversion",
    "SoundgoodizerMode",
]


class _BooBassStruct(StructBase):
    PROPS = dict.fromkeys(("_u1", "bass", "mid", "high"), "I")  # _u1 = [1, 0, 0, 0]


class _FruityBalanceStruct(StructBase):
    PROPS = {"pan": "I", "volume": "I"}


class _FruityFastDistStruct(StructBase):
    PROPS = dict.fromkeys(("pre", "threshold", "kind", "mix", "post"), "I")


class _FruitySendStruct(StructBase):
    PROPS = dict.fromkeys(("pan", "dry", "volume", "send_to"), "I")


class _FruitySoftClipperStruct(StructBase):
    PROPS = {"threshold": "I", "post": "I"}


class _FruityStereoEnhancerStruct(StructBase):
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


class _SoundgoodizerStruct(StructBase):
    PROPS = dict.fromkeys(("_u1", "mode", "amount"), "I")


class _WrapperStruct(StructBase):
    PROPS = {
        "_u16": 16,  # 16
        "flags": "H",  # 18
        "_u34": 34,  # 52
    }


class BooBassEvent(StructEventBase):
    STRUCT = _BooBassStruct


class FruityBalanceEvent(StructEventBase):
    STRUCT = _FruityBalanceStruct


class FruityFastDistEvent(StructEventBase):
    STRUCT = _FruityFastDistStruct


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
    STRUCT = _FruitySendStruct


class FruitySoftClipperEvent(StructEventBase):
    STRUCT = _FruitySoftClipperStruct


class FruityStereoEnhancerEvent(StructEventBase):
    STRUCT = _FruityStereoEnhancerStruct


class SoundgoodizerEvent(StructEventBase):
    STRUCT = _SoundgoodizerStruct


class WrapperEvent(StructEventBase):
    STRUCT = _WrapperStruct


@enum.unique
class _VSTPluginEventID(enum.IntEnum):
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


class _WrapperFlags(enum.IntFlag):
    Visible = 1 << 0
    _Disabled = 1 << 1
    Detached = 1 << 2
    Maximized = 1 << 3
    Generator = 1 << 4
    SmartDisable = 1 << 5
    ThreadedProcessing = 1 << 6
    DemoMode = 1 << 7  # saved with a demo version
    HideSettings = 1 << 8
    Captionized = 1 << 9  # TODO find meaning
    _DirectX = 1 << 16  # indicates the plugin is a DirectX plugin
    _EditorSize = 2 << 16


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
                    _VSTPluginEventID.FourCC,
                    _VSTPluginEventID.Name,
                    _VSTPluginEventID.PluginPath,
                    _VSTPluginEventID.Vendor,
                ):
                    isascii = True
                subevent = U64DataEvent(subid, subdata, isascii)
                subkey = getattr(_VSTPluginEventID(subid), "key") or subid
                self._props[subkey] = subdata
                self._events.append(subevent)

    def __bytes__(self) -> bytes:
        self._stream.seek(0)
        for event in self._events:
            try:
                key = getattr(_VSTPluginEventID(event.id), "key")
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
    Name = TEXT + 11  #: 3.3.0+ for :class:`pyflp.mixer.Slot`.
    # Plugin wrapper data, windows pos of plugin etc, currently
    # selected plugin wrapper page; minimized, closed or not
    Wrapper = (DATA + 4, WrapperEvent)
    Data = (DATA + 5, UnknownDataEvent)  #: 1.6.5+


@runtime_checkable
class _IPlugin(Protocol):
    INTERNAL_NAME: ClassVar[str]
    """The name used internally by FL to decide the type of plugin data."""


_PE_co = TypeVar("_PE_co", bound=AnyEvent, covariant=True)


class _WrapperProp(FlagProp):
    def __init__(self, flag: _WrapperFlags):
        super().__init__(flag, PluginID.Wrapper)


class _PluginBase(MultiEventModel, Generic[_PE_co]):
    def __init__(self, *events: WrapperEvent | _PE_co, **kw: Any):
        super().__init__(*events, **kw)

    compact = _WrapperProp(_WrapperFlags.HideSettings)
    """Whether plugin page toolbar is hidden or not.

    .. image:: img/plugin/toolbar_collapse.gif

    ![](https://bit.ly/3qzOMoO)
    """

    demo_mode = _WrapperProp(_WrapperFlags.DemoMode)
    """Whether the plugin state was saved in a demo / trial version of the plugin."""

    detached = _WrapperProp(_WrapperFlags.Detached)
    disabled = _WrapperProp(_WrapperFlags._Disabled)
    directx = _WrapperProp(_WrapperFlags._DirectX)
    """Whether the plugin is a DirectX plugin or not."""

    generator = _WrapperProp(_WrapperFlags.Generator)
    """Whether the plugin is a generator or an effect."""

    maximized = _WrapperProp(_WrapperFlags.Maximized)
    """Whether the plugin editor is maximized or minimized.

    .. image:: img/plugin/maximize.gif

    ![](https://bit.ly/3QDMWO3)
    """

    multithreaded = _WrapperProp(_WrapperFlags.ThreadedProcessing)
    """Whether threaded processing is enabled or not."""

    smart_disable = _WrapperProp(_WrapperFlags.SmartDisable)
    """Whether smart disable is enabled or not."""

    visible = _WrapperProp(_WrapperFlags.Visible)
    """Whether the editor of the plugin is visible or closed."""


AnyPlugin = _PluginBase[AnyEvent]  # TODO alias to _IPlugin + _PluginBase (both)


class PluginProp(RWProperty[AnyPlugin]):
    def __init__(self, types: dict[type[AnyEvent], type[AnyPlugin]]) -> None:
        self._types = types

    def __get__(self, instance: MultiEventModel, owner: Any = None) -> AnyPlugin | None:
        if owner is None:
            return NotImplemented

        try:
            wrapper = cast(WrapperEvent, instance._events[PluginID.Wrapper][0])
            params = instance._events[PluginID.Data][0]
        except (KeyError, IndexError):
            return

        for etype, ptype in self._types.items():
            if isinstance(params, etype):
                return ptype(params, wrapper)

    def __set__(self, instance: MultiEventModel, value: AnyPlugin):
        if isinstance(value, _IPlugin):
            self.internal_name = value.INTERNAL_NAME
        events = value.events_asdict()
        instance._events[PluginID.Data] = events[PluginID.Data]
        instance._events[PluginID.Wrapper] = events[PluginID.Wrapper]


class PluginIOInfo(SingleEventModel):
    mixer_offset = StructProp[int]()
    flags = StructProp[int]()


class VSTPlugin(_PluginBase[VSTPluginEvent], _IPlugin):
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
    """Pitch bend range sent to the plugin (in semitones)."""

    plugin_path = StructProp[str]()
    """The absolute path to the plugin binary."""

    state = StructProp[bytes]()
    """Plugin specific preset data blob."""

    vendor = StructProp[int]()
    """Plugin developer (vendor) name."""

    vst_number = StructProp[int]()  # TODO


class BooBass(_PluginBase[BooBassEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3Bk3aGK)"""  # noqa

    INTERNAL_NAME = "BooBass"
    bass = StructProp[int]()
    """Volume of the bass region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """

    high = StructProp[int]()
    """Volume of the high region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """

    mid = StructProp[int]()
    """Volume of the mid region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """


class FruityBalance(_PluginBase[FruityBalanceEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3RWItqU)"""  # noqa

    INTERNAL_NAME = "Fruity Balance"
    pan = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    volume = StructProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


@enum.unique
class FruityFastDistKind(enum.IntEnum):
    """Used by :attr:`FruityFastDist.kind`."""

    A = 0
    B = 1


class FruityFastDist(_PluginBase[FruityFastDistEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3qT6Jil)"""  # noqa

    INTERNAL_NAME = "Fruity Fast Dist"
    kind = StructProp[FruityFastDistKind]()
    mix = StructProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """

    post = StructProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """

    pre = StructProp[int]()
    """Linear.

    | Type    | Value | Percentage |
    |---------|-------|------------|
    | Min     | 64    | 33%        |
    | Max     | 192   | 100%       |
    | Default | 128   | 67%        |
    """

    threshold = StructProp[int]()
    """Linear, Stepped. Defaults to maximum value.

    | Type | Value | Percentage |
    |------|-------|------------|
    | Min  | 1     | 10%        |
    | Max  | 10    | 100%       |
    """


class FruityNotebook2(_PluginBase[FruityNotebook2Event], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3RHa4g5)"""  # noqa

    INTERNAL_NAME = "Fruity NoteBook 2"
    active_page = StructProp[int]()
    """Active page number of the notebook. Min: 0, Max: 100."""

    editable = StructProp[bool]()
    """Whether the notebook is marked as editable or read-only.

    This attribute is just a visual marker used by FL Studio.
    """

    pages = StructProp[Dict[int, str]]()
    """A dict of page numbers to their contents."""


class FruitySend(_PluginBase[FruitySendEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3DqjvMu)"""  # noqa

    INTERNAL_NAME = "Fruity Send"
    dry = StructProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 256   | 100%      |
    """

    pan = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    send_to = StructProp[int]()
    """Target insert index; depends on insert routing. Defaults to -1 (Master)."""

    volume = StructProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


class FruitySoftClipper(_PluginBase[FruitySoftClipperEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3BCWfJX)"""  # noqa

    INTERNAL_NAME = "Fruity Soft Clipper"
    post = StructProp[int]()
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 0     | 0%        |
    | Max     | 160   | 100%      |
    | Default | 128   | 80%       |
    """

    threshold = StructProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 1     | -INFdB / 0.00  |
    | Max     | 127   | 0.0dB / 1.00   |
    | Default | 100   | -4.4dB / 0.60  |
    """


@enum.unique
class StereoEnhancerEffectPosition(enum.IntEnum):
    """Used by :attr:`FruityStereoEnhancer.effect_position`."""

    Pre = 0
    Post = 1


@enum.unique
class StereoEnhancerPhaseInversion(enum.IntEnum):
    """Used by :attr:`FruityStereoEnhancer.phase_inversion`."""

    None_ = 0
    Left = 1
    Right = 2


class FruityStereoEnhancer(
    _PluginBase[FruityStereoEnhancerEvent], _IPlugin, ModelReprMixin
):
    """![](https://bit.ly/3DoHvji)"""  # noqa

    INTERNAL_NAME = "Fruity Stereo Enhancer"
    effect_position = StructProp[StereoEnhancerEffectPosition]()
    """Defaults to :attr:`StereoEnhancerEffectPosition.Post`."""

    pan = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    phase_inversion = StructProp[StereoEnhancerPhaseInversion]()
    """Default to :attr:`~StereoEnhancerPhaseInversion.None_`."""

    phase_offset = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -512  | 500ms L        |
    | Max     | 512   | 500ms R        |
    | Default | 0     | No offset      |
    """

    stereo_separation = StructProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -96   | 100% separated |
    | Max     | 96    | 100% merged    |
    | Default | 0     | No effect      |
    """

    volume = StructProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


@enum.unique
class SoundgoodizerMode(enum.IntEnum):
    """Used by :attr:`Soundgoodizer.mode`."""

    A = 0
    B = 1
    C = 2
    D = 3


class Soundgoodizer(_PluginBase[SoundgoodizerEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3dip70y)"""  # noqa

    INTERNAL_NAME = "Soundgoodizer"
    amount = StructProp[int]()
    """Logarithmic.

    | Min | Max  | Default |
    |-----|------|---------|
    | 0   | 1000 | 600     |
    """

    mode = StructProp[SoundgoodizerMode]()
    """4 preset modes (A, B, C and D)."""
