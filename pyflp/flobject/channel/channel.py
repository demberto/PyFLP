import enum
from typing import (
    Optional,
    Union,
    ValuesView
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
from pyflp.utils import (
    WORD,
    DWORD,
    TEXT,
    DATA
)

class ChannelKind(enum.IntEnum):
    Sampler = 0
    Audio = 2       # MIDI Out is also categorized as this for some reason
    Layer = 3
    Instrument = 4
    Automation = 5

class ChannelEventID(enum.IntEnum):
    Enabled = 0
    #_Vol = 2
    #_Pan = 3
    Zipped = 15
    #UseLoopPoints = 19
    Kind = 21
    TargetInsert = 22
    #FXProperties = 27
    Locked = 32
    New = WORD
    #Fx = WORD + 5
    #FadeStereo = WORD + 6
    #CutOff = WORD + 7
    #Vol = WORD + 8
    #Pan = WORD + 9
    #PreAmp = WORD + 10
    #Decay = WORD + 11
    #Attack = WORD + 12
    #DotNote = WORD + 13
    #DotPitch = WORD + 14
    #DotMix = WORD + 15
    #Resonance = WORD + 19
    #StereoDelay = WORD + 21
    #Fx3 = WORD + 22
    #DotReso = WORD + 23
    #DotCutOff = WORD + 24
    #ShiftDelay = WORD + 25
    #Dot = WORD + 27
    #DotRel = WORD + 32
    #DotShift = WORD + 28
    #Layer = WORD + 30
    #Swing = WORD + 33
    Color = DWORD
    #Echo = DWORD + 2
    #FxSine = DWORD + 3
    #CutSelfCutBy = DWORD + 4
    RootNote = DWORD + 7
    #_MainResoCutOff = DWORD + 9
    #DelayModXY = DWORD + 10
    #Reverb = DWORD + 11
    #StretchTime = DWORD + 12
    #FineTune = DWORD + 14
    #SamplerFlags = DWORD + 15
    #LayerFlags = DWORD + 16
    FilterChannelNum = DWORD + 17
    #AUSampleRate = DWORD + 25
    Icon = DWORD + 27
    Name = TEXT
    SamplePath = TEXT + 4
    #GeneratorName = TEXT + 9
    #Delay = DATA + 1
    Plugin = DATA + 5

class Channel(FLObject):
    _count = 0
    
    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    
    @property
    def index(self) -> Optional[int]:
        return getattr(self, '_index', None)
    
    @index.setter
    def index(self, value: int):
        self.setprop('index', value)
    
    @property
    def color(self) -> Optional[int]:
        return getattr(self, '_color', None)
    
    @color.setter
    def color(self, value: int):
        self.setprop('color', value)
    
    @property
    def target_insert(self) -> Optional[int]:
        """Allowed values: -1 to Insert.max_count"""
        return getattr(self, '_target_insert', None)
    
    @target_insert.setter
    def target_insert(self, value: int):
        assert value in range(-1, Insert.max_count)
        self.setprop('target_insert', value)
    
    @property
    def kind(self) -> Union[ChannelKind, int, None]:
        return getattr(self, '_kind', None)
    
    @kind.setter
    def kind(self, value: ChannelKind):
        self.setprop('kind', value)
    
    @property
    def enabled(self) -> Optional[bool]:
        return getattr(self, '_enabled', None)
    
    @enabled.setter
    def enabled(self, value: bool):
        self.setprop('enabled', value)

    @property
    def locked(self) -> Optional[bool]:
        return getattr(self, '_locked', None)
    
    @locked.setter
    def locked(self, value: bool):
        self.setprop('locked', value)
    
    @property
    def zipped(self) -> Optional[bool]:
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
        return getattr(self, '_icon', None)
    
    @icon.setter
    def icon(self, value: int):
        self.setprop('icon', value)
    
    @property
    def sample_path(self) -> Optional[str]:
        return getattr(self, '_sample_path', None)
    
    @sample_path.setter
    def sample_path(self, value: str):
        self.setprop('sample_path', value)

    @property
    def filter_channel(self) -> Optional[int]:
        return getattr(self, '_filter_channel', None)
    
    @filter_channel.setter
    def filter_channel(self, value: int):
        self.setprop('filter_channel', value)
    
    @property
    def plugin(self) -> Optional[Plugin]:
        return getattr(self, '_plugin', None)
    
    @plugin.setter
    def plugin(self, value: Plugin):
        self._plugin = value
    
    def _parse_byte_event(self, event: ByteEvent):
        if event.id == ChannelEventID.Enabled:
            self._events['enabled'] = event
            self._enabled = event.to_bool()
        elif event.id == ChannelEventID.Kind:
            self._events['kind'] = event
            self._kind = ChannelKind(event.to_uint8())
        elif event.id == ChannelEventID.Zipped:
            self._events['zipped'] = event
            self._zipped = event.to_bool()
        elif event.id == ChannelEventID.TargetInsert:
            self._events['target_insert'] = event
            self._target_insert = event.to_int8()
        elif event.id == ChannelEventID.Locked:
            self._events['locked'] = event
            self._locked = event.to_bool()
    
    def _parse_word_event(self, event: WordEvent):
        if event.id == ChannelEventID.New:
            self._events['index'] = event
            self._index = event.to_uint16()

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == ChannelEventID.Color:
            self._events['color'] = event
            self._color = event.to_uint32()
        elif event.id == ChannelEventID.RootNote:
            self._events['root_note'] = event
            self._root_note = event.to_uint32()
        elif event.id == ChannelEventID.Icon:
            self._events['icon'] = event
            self._icon = event.to_uint32()
        elif event.id == ChannelEventID.FilterChannelNum:
            self._events['filter_channel'] = event
            self._filter_channel = event.to_int32()
    
    def _parse_text_event(self, event: TextEvent):
        if event.id == ChannelEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()
        elif event.id == ChannelEventID.SamplePath:
            self._events['sample_path'] = event
            self._sample_path = event.to_str()
    
    def _parse_data_event(self, event: DataEvent) -> None:
        if event.id == ChannelEventID.Plugin:
            self._events['plugin'] = event
            self._plugin = Plugin()
            self._plugin.parse(event)
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        self.plugin.save()
        return super().save()

    def __init__(self):
        Channel._count += 1
        super().__init__()
        self._log.info(f"__init__(), count: {self._count}")