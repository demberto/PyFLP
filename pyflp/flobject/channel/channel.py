import enum
from typing import List, Optional, Union, ValuesView
from pyflp.exceptions import DataCorruptionDetected

from pyflp.flobject import FLObject
from pyflp.event import Event, ByteEvent, WordEvent, DWordEvent, TextEvent, DataEvent
from pyflp.flobject.plugin import Plugin
from pyflp.flobject.insert import Insert

from .enums import ChannelEvent, ChannelFXEvent
from .delay import ChannelDelay
from .fx import ChannelFX

__all__ = ["Channel", "ChannelKind"]


class ChannelKind(enum.IntEnum):
    Sampler = 0
    Audio = 2  # MIDI Out is also categorized as this for some reason
    Layer = 3
    Instrument = 4
    Automation = 5


class Channel(FLObject):
    """Represents an Audio, Instrument, Layer or a Sampler channel in the channel rack."""

    max_count = 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object, kind={self.kind}>"

    # * Properties
    @property
    def default_name(self) -> Optional[str]:
        """Default name of the channel. Default event is stored.
        The value of this depends on the type of `plugin`:

        * Native (stock) plugin: The name obtained from the plugin is stored.
        * VST plugin (VSTi): 'Fruity Wrapper'.

        See `name` also.
        """
        return getattr(self, "_default_name", None)

    @default_name.setter
    def default_name(self, value: str):
        self._setprop("default_name", value)

    @property
    def index(self) -> Optional[int]:
        """Index of the channel, should be no more than
        `pyflp.flobject.misc.misc.Misc.channel_count`."""
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        self._setprop("index", value)

    @property
    def volume(self) -> Optional[int]:
        """Volume of the channel. Default event is stored."""
        return getattr(self, "_volume", None)

    @volume.setter
    def volume(self, value: int):
        self._setprop("volume", value)

    @property
    def pan(self) -> Optional[int]:
        """Panning of the channel. Default event is stored."""
        return getattr(self, "_pan", None)

    @pan.setter
    def pan(self, value: int):
        self._setprop("pan", value)

    @property
    def color(self) -> Optional[int]:
        """Color of the channel. Default event is stored."""
        return getattr(self, "_color", None)

    @color.setter
    def color(self, value: int):
        self._setprop("color", value)

    @property
    def target_insert(self) -> Optional[int]:
        """The index of the `pyflp.flobject.insert.insert.Insert` the channel is routed to.
        Allowed values: -1 to `pyflp.flobject.insert.insert.Insert.max_count`."""
        return getattr(self, "_target_insert", None)

    @target_insert.setter
    def target_insert(self, value: int):
        assert value in range(-1, Insert.max_count)
        self._setprop("target_insert", value)

    @property
    def kind(self) -> Union[ChannelKind, int, None]:
        """Type of channel. See `ChannelKind` for the various types."""
        return getattr(self, "_kind", None)

    @kind.setter
    def kind(self, value: Union[ChannelKind, int]):
        self._setprop("kind", value)

    @property
    def enabled(self) -> Optional[bool]:
        """Whether the channel is enabled in the channel rack."""
        return getattr(self, "_enabled", None)

    @enabled.setter
    def enabled(self, value: bool):
        self._setprop("enabled", value)

    @property
    def locked(self) -> Optional[bool]:
        """Whether the channel is locked in the channel rack.
        Paired with the `Channel.enabled`, it represents the
        actual state of the channel."""
        return getattr(self, "_locked", None)

    @locked.setter
    def locked(self, value: bool):
        self._setprop("locked", value)

    @property
    def zipped(self) -> Optional[bool]:
        """Whether the channel is zipped in the channel rack."""
        return getattr(self, "_zipped", None)

    @zipped.setter
    def zipped(self, value: bool):
        self._setprop("zipped", value)

    @property
    def root_note(self) -> Optional[int]:
        """Root note of the channel."""
        return getattr(self, "_root_note", None)

    @root_note.setter
    def root_note(self, value: int):
        self._setprop("root_note", value)

    @property
    def icon(self) -> Optional[int]:
        """Icon of the channel."""
        return getattr(self, "_icon", None)

    @icon.setter
    def icon(self, value: int):
        self._setprop("icon", value)

    @property
    def sample_path(self) -> Optional[str]:
        """The path to the sample file on the disk. Valid only if
        `Channel.kind` is `ChannelKind.Sampler` or `ChannelKind.Audio`."""
        return getattr(self, "_sample_path", None)

    @sample_path.setter
    def sample_path(self, value: str):
        assert self._kind in (ChannelKind.Sampler, ChannelKind.Audio)
        self._setprop("sample_path", value)

    @property
    def filter_channel(self) -> Optional[int]:
        """The channel display filter (a.k.a : `FilterChannel`) under which channel is grouped."""
        return getattr(self, "_filter_channel", None)

    @filter_channel.setter
    def filter_channel(self, value: int):
        self._setprop("filter_channel", value)

    @property
    def plugin(self) -> Optional[Plugin]:
        """The `pyflp.flobject.plugin.plugin.Plugin` associated with the channel.
        Valid only if `Channel.kind` is `ChannelKind.Instrument`."""
        return getattr(self, "_plugin", None)

    @plugin.setter
    def plugin(self, value: Plugin):
        assert (
            self._kind == ChannelKind.Instrument
        ), "Channel kind must be ChannelKind.Instrument to assign a plugin to it"
        self._plugin = value

    @property
    def children(self) -> List[int]:
        """List of children `index`es of a Layer.
        Valid only if `kind` is `ChannelKind.Layer`."""
        return getattr(self, "_children", [])

    @children.setter
    def children(self, value: List[int]):
        assert self._kind == ChannelKind.Layer, "Only Layer channels can have children."
        for child in value:
            assert child <= Channel.max_count
        self._children = value

    @property
    def fx(self) -> Optional[ChannelFX]:
        """See `ChannelFX`"""
        return getattr(self, "_fx", None)

    @fx.setter
    def fx(self, value: ChannelFX):
        self._fx = value

    @property
    def name(self) -> Optional[str]:
        """The value of this depends on the type of `plugin`:

        * Native (stock) plugin: User-given name. Default event is not stored.
        * VST plugin (VSTi): The name obtained from the VST, or the user-given name.
          Default event (i.e VST plugin name) is stored.

        See `default_name` also.
        """
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self._setprop("name", value)

    @property
    def sampler_flags(self) -> Optional[int]:
        """Flags associated with a channel of kind `ChannelKind.Sampler`."""
        return getattr(self, "_sampler_flags", None)

    @sampler_flags.setter
    def sampler_flags(self, value: int):
        self._setprop("sampler_flags", value)

    @property
    def layer_flags(self) -> Optional[int]:
        """Flags associated with a channel of kind `ChannelKind.Layer`."""
        return getattr(self, "_layer_flags", None)

    @layer_flags.setter
    def layer_flags(self, value: int):
        self._setprop("layer_flags", value)

    @property
    def use_loop_points(self) -> Optional[bool]:
        """Sampler -> Playback -> Use loop points."""
        return getattr(self, "_use_loop_points", None)

    @use_loop_points.setter
    def use_loop_points(self, value: bool):
        self._setprop("use_loop_points", value)

    @property
    def swing(self) -> Optional[int]:
        """Sampler/Instruemnt -> Miscellaneous functions -> Time -> Swing."""
        return getattr(self, "_swing", None)

    @swing.setter
    def swing(self, value: int):
        self._setprop("swing", value)

    @property
    def delay(self) -> Optional[ChannelDelay]:
        return getattr(self, "_delay", None)

    @delay.setter
    def delay(self, value: ChannelDelay):
        self._delay = value

    # * Parsing logic
    def parse_event(self, e: Event) -> None:
        if e.id in ChannelFXEvent.__members__.values():
            if not hasattr(self, "_fx"):
                self._fx = ChannelFX()
            self._fx.parse_event(e)
            return
        return super().parse_event(e)

    def _parse_byte_event(self, e: ByteEvent):
        if e.id == ChannelEvent.Enabled:
            self._parse_bool_prop(e, "enabled")
        elif e.id == ChannelEvent._Vol:
            self._parse_uint8_prop(e, "volume")
        elif e.id == ChannelEvent._Pan:
            self._parse_int8_prop(e, "pan")
        elif e.id == ChannelEvent.Kind:
            self._events["kind"] = e
            kind = e.to_uint8()
            try:
                self._kind = ChannelKind(kind)
            except AttributeError:
                self._kind = kind  # type: ignore
                self._log.error(
                    f"Unknown channel kind {kind}; expected one of {ChannelKind.__members__}"
                )
        elif e.id == ChannelEvent.Zipped:
            self._parse_bool_prop(e, "zipped")
        elif e.id == ChannelEvent.UseLoopPoints:
            self._parse_bool_prop(e, "use_loop_points")
        elif e.id == ChannelEvent.TargetInsert:
            self._parse_int8_prop(e, "target_insert")
        elif e.id == ChannelEvent.Locked:
            self._parse_bool_prop(e, "locked")

    def _parse_word_event(self, e: WordEvent):
        if e.id == ChannelEvent.New:
            self._parse_uint16_prop(e, "index")
        elif e.id == ChannelEvent.Volume:
            self._parse_uint16_prop(e, "volume")
        elif e.id == ChannelEvent.Pan:
            self._parse_int16_prop(e, "pan")
        elif e.id == ChannelEvent.LayerChildren:
            if not self.kind == ChannelKind.Layer:
                exc = f"Channel {self._idx} has children but it is not a layer"
                self._log.exception(exc)
                raise DataCorruptionDetected(exc)
            self._events[f"child{self.__children_count}"] = e
            self.__children_count += 1
            index = e.to_uint16()
            if index in self.children:
                self._log.error(f"Duplicate layer event, child index {index}")
            self.children.append(index)
        elif e.id == ChannelEvent.Swing:
            self._parse_uint16_prop(e, "swing")

    def _parse_dword_event(self, e: DWordEvent):
        if e.id == ChannelEvent.Color:
            self._parse_uint32_prop(e, "color")
        elif e.id == ChannelEvent.RootNote:
            self._parse_uint32_prop(e, "root_note")
        elif e.id == ChannelEvent.Icon:
            self._parse_uint32_prop(e, "icon")
        elif e.id == ChannelEvent.SamplerFlags:
            self._parse_uint32_prop(e, "sampler_flags")
        elif e.id == ChannelEvent.LayerFlags:
            self._parse_uint32_prop(e, "layer_flags")
        elif e.id == ChannelEvent.FilterChannelNum:
            self._parse_int32_prop(e, "filter_channel")

    def _parse_text_event(self, e: TextEvent):
        if e.id == ChannelEvent.DefaultName:
            self._parse_str_prop(e, "default_name")
        elif e.id == ChannelEvent.SamplePath:
            self._parse_str_prop(e, "sample_path")
        elif e.id == ChannelEvent.Name:
            self._parse_str_prop(e, "name")

    def _parse_data_event(self, e: DataEvent) -> None:
        if e.id == ChannelEvent.Plugin:
            self._parse_flobject_prop(e, "plugin", Plugin())
        elif e.id == ChannelEvent.Delay:
            self._parse_flobject_prop(e, "delay", ChannelDelay())

    def save(self) -> List[Event]:  # type: ignore
        events = list(super().save())

        # Plugin, ChannelDelay and layer children are all already in _events
        if self.fx:
            events.extend(list(self.fx.save()))
        return events

    def __init__(self):
        # Layer children count, used for unique dictionary keys in self._events
        self.__children_count = 0
        super().__init__()
