import enum
from typing import (
    List,
    Optional,
    Union
)

from pyflp.flobject.flobject import FLObject
from pyflp.event import(
    Event,
    ByteEvent,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)
from pyflp.flobject.plugin import Plugin
from pyflp.flobject.insert import Insert
from pyflp.flobject.channel.event_id import ChannelEventID, ChannelFXEventID
from pyflp.flobject.channel.channel_fx import ChannelFX

__all__ = ['Channel']

class ChannelKind(enum.IntEnum):
    Sampler = 0
    Audio = 2       # MIDI Out is also categorized as this for some reason
    Layer = 3
    Instrument = 4
    Automation = 5

class Channel(FLObject):
    max_count = 0

    #region Properties
    @property
    def default_name(self) -> Optional[str]:
        """Default name of the channel. Default event is stored.
        The value of this depends on the type of `plugin`:
        
        * Native (stock) plugin: The name obtained from the plugin is stored.
        * VST plugin (VSTi): 'Fruity Wrapper'.
        
        See `name` also.
        """
        return getattr(self, '_default_name', None)

    @default_name.setter
    def default_name(self, value: str):
        self.setprop('default_name', value)

    @property
    def index(self) -> Optional[int]:
        """Index of the channel, should be no more than `pyflp.flobject.misc.misc.Misc.channel_count`."""
        return getattr(self, '_index', None)

    @index.setter
    def index(self, value: int):
        self.setprop('index', value)

    @property
    def volume(self) -> Optional[int]:
        """Volume of the channel. Default event is stored."""
        return getattr(self, '_volume', None)

    @volume.setter
    def volume(self, value: int):
        self.setprop('volume', value)

    @property
    def pan(self) -> Optional[int]:
        """Panning of the channel. Default event is stored."""
        return getattr(self, '_pan', None)

    @pan.setter
    def pan(self, value: int):
        self.setprop('pan', value)

    @property
    def color(self) -> Optional[int]:
        """Color of the channel. Default event is stored."""
        return getattr(self, '_color', None)

    @color.setter
    def color(self, value: int):
        self.setprop('color', value)

    @property
    def target_insert(self) -> Optional[int]:
        """The index of the `pyflp.flobject.insert.insert.Insert` the channel is routed to.
        Allowed values: -1 to `pyflp.flobject.insert.insert.Insert.max_count`."""
        return getattr(self, '_target_insert', None)

    @target_insert.setter
    def target_insert(self, value: int):
        assert value in range(-1, Insert.max_count)
        self.setprop('target_insert', value)

    @property
    def kind(self) -> Union[ChannelKind, int, None]:
        """Type of channel. See `ChannelKind` for the various types."""
        return getattr(self, '_kind', None)

    @kind.setter
    def kind(self, value: ChannelKind):
        self.setprop('kind', value)

    @property
    def enabled(self) -> Optional[bool]:
        """Whether the channel is enabled in the channel rack."""
        return getattr(self, '_enabled', None)

    @enabled.setter
    def enabled(self, value: bool):
        self.setprop('enabled', value)

    @property
    def locked(self) -> Optional[bool]:
        """Whether the channel is locked in the channel rack.
        Paired with the `Channel.enabled`, it represents the actual state of the channel."""
        return getattr(self, '_locked', None)

    @locked.setter
    def locked(self, value: bool):
        self.setprop('locked', value)

    @property
    def zipped(self) -> Optional[bool]:
        """Whether the channel is zipped in the channel rack."""
        return getattr(self, '_zipped', None)

    @zipped.setter
    def zipped(self, value: bool):
        self.setprop('zipped', value)

    @property
    def root_note(self) -> Optional[int]:
        return getattr(self, '_root_note', None)

    @root_note.setter
    def root_note(self, value: int):
        self.setprop('root_note', value)

    @property
    def icon(self) -> Optional[int]:
        """Icon of the channel."""
        return getattr(self, '_icon', None)

    @icon.setter
    def icon(self, value: int):
        self.setprop('icon', value)

    @property
    def sample_path(self) -> Optional[str]:
        """The path to the sample file on the disk. Valid only if
        `Channel.kind` is `ChannelKind.Sampler` or `ChannelKind.Audio`."""
        assert self._kind in (ChannelKind.Sampler, ChannelKind.Audio)
        return getattr(self, '_sample_path', None)

    @sample_path.setter
    def sample_path(self, value: str):
        self.setprop('sample_path', value)

    @property
    def filter_channel(self) -> Optional[int]:
        """The channel display filter (a.k.a : `FilterChannel`) under which channel is grouped."""
        return getattr(self, '_filter_channel', None)

    @filter_channel.setter
    def filter_channel(self, value: int):
        self.setprop('filter_channel', value)

    @property
    def plugin(self) -> Optional[Plugin]:
        """The `pyflp.flobject.plugin.plugin.Plugin` associated with the channel.
        Valid only if `Channel.kind` is `ChannelKind.Instrument`."""
        return getattr(self, '_plugin', None)

    @plugin.setter
    def plugin(self, value: Plugin):
        assert self._kind == ChannelKind.Instrument, "Channel kind must be ChannelKind.Instrument to assign a plugin to it"
        self._plugin = value

    @property
    def children(self) -> List[int]:
        """List of children :attr:`~Channel.index`es of a Layer.
        Valid only if :attr:`~Channel.kind` is :attr:`~ChannelKind.Layer`."""
        assert self._kind == ChannelKind.Layer, "Only Layer channels can have children."
        return getattr(self, '_children', [])

    @children.setter
    def children(self, value: List[int]):
        for child in value:
            assert child <= Channel
        self._children = value
    
    @property
    def fx(self) -> Optional[ChannelFX]:
        return getattr(self, '_fx', None)

    @fx.setter
    def fx(self, value: ChannelFX):
        self._fx = value
    
    @property
    def name(self) -> Optional[str]:
        """The value of this depends on the type of `plugin`:
        
        * Native (stock) plugin: User-given name. Default event is not stored.
        * VST plugin (VSTi): The name obtained from the VST, or the user-given name. \
          Default event (i.e VST plugin name) is stored.
        
        See `default_name` also.
        """
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    #endregion

    #region Parsing logic
    def parse(self, event: Event) -> None:
        if event.id in ChannelFXEventID.__members__.values():
            if not hasattr(self, '_fx'):
                self._fx = ChannelFX()
            self._fx.parse(event)
            return
        return super().parse(event)
    
    def _parse_byte_event(self, event: ByteEvent):
        if event.id == ChannelEventID.Enabled:
            self.parse_bool_prop(event, 'enabled')
        elif event.id == ChannelEventID._Vol:
            self.parse_uint8_prop(event, 'volume')
        elif event.id == ChannelEventID._Pan:
            self.parse_int8_prop(event, 'pan')
        elif event.id == ChannelEventID.Kind:
            self._events['kind'] = event
            kind = event.to_uint8()
            try:
                self._kind = ChannelKind(kind)
            except AttributeError:
                self._kind = kind
                self._log.error(f"Unknown channel kind {kind}; expected one of {ChannelKind.__members__}")
        elif event.id == ChannelEventID.Zipped:
            self.parse_bool_prop(event, 'zipped')
        elif event.id == ChannelEventID.TargetInsert:
            self.parse_int8_prop(event, 'target_insert')
        elif event.id == ChannelEventID.Locked:
            self.parse_bool_prop(event, 'locked')

    def _parse_word_event(self, event: WordEvent):
        if event.id == ChannelEventID.New:
            self.parse_uint16_prop(event, 'index')
        elif event.id == ChannelEventID.Volume:
            self.parse_uint16_prop(event, 'volume')
        elif event.id == ChannelEventID.Pan:
            self.parse_int16_prop(event, 'pan')
        elif event.id == ChannelEventID.LayerChildren:
            children_events: List[Event] = self._events.get('children', [])
            children_events.append(event)
            children: List[int] = getattr(self, '_children', [])
            children.append(event.to_uint16())

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == ChannelEventID.Color:
            self.parse_uint32_prop(event, 'color')
        elif event.id == ChannelEventID.RootNote:
            self.parse_uint32_prop(event, 'root_note')
        elif event.id == ChannelEventID.Icon:
            self.parse_uint32_prop(event, 'icon')
        elif event.id == ChannelEventID.FilterChannelNum:
            self.parse_int32_prop(event, 'filter_channel')

    def _parse_text_event(self, event: TextEvent):
        if event.id == ChannelEventID.DefaultName:
            self.parse_str_prop(event, 'default_name')
        elif event.id == ChannelEventID.SamplePath:
            self.parse_str_prop(event, 'sample_path')
        elif event.id == ChannelEventID.GeneratorName:
            self.parse_str_prop(event, 'name')

    def _parse_data_event(self, event: DataEvent) -> None:
        if event.id == ChannelEventID.Plugin:
            self._events['plugin'] = event
            self._plugin = Plugin()
            self._plugin.parse(event)
    #endregion

    def save(self) -> Optional[List[Event]]:
        self._log.info("save() called")
        event_store: List[Event] = super().save()
        
        if self.plugin:
            # Present only for ChannelKind.Instrument
            event_store.extend(self.plugin.save())
        if self.fx:
            event_store.extend(self.fx.save())
        
        return event_store

    def __init__(self):
        super().__init__()