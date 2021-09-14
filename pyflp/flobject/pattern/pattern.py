import enum
import io
from pyflp.bytesioex import BytesIOEx
from typing import (
    List,
    Optional,
    ValuesView
)

from pyflp.flobject.flobject import FLObject
from pyflp.event import (
    Event,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)
from pyflp.flobject.pattern.note import Note
from pyflp.utils import (
    WORD,
    DWORD,
    TEXT,
    DATA
)

@enum.unique
class PatternEventID(enum.IntEnum):
    New = WORD + 1
    #_Data = WORD + 4
    Color = DWORD + 22
    Name = TEXT + 1
    #_157 = DWORD + 29   # FL 12.5+
    #_158 = DWORD + 30   # default: -1
    #_164 = DWORD + 36   # default: 0
    #Controllers = DATA + 15
    Notes = DATA + 16

class Pattern(FLObject):
    _count = 0
    NOTE_SIZE = 24
    
    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    
    @property
    def color(self) -> Optional[int]:
        return getattr(self, '_color', None)
    
    @color.setter
    def color(self, value: int):
        self.setprop('color', value)

    @property
    def index(self) -> Optional[int]:
        return getattr(self, '_index', None)
    
    @index.setter
    def index(self, value: int):
        self.setprop('index', value)
    
    @property
    def notes(self) -> List[Note]:
        return getattr(self, '_notes', [])
    
    @notes.setter
    def notes(self, value: List[Note]):
        for note in value:
            pass
        self._notes = value
    
    def _parse_word_event(self, event: WordEvent):
        if event.id == PatternEventID.New:
            self._events['index'] = event
            self._index = event.to_uint16()
    
    def _parse_dword_event(self, event: DWordEvent):
        if event.id == PatternEventID.Color:
            self._events['color'] = event
            self._color = event.to_uint32()

    def _parse_text_event(self, event: TextEvent):
        if event.id == PatternEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()
    
    def _parse_data_event(self, event: DataEvent):
        if event.id == PatternEventID.Notes:
            self._events['notes'] = event
            if not event.data % Pattern.NOTE_SIZE == 0:
                self._log.error(f"Cannot parse pattern notes, size % {Pattern.NOTE_SIZE} != 0, contact me!")
            self._notes_data = io.BytesIO(event.data)
            while True:
                data = self._notes_data.read(Pattern.NOTE_SIZE)
                if not data:
                    break
                note = Note()
                note.parse(data)
                self._notes.append(note)
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        notes = self.notes
        notes_event = self._events.get('notes')
        if notes and notes_event:
            self._notes_data = io.BytesIO()
            for idx, note in enumerate(notes):
                self._log.debug(f"Saving pattern note {idx}")
                self._notes_data.write(note.save())
        self._notes_data.seek(0)
        notes_event.dump(self._notes_data.read())
        return super().save()
    
    def __init__(self):
        super().__init__()
        self.idx = Pattern._count
        Pattern._count += 1
        self._log.info(f"__init__(), index: {self.idx}, count: {self._count}")