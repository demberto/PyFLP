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
import warnings
from typing import Any, ClassVar, Dict, Generic, TypeVar

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, get_args, runtime_checkable
else:
    from typing_extensions import get_args, Literal, Protocol, runtime_checkable

import construct as c
import construct_typed as ct

from ._descriptors import FlagProp, RWProperty, StructProp
from ._events import (
    DATA,
    DWORD,
    TEXT,
    AnyEvent,
    ColorEvent,
    EventEnum,
    EventTree,
    FourByteBool,
    StdEnum,
    StructEventBase,
    T,
    U32Event,
)
from ._models import EventModel, ModelReprMixin

__all__ = [
    "BooBass",
    "FruityBalance",
    "FruityFastDist",
    "FruityNotebook2",
    "FruitySend",
    "FruitySoftClipper",
    "FruityStereoEnhancer",
    "PluginIOInfo",
    "Soundgoodizer",
    "VSTPlugin",
]


@enum.unique
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


class BooBassEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Bytes(4),
        "bass" / c.Int32ul,
        "mid" / c.Int32ul,
        "high" / c.Int32ul,
    ).compile()


class FruityBalanceEvent(StructEventBase):
    STRUCT = c.Struct("pan" / c.Int32ul, "volume" / c.Int32ul).compile()


class FruityCenterEvent(StructEventBase):
    STRUCT = c.Struct("_u1" / c.Bytes(4), "enabled" / FourByteBool).compile()


class FruityFastDistEvent(StructEventBase):
    STRUCT = c.Struct(
        "pre" / c.Int32ul,
        "threshold" / c.Int32ul,
        "kind" / c.Enum(c.Int32ul, A=0, B=1),
        "mix" / c.Int32ul,
        "post" / c.Int32ul,
    ).compile()


class FruityNotebook2Event(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Bytes(4),
        "active_page" / c.Int32ul,
        "pages"
        / c.GreedyRange(
            c.Struct(
                "index" / c.Int32sl,
                c.StopIf(lambda ctx: ctx["index"] == -1),
                "length" / c.VarInt,
                "value" / c.PaddedString(lambda ctx: ctx["length"] * 2, "utf-16-le"),
            ),
        ),
        "editable" / c.Flag,
    )


class FruitySendEvent(StructEventBase):
    STRUCT = c.Struct(
        "pan" / c.Int32sl,
        "dry" / c.Int32ul,
        "volume" / c.Int32ul,
        "send_to" / c.Int32sl,
    ).compile()


class FruitySoftClipperEvent(StructEventBase):
    STRUCT = c.Struct("threshold" / c.Int32ul, "post" / c.Int32ul).compile()


class FruityStereoEnhancerEvent(StructEventBase):
    STRUCT = c.Struct(
        "pan" / c.Int32sl,
        "volume" / c.Int32ul,
        "stereo_separation" / c.Int32ul,
        "phase_offset" / c.Int32ul,
        "effect_position" / c.Enum(c.Int32ul, pre=0, post=1),
        "phase_inversion" / c.Enum(c.Int32ul, none=0, left=1, right=2),
    ).compile()


class SoundgoodizerEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Bytes(4),
        "mode" / c.Enum(c.Int32ul, A=0, B=1, C=2, D=3),
        "amount" / c.Int32ul,
    ).compile()


class WrapperEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Bytes(16),  # 16
        "flags" / StdEnum[_WrapperFlags](c.Int16ul),  # 18
        "_u2" / c.Bytes(34),  # 52
    ).compile()


@enum.unique
class _VSTPluginEventID(ct.EnumBase):
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
    FourCC = (51, "fourcc")  # Not present for Waveshells & VST3
    GUID = (52, "guid")
    State = (53, "state")
    Name = (54, "name")
    PluginPath = (55, "plugin_path")
    Vendor = (56, "vendor")
    _57 = 57  # TODO, not present for Waveshells


class VSTPluginEvent(StructEventBase):
    STRUCT = c.Struct(
        "type" / c.Int32ul,  # * 8 or 10 for VSTs, but I am not forcing it
        "events"
        / c.GreedyRange(
            c.Struct(
                "id" / StdEnum[_VSTPluginEventID](c.Int32ul),
                # TODO Using a c.Select or c.IfThenElse doesn't work here
                # Check https://github.com/construct/construct/issues/993
                "data" / c.Prefixed(c.Int64ul, c.GreedyBytes),
            ),
        ),
    )

    def __init__(self, id: Any, data: bytearray):
        if data[0] not in (8, 10):
            warnings.warn(
                f"VSTPluginEvent: Unknown marker {data[0]} detected ."
                "Open an issue at https://github.com/demberto/PyFLP/issues "
                "if you are seeing this!",
                RuntimeWarning,
                stacklevel=0,
            )
        super().__init__(id, data)

    def __getitem__(self, key: str) -> str | bytes:
        for event in self._struct["events"]:
            if event["id"].key == key:
                if self._is_ascii_event(event["id"]):
                    return event["data"].decode("ascii")
                return event["data"]
        raise AttributeError(f"No event with key {key!r} found")

    def __setitem__(self, key: str, value: str | bytes):
        for event in self._struct["events"]:
            if self._is_ascii_event(event["id"]) and isinstance(value, str):
                try:
                    value.encode("ascii")
                except UnicodeEncodeError as exc:
                    raise ValueError("Strings must have only ASCII data") from exc

            if event["id"].key == key:
                event["size"] = len(value)
                event["data"] = value

        # Errors if any, will be raised here itself, so its
        # better not to override __bytes__ for this part
        self._data = self.STRUCT.build(self._struct)

    @staticmethod
    def _is_ascii_event(id: _VSTPluginEventID):
        return not getattr(id, "key").isdecimal()


@enum.unique
class PluginID(EventEnum):
    """IDs shared by :class:`pyflp.channel.Channel` and :class:`pyflp.mixer.Slot`."""

    Color = (DWORD, ColorEvent)
    Icon = (DWORD + 27, U32Event)
    InternalName = TEXT + 9
    Name = TEXT + 11  #: 3.3.0+ for :class:`pyflp.mixer.Slot`.
    # TODO Additional possible fields: Plugin wrapper data, window
    # positions of plugin, currently selected plugin wrapper page, etc.
    Wrapper = (DATA + 4, WrapperEvent)
    # * The type of this event is decided during event collection
    Data = DATA + 5  #: 1.6.5+


@runtime_checkable
class _IPlugin(Protocol):
    INTERNAL_NAME: ClassVar[str]
    """The name used internally by FL to decide the type of plugin data."""


_PE_co = TypeVar("_PE_co", bound=AnyEvent, covariant=True)


class _WrapperProp(FlagProp):
    def __init__(self, flag: _WrapperFlags, **kw: Any):
        super().__init__(flag, PluginID.Wrapper, **kw)


class _PluginBase(EventModel, Generic[_PE_co]):
    def __init__(self, events: EventTree, **kw: Any):
        super().__init__(events, **kw)

    compact = _WrapperProp(_WrapperFlags.HideSettings)
    """Whether plugin page toolbar is hidden or not.

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
    def __init__(self, *types: type[AnyPlugin]) -> None:
        self._types = types

    def __get__(self, ins: EventModel, owner: Any = None) -> AnyPlugin | None:
        if owner is None:
            return NotImplemented

        for ptype in self._types:
            if isinstance(ins.events.first(PluginID.Data), get_args(ptype)[0]):
                return ptype(
                    ins.events.subdict(
                        lambda e: e.id in (PluginID.Wrapper, PluginID.Data)
                    )
                )

    def __set__(self, instance: EventModel, value: AnyPlugin):
        if isinstance(value, _IPlugin):
            setattr(instance, "internal_name", value.INTERNAL_NAME)
        instance.events[PluginID.Data] = value.events[PluginID.Data]
        instance.events[PluginID.Wrapper] = value.events[PluginID.Wrapper]


class _PluginDataProp(StructProp[T]):
    def __init__(self, prop: str | None = None):
        super().__init__(PluginID.Data, prop=prop)


class PluginIOInfo(EventModel):
    mixer_offset = StructProp[int]()
    flags = StructProp[int]()


class VSTPlugin(_PluginBase[VSTPluginEvent], _IPlugin):
    """Represents a VST2 or a VST3 generator or effect.

    *New in FL Studio v1.5.23*: VST2 support (beta).
    *New in FL Studio v9.0.3*: VST3 support.
    """

    INTERNAL_NAME = "Fruity Wrapper"
    fourcc = _PluginDataProp[str]()
    """A unique four character code identifying the plugin.

    A database can be found on Steinberg's developer portal.
    """

    guid = _PluginDataProp[bytes]()  # See issue #8
    midi_in = _PluginDataProp[int]()
    """MIDI Input Port. Min: 0, Max: 255."""

    midi_out = _PluginDataProp[int]()
    """MIDI Output Port. Min: 0, Max: 255."""

    name = _PluginDataProp[str]()
    """Factory name of the plugin."""

    num_inputs = _PluginDataProp[int]()
    """Number of inputs the plugin supports."""

    num_outputs = _PluginDataProp[int]()
    """Number of outputs the plugin supports."""

    pitch_bend = _PluginDataProp[int]()
    """Pitch bend range sent to the plugin (in semitones)."""

    plugin_path = _PluginDataProp[str]()
    """The absolute path to the plugin binary."""

    state = _PluginDataProp[bytes]()
    """Plugin specific preset data blob."""

    vendor = _PluginDataProp[int]()
    """Plugin developer (vendor) name."""

    vst_number = _PluginDataProp[int]()  # TODO


class BooBass(_PluginBase[BooBassEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3Bk3aGK)"""

    INTERNAL_NAME = "BooBass"
    bass = _PluginDataProp[int]()
    """Volume of the bass region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """

    high = _PluginDataProp[int]()
    """Volume of the high region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """

    mid = _PluginDataProp[int]()
    """Volume of the mid region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """


class FruityBalance(_PluginBase[FruityBalanceEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3RWItqU)"""

    INTERNAL_NAME = "Fruity Balance"
    pan = _PluginDataProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    volume = _PluginDataProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


class FruityCenter(_PluginBase[FruityCenterEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3TA9IIv)"""

    INTERNAL_NAME = "Fruity Center"
    enabled = _PluginDataProp[bool]()
    """Removes DC offset if True; effectively behaving like a bypass button.

    Labelled as **Status** for some reason in the UI.
    """


class FruityFastDist(_PluginBase[FruityFastDistEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3qT6Jil)"""

    INTERNAL_NAME = "Fruity Fast Dist"
    kind = _PluginDataProp[Literal["A", "B"]]()
    mix = _PluginDataProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """

    post = _PluginDataProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """

    pre = _PluginDataProp[int]()
    """Linear.

    | Type    | Value | Percentage |
    |---------|-------|------------|
    | Min     | 64    | 33%        |
    | Max     | 192   | 100%       |
    | Default | 128   | 67%        |
    """

    threshold = _PluginDataProp[int]()
    """Linear, Stepped. Defaults to maximum value.

    | Type | Value | Percentage |
    |------|-------|------------|
    | Min  | 1     | 10%        |
    | Max  | 10    | 100%       |
    """


class FruityNotebook2(_PluginBase[FruityNotebook2Event], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3RHa4g5)"""

    INTERNAL_NAME = "Fruity NoteBook 2"
    active_page = _PluginDataProp[int]()
    """Active page number of the notebook. Min: 0, Max: 100."""

    editable = _PluginDataProp[bool]()
    """Whether the notebook is marked as editable or read-only.

    This attribute is just a visual marker used by FL Studio.
    """

    pages = _PluginDataProp[Dict[int, str]]()
    """A dict of page numbers to their contents."""


class FruitySend(_PluginBase[FruitySendEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3DqjvMu)"""

    INTERNAL_NAME = "Fruity Send"
    dry = _PluginDataProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 256   | 100%      |
    """

    pan = _PluginDataProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    send_to = _PluginDataProp[int]()
    """Target insert index; depends on insert routing. Defaults to -1 (Master)."""

    volume = _PluginDataProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


class FruitySoftClipper(_PluginBase[FruitySoftClipperEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3BCWfJX)"""

    INTERNAL_NAME = "Fruity Soft Clipper"
    post = _PluginDataProp[int]()
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 0     | 0%        |
    | Max     | 160   | 100%      |
    | Default | 128   | 80%       |
    """

    threshold = _PluginDataProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 1     | -INFdB / 0.00  |
    | Max     | 127   | 0.0dB / 1.00   |
    | Default | 100   | -4.4dB / 0.60  |
    """


class FruityStereoEnhancer(
    _PluginBase[FruityStereoEnhancerEvent], _IPlugin, ModelReprMixin
):
    """![](https://bit.ly/3DoHvji)"""

    INTERNAL_NAME = "Fruity Stereo Enhancer"
    effect_position = _PluginDataProp[Literal["pre", "post"]]()
    """Defaults to ``post``."""

    pan = _PluginDataProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    phase_inversion = _PluginDataProp[Literal["none", "left", "right"]]()
    """Default to ``None``."""

    phase_offset = _PluginDataProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -512  | 500ms L        |
    | Max     | 512   | 500ms R        |
    | Default | 0     | No offset      |
    """

    stereo_separation = _PluginDataProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -96   | 100% separated |
    | Max     | 96    | 100% merged    |
    | Default | 0     | No effect      |
    """

    volume = _PluginDataProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


class Soundgoodizer(_PluginBase[SoundgoodizerEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3dip70y)"""

    INTERNAL_NAME = "Soundgoodizer"
    amount = _PluginDataProp[int]()
    """Logarithmic.

    | Min | Max  | Default |
    |-----|------|---------|
    | 0   | 1000 | 600     |
    """

    mode = _PluginDataProp[Literal["A", "B", "C", "D"]]()
    """4 preset modes (A, B, C and D). Defaults to ``A``."""


def get_event_by_internal_name(name: str) -> type[StructEventBase] | None:
    for cls in _PluginBase.__subclasses__():
        if getattr(cls, "INTERNAL_NAME", None) == name:
            return cls.__orig_bases__[0].__args__[0]  # type: ignore
