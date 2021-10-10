import io
from typing import List, Optional, ValuesView

from pyflp.flobject.flobject import FLObject
from pyflp.event import Event, WordEvent, DWordEvent, TextEvent, DataEvent
from .note import Note
from .enums import PatternEvent

__all__ = ["Pattern"]


class Pattern(FLObject):
    _count = 0

    NOTE_SIZE = 24

    # * Properties
    @property
    def name(self) -> Optional[str]:
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self.setprop("name", value)

    @property
    def color(self) -> Optional[int]:
        return getattr(self, "_color", None)

    @color.setter
    def color(self, value: int):
        self.setprop("color", value)

    @property
    def index(self) -> Optional[int]:
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        self.setprop("index", value)
        self._events["index (metadata)"].dump(value)

    @property
    def notes(self) -> List[Note]:
        return getattr(self, "_notes", [])

    @notes.setter
    def notes(self, value: List[Note]):
        self._notes = value

    # * Parsing logic
    def parse_index1(self, event: WordEvent):
        """Thanks to FL for storing data of a single
        pattern at 2 different places."""
        self._events["index (metadata)"] = event

    def _parse_word_event(self, event: WordEvent):
        if event.id == PatternEvent.New:
            self._events["index"] = event
            self._index = event.to_uint16()

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == PatternEvent.Color:
            self.parse_uint32_prop(event, "color")

    def _parse_text_event(self, event: TextEvent):
        if event.id == PatternEvent.Name:
            self.parse_str_prop(event, "name")

    def _parse_data_event(self, event: DataEvent):
        if event.id == PatternEvent.Notes:
            self._events["notes"] = event
            if not len(event.data) % Pattern.NOTE_SIZE == 0:
                self._log.error(
                    f"Cannot parse pattern notes, size % {Pattern.NOTE_SIZE} != 0, contact me!"
                )
            self._notes_data = io.BytesIO(event.data)
            while True:
                data = self._notes_data.read(Pattern.NOTE_SIZE)
                if data == b"":  # None != b'', wow Python
                    break
                note = Note()
                note.parse(data)
                self._notes.append(note)

    def save(self) -> ValuesView[Event]:
        events = super().save()

        # Note events
        notes = self.notes
        notes_event = self._events.get("notes")
        if notes and notes_event:
            self._notes_data = io.BytesIO()
            for i, note in enumerate(notes):
                self._log.debug(f"Saving pattern note {i + 1}")
                self._notes_data.write(note.save())
            self._notes_data.seek(0)
            notes_event.dump(self._notes_data.read())

        # TODO: Controller events

        return events

    # * Utility methods
    def is_empty(self) -> bool:
        """Whether pattern has notes"""
        return "notes" in self._events

    def __init__(self):
        super().__init__()
        self.parse_metadata = False
        self._notes: List[Note] = []
