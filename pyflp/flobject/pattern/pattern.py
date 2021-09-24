import io
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
from pyflp.flobject.pattern.event_id import PatternEventID

__all__ = ['Pattern']

class Pattern(FLObject):
    _count = 0
    _parse_metadata = False     # Assuming metadata comes after note events

    NOTE_SIZE = 24

    #region Properties
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
        self._events['index (metadata)'].dump(value)

    @property
    def notes(self) -> List[Note]:
        return getattr(self, '_notes', [])

    @notes.setter
    def notes(self, value: List[Note]):
        self._notes = value
    #endregion

    #region Parsing logic
    def _parse_word_event(self, event: WordEvent):
        if event.id == PatternEventID.New:
            # TODO: Fix this
            if Pattern._parse_metadata:
                self._events['index (metadata)'] = event
            else:
                self._events['index'] = event
                self._index = event.to_uint16()


    def _parse_dword_event(self, event: DWordEvent):
        if event.id == PatternEventID.Color:
            self.parse_uint32_prop(event, 'color')

    def _parse_text_event(self, event: TextEvent):
        if event.id == PatternEventID.Name:
            self.parse_str_prop(event, 'name')

    def _parse_data_event(self, event: DataEvent):
        if event.id == PatternEventID.Notes:
            self._events['notes'] = event
            if not len(event.data) % Pattern.NOTE_SIZE == 0:
                self._log.error(f"Cannot parse pattern notes, size % {Pattern.NOTE_SIZE} != 0, contact me!")
            self._notes_data = io.BytesIO(event.data)
            while True:
                data = self._notes_data.read(Pattern.NOTE_SIZE)
                if data is None:
                    break
                note = Note()
                note.parse(data)
                self._notes.append(note)
    #endregion

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info(f"save() called {self.idx}")
        
        # Note events
        notes = self.notes
        notes_event = self._events.get('notes')
        if notes and notes_event:
            self._notes_data = io.BytesIO()
            for i, note in enumerate(notes):
                self._log.debug(f"Saving pattern note {i + 1}")
                self._notes_data.write(note.save())
            self._notes_data.seek(0)
            notes_event.dump(self._notes_data.read())
        
        # TODO: Controller events
        
        return super().save()

    #region Utility methods
    def is_empty(self) -> bool:
        """Whether pattern has notes"""
        return 'notes' in self._events
    #endregion

    def __init__(self):
        super().__init__()
        self.idx = Pattern._count
        Pattern._count += 1
        self._log.info(f"__init__(), index: {self.idx}, count: {self._count}")
        self._notes: List[Note] = []
