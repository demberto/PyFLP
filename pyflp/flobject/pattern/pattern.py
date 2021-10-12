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
        """Pattern name. Default event is not stored."""
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self._setprop("name", value)

    @property
    def color(self) -> Optional[int]:
        """Pattern color."""
        return getattr(self, "_color", None)

    @color.setter
    def color(self, value: int):
        self._setprop("color", value)

    @property
    def index(self) -> Optional[int]:
        """Pattern index. Begins from 1.

        Occurs twice, once near the top with note data and once with rest of
        the metadata. The first time a `PatternEvent.New` occurs, it is
        parsed by `parse_index1()`. Empty patterns are not stored at the top
        since they don't have any note data. They come later on.

        See `Parser.__parse_pattern()` for implemntation."""
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        self._setprop("index", value)
        self._events["index (metadata)"].dump(value)

    @property
    def notes(self) -> List[Note]:
        """Contains the list of MIDI events (notes) of all channels."""
        return getattr(self, "_notes", [])

    @notes.setter
    def notes(self, value: List[Note]):
        self._notes = value

    # * Parsing logic
    def parse_index1(self, e: WordEvent):
        """Thanks to FL for storing data of a single
        pattern at 2 different places."""
        self._events["index (metadata)"] = e

    def _parse_word_event(self, e: WordEvent):
        if e.id == PatternEvent.New:
            self._parse_uint16_prop(e, "index")

    def _parse_dword_event(self, e: DWordEvent):
        if e.id == PatternEvent.Color:
            self._parse_uint32_prop(e, "color")

    def _parse_text_event(self, e: TextEvent):
        if e.id == PatternEvent.Name:
            self._parse_str_prop(e, "name")

    def _parse_data_event(self, e: DataEvent):
        if e.id == PatternEvent.Notes:
            self._events["notes"] = e
            if not len(e.data) % Pattern.NOTE_SIZE == 0:
                self._log.error(
                    f"Cannot parse pattern notes, size % {Pattern.NOTE_SIZE} != 0, contact me!"
                )
            self._notes_data = io.BytesIO(e.data)
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
        """Whether pattern has note data."""
        return "notes" in self._events

    def __init__(self):
        super().__init__()
        self._notes: List[Note] = []
