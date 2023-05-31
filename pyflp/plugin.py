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

"""Contains the types used by native and VST plugins to store their preset data."""

from __future__ import annotations

import enum
import warnings
from typing import Any, ClassVar, Dict, Generic, Literal, Protocol, TypeVar, cast, runtime_checkable

import construct as c
import construct_typed as ct

from pyflp._adapters import FourByteBool, StdEnum
from pyflp._descriptors import FlagProp, NamedPropMixin, RWProperty, StructProp
from pyflp._events import (
    DATA,
    DWORD,
    TEXT,
    AnyEvent,
    ColorEvent,
    EventEnum,
    EventTree,
    StructEventBase,
    U32Event,
    UnknownDataEvent,
)
from pyflp._models import EventModel, ModelReprMixin
from pyflp.types import T

__all__ = [
    "BooBass",
    "FruitKick",
    "FruityBalance",
    "FruityBloodOverdrive",
    "FruityFastDist",
    "FruityNotebook2",
    "FruitySend",
    "FruitySoftClipper",
    "FruityStereoEnhancer",
    "Plucked",
    "PluginID",
    "PluginIOInfo",
    "Soundgoodizer",
    "VSTPlugin",
]


@enum.unique
class _WrapperFlags(enum.IntFlag):
    Visible = 1 << 0
    _Disabled = 1 << 1
    Detached = 1 << 2
    # _U3 = 1 << 3
    Generator = 1 << 4
    SmartDisable = 1 << 5
    ThreadedProcessing = 1 << 6
    DemoMode = 1 << 7  # saved with a demo version
    HideSettings = 1 << 8
    Minimized = 1 << 9
    _DirectX = 1 << 16  # indicates the plugin is a DirectX plugin
    _EditorSize = 2 << 16


class BooBassEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.If(c.this._.len == 16, c.Bytes(4)),
        "bass" / c.Int32ul,
        "mid" / c.Int32ul,
        "high" / c.Int32ul,
    ).compile()


class FruitKickEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Bytes(4),
        "max_freq" / c.Int32sl,
        "min_freq" / c.Int32sl,
        "freq_decay" / c.Int32ul,
        "amp_decay" / c.Int32ul,
        "click" / c.Int32ul,
        "distortion" / c.Int32ul,
        "_u2" / c.Bytes(4),
    ).compile()


class FruityBalanceEvent(StructEventBase):
    STRUCT = c.Struct("pan" / c.Int32ul, "volume" / c.Int32ul).compile()


class FruityBloodOverdriveEvent(StructEventBase):
    STRUCT = c.Struct(
        "plugin_marker" / c.If(c.this._.len == 36, c.Bytes(4)),  # redesigned native plugin marker
        "pre_band" / c.Int32ul,
        "color" / c.Int32ul,
        "pre_amp" / c.Int32ul,
        "x100" / FourByteBool,
        "post_filter" / c.Int32ul,
        "post_gain" / c.Int32ul,
        "_u1" / c.Bytes(4),
        "_u2" / c.Bytes(4),
    ).compile()


class FruityCenterEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.If(c.this._.len == 8, c.Bytes(4)), "enabled" / FourByteBool
    ).compile()


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


class PluckedEvent(StructEventBase):
    STRUCT = c.Struct(
        "decay" / c.Int32ul,
        "color" / c.Int32ul,
        "normalize" / FourByteBool,
        "gate" / FourByteBool,
        "widen" / FourByteBool,
    ).compile()


class SoundgoodizerEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.If(c.this._.len == 12, c.Bytes(4)),
        "mode" / c.Enum(c.Int32ul, A=0, B=1, C=2, D=3),
        "amount" / c.Int32ul,
    ).compile()


NativePluginEvent = UnknownDataEvent
"""Placeholder event type for unimplemented native :attr:`PluginID.Data` events."""


class WrapperPage(ct.EnumBase):
    Editor = 0
    """:guilabel:`Plugin editor`."""

    Settings = 1
    """:guilabel:`VST wrapper settings`."""

    Sample = 3
    """:guilabel:`Sample settings`."""

    Envelope = 4
    """:guilabel:`Envelope / instrument settings`."""

    Miscellaneous = 5
    """:guilabel:`Miscallenous functions`."""


class WrapperEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Optional(c.Bytes(16)),  # 16
        "flags" / c.Optional(StdEnum[_WrapperFlags](c.Int16ul)),  # 18
        "_u2" / c.Optional(c.Bytes(2)),  # 20
        "page" / c.Optional(StdEnum[WrapperPage](c.Int8ul)),  # 21
        "_u3" / c.Optional(c.Bytes(23)),  # 44
        "width" / c.Optional(c.Int32ul),  # 48
        "height" / c.Optional(c.Int32ul),  # 52
        "_extra" / c.GreedyBytes,  # None as of 20.9.2
    ).compile()


@enum.unique
class _VSTPluginEventID(ct.EnumBase):
    MIDI = 1
    Flags = 2
    IO = 30
    Inputs = 31
    Outputs = 32
    PluginInfo = 50
    FourCC = 51  # Not present for Waveshells & VST3
    GUID = 52
    State = 53
    Name = 54
    PluginPath = 55
    Vendor = 56
    _57 = 57  # TODO, not present for Waveshells


class _VSTFlags(enum.IntFlag):
    SendPBRange = 1 << 0
    FixedSizeBuffers = 1 << 1
    NotifyRender = 1 << 2
    ProcessInactive = 1 << 3
    DontSendRelVelo = 1 << 5
    DontNotifyChanges = 1 << 6
    SendLoopPos = 1 << 11
    AllowThreaded = 1 << 12
    KeepFocus = 1 << 15
    DontKeepCPUState = 1 << 16
    SendModX = 1 << 17
    LoadBridged = 1 << 18
    ExternalWindow = 1 << 21
    UpdateWhenHidden = 1 << 23
    DontResetOnTransport = 1 << 25
    DPIAwareBridged = 1 << 26
    AcceptFileDrop = 1 << 28
    AllowSmartDisable = 1 << 29
    ScaleEditor = 1 << 30
    DontUseTimeOffset = 1 << 31


class _VSTFlags2(enum.IntFlag):
    ProcessMaxSize = 1 << 0
    UseMaxFromHost = 1 << 1


class VSTPluginEvent(StructEventBase):
    _MIDIStruct = c.Struct(
        "input" / c.Optional(c.Int32sl),  # 4
        "output" / c.Optional(c.Int32sl),  # 8
        "pb_range" / c.Optional(c.Int32ul),  # 12
        "_extra" / c.GreedyBytes,  # upto 20
    ).compile()

    _FlagsStruct = c.Struct(
        "_u1" / c.Optional(c.Bytes(9)),  # 9
        "flags" / c.Optional(StdEnum[_VSTFlags](c.Int32ul)),  # 13
        "flags2" / c.Optional(StdEnum[_VSTFlags2](c.Int32ul)),  # 17
        "_u2" / c.Optional(c.Bytes(5)),  # 22
        "fast_idle" / c.Optional(c.Flag),  # 23
        "_extra" / c.GreedyBytes,
    ).compile()

    STRUCT = c.Struct(
        "type" / c.Int32ul,  # * 8 or 10 for VSTs, but I am not forcing it
        "events"
        / c.GreedyRange(
            c.Struct(
                "id" / StdEnum[_VSTPluginEventID](c.Int32ul),
                # ! Using a c.Select or c.IfThenElse doesn't work here
                # Check https://github.com/construct/construct/issues/993
                "data"  # pyright: ignore
                / c.Prefixed(
                    c.Int64ul,
                    c.Switch(
                        c.this["id"],
                        {
                            _VSTPluginEventID.MIDI: _MIDIStruct,
                            _VSTPluginEventID.Flags: _FlagsStruct,
                            _VSTPluginEventID.FourCC: c.GreedyString("utf8"),
                            _VSTPluginEventID.Name: c.GreedyString("utf8"),  # See #150
                            _VSTPluginEventID.Vendor: c.GreedyString("utf8"),
                            _VSTPluginEventID.PluginPath: c.GreedyString("utf8"),
                        },
                        default=c.GreedyBytes,
                    ),
                ),
            ),
        ),
    ).compile()

    def __init__(self, id: Any, data: bytearray) -> None:
        if data[0] not in (8, 10):
            warnings.warn(
                f"VSTPluginEvent: Unknown marker {data[0]} detected. "
                "Open an issue at https://github.com/demberto/PyFLP/issues "
                "if you are seeing this!",
                RuntimeWarning,
                stacklevel=3,
            )
        super().__init__(id, data)


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
    def __init__(self, flag: _WrapperFlags, **kw: Any) -> None:
        super().__init__(flag, PluginID.Wrapper, **kw)


class _PluginBase(EventModel, Generic[_PE_co]):
    def __init__(self, events: EventTree, **kw: Any) -> None:
        super().__init__(events, **kw)

    compact = _WrapperProp(_WrapperFlags.HideSettings)
    """Whether plugin page toolbar (:guilabel:`Detailed settings`) is hidden.

    ![](https://bit.ly/3qzOMoO)
    """

    demo_mode = _WrapperProp(_WrapperFlags.DemoMode)  # TODO Verify if this works
    """Whether the plugin state was saved in a demo / trial version."""

    detached = _WrapperProp(_WrapperFlags.Detached)
    """Plugin editor can be moved between different monitors when detached."""

    disabled = _WrapperProp(_WrapperFlags._Disabled)
    """This is a legacy property; DON'T use it.

    Check :attr:`Channel.enabled` or :attr:`Slot.enabled` instead.
    """

    directx = _WrapperProp(_WrapperFlags._DirectX)
    """Whether the plugin is a DirectX plugin or not."""

    generator = _WrapperProp(_WrapperFlags.Generator)
    """Whether the plugin is a generator or an effect."""

    height = StructProp[int](PluginID.Wrapper)
    """Height of the plugin editor (in pixels)."""

    minimized = _WrapperProp(_WrapperFlags.Minimized)
    """Whether the plugin editor is maximized or minimized.

    ![](https://bit.ly/3QDMWO3)
    """

    multithreaded = _WrapperProp(_WrapperFlags.ThreadedProcessing)
    """Whether threaded processing is enabled or not."""

    page = StructProp[WrapperPage](PluginID.Wrapper)
    """Active / selected / current page.

    ![](https://bit.ly/3ffJKM3)
    """

    smart_disable = _WrapperProp(_WrapperFlags.SmartDisable)
    """Whether smart disable is enabled or not."""

    visible = _WrapperProp(_WrapperFlags.Visible)
    """Whether the editor of the plugin is visible or closed."""

    width = StructProp[int](PluginID.Wrapper)
    """Width of the plugin editor (in pixels)."""


AnyPlugin = _PluginBase[AnyEvent]  # TODO alias to _IPlugin + _PluginBase (both)


class PluginProp(RWProperty[AnyPlugin]):
    def __init__(self, *types: type[AnyPlugin]) -> None:
        self._types = types

    @staticmethod
    def _get_plugin_events(ins: EventModel) -> EventTree:
        return ins.events.subtree(lambda e: e.id in (PluginID.Wrapper, PluginID.Data))

    def __get__(self, ins: EventModel, owner: Any = None) -> AnyPlugin | None:
        if owner is None:
            return NotImplemented

        try:
            data_event = ins.events.first(PluginID.Data)
        except KeyError:
            return None

        if isinstance(data_event, UnknownDataEvent):
            return _PluginBase(self._get_plugin_events(ins))

        for ptype in self._types:
            event_type = ptype.__orig_bases__[0].__args__[0]  # type: ignore
            if isinstance(data_event, event_type):
                return ptype(self._get_plugin_events(ins))

    def __set__(self, ins: EventModel, value: AnyPlugin) -> None:
        if isinstance(value, _IPlugin):
            setattr(ins, "internal_name", value.INTERNAL_NAME)

        for id in (PluginID.Data, PluginID.Wrapper):
            for ie in ins.events.lst:
                if ie.e.id == id:
                    ie.e = value.events.first(id)


class _NativePluginProp(StructProp[T]):
    def __init__(self, prop: str | None = None, **kwds: Any) -> None:
        super().__init__(PluginID.Data, prop=prop, **kwds)


class _VSTPluginProp(RWProperty[T], NamedPropMixin):
    def __init__(self, id: _VSTPluginEventID, prop: str | None = None) -> None:
        self._id = id
        NamedPropMixin.__init__(self, prop)

    def __get__(self, ins: EventModel, _=None) -> T:
        event = cast(VSTPluginEvent, ins.events.first(PluginID.Data))
        for e in event["events"]:
            if e["id"] == self._id:
                return self._get(e["data"])
        raise AttributeError(self._id)

    def _get(self, value: Any) -> T:
        return cast(T, value if isinstance(value, (str, bytes)) else value[self._prop])

    def __set__(self, ins: EventModel, value: T) -> None:
        self._set(cast(VSTPluginEvent, ins.events.first(PluginID.Data)), value)

    def _set(self, event: VSTPluginEvent, value: T) -> None:
        for e in event["events"]:
            if e["id"] == self._id:
                e["data"] = value
                break


class _VSTFlagProp(_VSTPluginProp[bool]):
    def __init__(
        self, flag: _VSTFlags | _VSTFlags2, prop: str = "flags", inverted: bool = False
    ) -> None:
        super().__init__(_VSTPluginEventID.Flags, prop)
        self._flag = flag
        self._inverted = inverted

    def _get(self, value: Any) -> bool:
        retbool = self._flag in value[self._prop]
        return retbool if not self._inverted else not retbool

    def _set(self, event: VSTPluginEvent, value: bool) -> None:
        if self._inverted:
            value = not value

        for e in event["events"]:
            if e["id"] == self._id:
                if value:
                    e["data"][self._prop] |= value
                else:
                    e["data"][self._prop] &= ~value
                break


class PluginIOInfo(EventModel):
    mixer_offset = StructProp[int]()
    flags = StructProp[int]()


class VSTPlugin(_PluginBase[VSTPluginEvent], _IPlugin):
    """Represents a VST2 or a VST3 generator or effect.

    *New in FL Studio v1.5.23*: VST2 support (beta).
    *New in FL Studio v9.0.3*: VST3 support.
    """

    INTERNAL_NAME = "Fruity Wrapper"

    def __repr__(self) -> str:
        return f"VSTPlugin(name={self.name!r}, vendor={self.vendor!r})"

    class _AutomationOptions(EventModel):
        """See :attr:`VSTPlugin.automation`."""

        notify_changes = _VSTFlagProp(_VSTFlags.DontNotifyChanges, inverted=True)
        """Record parameter changes as automation.

        :guilabel:`Notify about parameter changes`. Defaults to ``True``.
        """

    class _CompatibilityOptions(EventModel):
        """See :attr:`VSTPlugin.compatibility`."""

        buffers_maxsize = _VSTFlagProp(_VSTFlags2.UseMaxFromHost, prop="flags2")
        """:guilabel:`Use maximum buffer size from host`. Defaults to ``False``."""

        fast_idle = _VSTPluginProp[bool](_VSTPluginEventID.Flags)
        """Increases idle rate - can make plugin GUI feel more responsive if its slow.

        May increase CPU usage. Defaults to ``False``.
        """

        fixed_buffers = _VSTFlagProp(_VSTFlags.FixedSizeBuffers)
        """:guilabel:`Use fixed size buffers`. Defaults to ``False``.

        Makes FL Studio send fixed size buffers instead of variable ones when ``True``.
        Can fix rendering errors caused by plugins. Increases latency by 2ms.
        """

        process_maximum = _VSTFlagProp(_VSTFlags2.ProcessMaxSize, prop="flags2")
        """:guilabel:`Process maximum size buffers`. Defaults to ``False``."""

        reset_on_transport = _VSTFlagProp(_VSTFlags.DontResetOnTransport, inverted=True)
        """:guilabel:`Reset plugin when FL Studio resets`. Defaults to ``True``."""

        send_loop = _VSTFlagProp(_VSTFlags.SendLoopPos)
        """Lets the plugin know about :attr:`Arrangemnt.loop_pos`.

        :guilabel:`Send loop position`. Defaults to ``True``.
        """

        use_time_offset = _VSTFlagProp(_VSTFlags.DontUseTimeOffset, inverted=True)
        """Adjust time information reported by plugin.

        Can fix timing issues caused by plugins in FL Studio <20.7 project.
        :guilabel:`Use time offset`. Defaults to ``False``.
        """

    class _MIDIOptions(EventModel):
        """See :attr:`VSTPlugin.midi`.

        ![](https://bit.ly/3NbGr4U)
        """

        input = _VSTPluginProp[int](_VSTPluginEventID.MIDI)
        """MIDI Input Port. Min = 0, Max = 255. Not selected = -1 (default)."""

        output = _VSTPluginProp[int](_VSTPluginEventID.MIDI)
        """MIDI Output Port. Min = 0, Max = 255. Not selected = -1 (default)."""

        pb_range = _VSTPluginProp[int](_VSTPluginEventID.MIDI)
        """Pitch bend range MIDI RPN sent to the plugin (in semitones).

        Min = 1. Max = 48. Defaults to 12.
        """

        send_modx = _VSTFlagProp(_VSTFlags.SendModX)
        """:guilabel:`Send MOD X as polyphonic aftertouch`. Defaults to ``False``."""

        send_pb = _VSTFlagProp(_VSTFlags.SendPBRange)
        """:guilabel:`Send pitch bend range (semitones)`. Defaults to ``False``.

        See also:
            :attr:`pb_range` - Sent to plugin as a MIDI RPN if this is ``True``.
        """

        send_release = _VSTFlagProp(_VSTFlags.DontSendRelVelo, inverted=True)
        """Whether release velocity should be sent in note off messages.

        :guilabel:`Send note release velocity`. Defaults to ``True``.
        """

    class _ProcessingOptions(EventModel):
        """See :attr:`VSTPlugin.processing`."""

        allow_sd = _VSTFlagProp(_VSTFlags.AllowSmartDisable)
        """:guilabel:`Allow smart disable`. Defaults to ``True``.

        Disables the :attr:`VSTPlugin.smart_disable` feature if ``False``.
        """

        bridged = _VSTFlagProp(_VSTFlags.LoadBridged)
        """Load a plugin in separate process.

        :guilabel:`Make bridged`. Defaults to ``False``.
        """

        external = _VSTFlagProp(_VSTFlags.ExternalWindow)
        """Keep plugin editor in bridge process.

        :guilabel:`External window`. Defaults to ``False``.
        """

        keep_state = _VSTFlagProp(_VSTFlags.DontKeepCPUState, inverted=True)
        """Don't touch unless you have issues like DC offsets, spikes and crashes.

        :guilabel:`Ensure processor state in callbacks`. Defaults to ``True``.
        """

        multithreaded = _VSTFlagProp(_VSTFlags.AllowThreaded)
        """Allow plugin to be multi-threaded by FL Studio.

        Disables the :attr:`VSTPlugin.multithreaded` feature if ``False``.

        :guilabel:`Allow threaded processing`. Defaults to ``True``.
        """

        notify_render = _VSTFlagProp(_VSTFlags.NotifyRender)
        """Lets the plugin know when rendering to audio file.

        This can be used by the plugin to switch to HQ processing or disable
        output entirely if it is in demo mode (depends on the plugin logic).

        :guilabel:`Notify about rendering mode`. Defaults to ``True``.
        """

        process_inactive = _VSTFlagProp(_VSTFlags.ProcessInactive)
        """Make FL Studio also process inputs / outputs marked as inactive by plugin.

        :guilabel:`Process inactive inputs and outputs`. Defaults to ``True``.
        """

    class _UIOptions(EventModel):
        """See :attr:`VSTPlugin.ui`.

        ![](https://bit.ly/3Nb3dtP)
        """

        accept_drop = _VSTFlagProp(_VSTFlags.AcceptFileDrop)
        """Host is bypassed when a file is dropped on the plugin editor.

        :guilabel:`Accept dropped files`. Defaults to ``False``.
        """

        always_update = _VSTFlagProp(_VSTFlags.UpdateWhenHidden)
        """Whether plugin UI should be updated when hidden; default to ``False``."""

        dpi_aware = _VSTFlagProp(_VSTFlags.DPIAwareBridged)
        """Enable if plugin editors look too big or small.

        :guilabel:`DPI aware when bridged`. Defaults to ``True``.
        """

        scale_editor = _VSTFlagProp(_VSTFlags.ScaleEditor)
        """Scale dimensions of editor that appear cut-off on high-res screens.

        :guilabel:`Scale editor dimensions`. Defaults to ``False``.
        """

    def __init__(self, events: EventTree, **kw: Any) -> None:
        super().__init__(events, **kw)

        # This doesn't break lazy evaluation in any way
        self.automation = self._AutomationOptions(events)
        self.compatibility = self._CompatibilityOptions(events)
        self.midi = self._MIDIOptions(events)
        self.processing = self._ProcessingOptions(events)
        self.ui = self._UIOptions(events)

    fourcc = _VSTPluginProp[str](_VSTPluginEventID.FourCC)
    """A unique four character code identifying the plugin.

    A database can be found on Steinberg's developer portal.
    """

    guid = _VSTPluginProp[bytes](_VSTPluginEventID.GUID)  # See issue #8
    name = _VSTPluginProp[str](_VSTPluginEventID.Name)
    """Factory name of the plugin."""

    # num_inputs = _VSTPluginProp[int]()
    # """Number of inputs the plugin supports."""

    # num_outputs = _VSTPluginProp[int]()
    # """Number of outputs the plugin supports."""

    plugin_path = _VSTPluginProp[str](_VSTPluginEventID.PluginPath)
    """The absolute path to the plugin binary."""

    state = _VSTPluginProp[bytes](_VSTPluginEventID.State)
    """Plugin specific preset data blob."""

    vendor = _VSTPluginProp[str](_VSTPluginEventID.Vendor)
    """Plugin developer (vendor) name."""

    # vst_number = _VSTPluginProp[int]()  # TODO


class BooBass(_PluginBase[BooBassEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3Bk3aGK)"""

    INTERNAL_NAME = "BooBass"
    bass = _NativePluginProp[int]()
    """Volume of the bass region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """

    high = _NativePluginProp[int]()
    """Volume of the high region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """

    mid = _NativePluginProp[int]()
    """Volume of the mid region.

    | Min | Max   | Default |
    |-----|-------|---------|
    | 0   | 65535 | 32767   |
    """


class FruitKick(_PluginBase[FruitKickEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/41fIPxE)"""

    INTERNAL_NAME = "Fruit Kick"
    amp_decay = _NativePluginProp[int]()
    """Amplitude (volume) decay length. Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0%             |
    | Max     | 256   | 100%           |
    | Default | 128   | 50%            |
    """

    click = _NativePluginProp[int]()
    """Amount of phase offset added to produce a click. Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0%             |
    | Max     | 64    | 100%           |
    | Default | 32    | 50%            |
    """

    distortion = _NativePluginProp[int]()
    """Linear. Defaults to minimum.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0%             |
    | Max     | 128   | 100%           |
    """

    freq_decay = _NativePluginProp[int]()
    """Pitch sweep time / pitch decay. Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0%             |
    | Max     | 256   | 100%           |
    | Default | 64    | 25%            |
    """

    max_freq = _NativePluginProp[int]()
    """Start frequency. Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -900  | -67%           |
    | Max     | 3600  | 100%           |
    | Default | 0     | 0%             |
    """

    min_freq = _NativePluginProp[int]()
    """Sweep to / end frequency. Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -1200 | -100%          |
    | Max     | 1200  | 100%           |
    | Default | -600  | -50%           |
    """


class FruityBalance(_PluginBase[FruityBalanceEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3RWItqU)"""

    INTERNAL_NAME = "Fruity Balance"
    pan = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    volume = _NativePluginProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


class FruityBloodOverdrive(_PluginBase[FruityBloodOverdriveEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3LnS1LE)"""

    INTERNAL_NAME = "Fruity Blood Overdrive"

    pre_band = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0.0000         |
    | Max     | 10000 | 1.0000         |
    | Default | 0     | 0.0000         |
    """

    color = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0.0000         |
    | Max     | 10000 | 1.0000         |
    | Default | 5000  | 0.5000         |
    """

    pre_amp = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0.0000         |
    | Max     | 10000 | 1.0000         |
    | Default | 0     | 0.0000         |
    """

    x100 = _NativePluginProp[bool]()
    """Boolean.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Off     | 0     | Off            |
    | On      | 1     | On             |
    | Default | 0     | Off            |
    """

    post_filter = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | 0.0000         |
    | Max     | 10000 | 1.0000         |
    | Default | 0     | 0.0000         |
    """

    post_gain = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -1.0000        |
    | Max     | 10000 |  0.0000        |
    | Default | 10000 |  0.0000        |
    """


class FruityCenter(_PluginBase[FruityCenterEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3TA9IIv)"""

    INTERNAL_NAME = "Fruity Center"
    enabled = _NativePluginProp[bool]()
    """Removes DC offset if True; effectively behaving like a bypass button.

    Labelled as **Status** for some reason in the UI.
    """


class FruityFastDist(_PluginBase[FruityFastDistEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3qT6Jil)"""

    INTERNAL_NAME = "Fruity Fast Dist"
    kind = _NativePluginProp[Literal["A", "B"]]()
    mix = _NativePluginProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """

    post = _NativePluginProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 128   | 100%      |
    """

    pre = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Percentage |
    |---------|-------|------------|
    | Min     | 64    | 33%        |
    | Max     | 192   | 100%       |
    | Default | 128   | 67%        |
    """

    threshold = _NativePluginProp[int]()
    """Linear, Stepped. Defaults to maximum value.

    | Type | Value | Percentage |
    |------|-------|------------|
    | Min  | 1     | 10%        |
    | Max  | 10    | 100%       |
    """


class FruityNotebook2(_PluginBase[FruityNotebook2Event], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3RHa4g5)"""

    INTERNAL_NAME = "Fruity NoteBook 2"
    active_page = _NativePluginProp[int]()
    """Active page number of the notebook. Min: 0, Max: 100."""

    editable = _NativePluginProp[bool]()
    """Whether the notebook is marked as editable or read-only.

    This attribute is just a visual marker used by FL Studio.
    """

    pages = _NativePluginProp[Dict[int, str]]()
    """A dict of page numbers to their contents."""


class FruitySend(_PluginBase[FruitySendEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3DqjvMu)"""

    INTERNAL_NAME = "Fruity Send"
    dry = _NativePluginProp[int]()
    """Linear. Defaults to maximum value.

    | Type | Value | Mix (wet) |
    |------|-------|-----------|
    | Min  | 0     | 0%        |
    | Max  | 256   | 100%      |
    """

    pan = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    send_to = _NativePluginProp[int]()
    """Target insert index; depends on insert routing. Defaults to -1 (Master)."""

    volume = _NativePluginProp[int]()
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
    post = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Mix (wet) |
    |---------|-------|-----------|
    | Min     | 0     | 0%        |
    | Max     | 160   | 100%      |
    | Default | 128   | 80%       |
    """

    threshold = _NativePluginProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 1     | -INFdB / 0.00  |
    | Max     | 127   | 0.0dB / 1.00   |
    | Default | 100   | -4.4dB / 0.60  |
    """


class FruityStereoEnhancer(_PluginBase[FruityStereoEnhancerEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3DoHvji)"""

    INTERNAL_NAME = "Fruity Stereo Enhancer"
    effect_position = _NativePluginProp[Literal["pre", "post"]]()
    """Defaults to ``post``."""

    pan = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -128  | 100% left      |
    | Max     | 127   | 100% right     |
    | Default | 0     | Centred        |
    """

    phase_inversion = _NativePluginProp[Literal["none", "left", "right"]]()
    """Default to ``None``."""

    phase_offset = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -512  | 500ms L        |
    | Max     | 512   | 500ms R        |
    | Default | 0     | No offset      |
    """

    stereo_separation = _NativePluginProp[int]()
    """Linear.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | -96   | 100% separated |
    | Max     | 96    | 100% merged    |
    | Default | 0     | No effect      |
    """

    volume = _NativePluginProp[int]()
    """Logarithmic.

    | Type    | Value | Representation |
    |---------|-------|----------------|
    | Min     | 0     | -INFdB / 0.00  |
    | Max     | 320   | 5.6dB / 1.90   |
    | Default | 256   | 0.0dB / 1.00   |
    """


class Plucked(_PluginBase[PluckedEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3GuFz9k)"""

    INTERNAL_NAME = "Plucked!"
    color = _NativePluginProp[int]()
    """Linear.

    | Min | Max  | Default |
    |-----|------|---------|
    | 0   | 128  | 64      |
    """

    decay = _NativePluginProp[int]()
    """Linear.

    | Min | Max  | Default |
    |-----|------|---------|
    | 0   | 256  | 128     |
    """

    gate = _NativePluginProp[bool]()
    """Stops the voices abruptly when released, otherwise the decay keeps going."""

    normalize = _NativePluginProp[bool]()
    """Same :attr:`decay` is tried to be used for all semitones.

    If not, higher notes have a shorter decay.
    """

    widen = _NativePluginProp[bool]()
    """Enriches the stereo panorama of the sound."""


class Soundgoodizer(_PluginBase[SoundgoodizerEvent], _IPlugin, ModelReprMixin):
    """![](https://bit.ly/3dip70y)"""

    INTERNAL_NAME = "Soundgoodizer"
    amount = _NativePluginProp[int]()
    """Logarithmic.

    | Min | Max  | Default |
    |-----|------|---------|
    | 0   | 1000 | 600     |
    """

    mode = _NativePluginProp[Literal["A", "B", "C", "D"]]()
    """4 preset modes (A, B, C and D). Defaults to ``A``."""


def get_event_by_internal_name(name: str) -> type[AnyEvent]:
    for cls in _PluginBase.__subclasses__():
        if getattr(cls, "INTERNAL_NAME", None) == name:
            return cls.__orig_bases__[0].__args__[0]  # type: ignore
    return NativePluginEvent
