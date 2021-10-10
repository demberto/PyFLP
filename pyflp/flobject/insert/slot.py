from typing import Optional, ValuesView

from pyflp.flobject import FLObject
from pyflp.event import Event, WordEvent, DWordEvent, TextEvent, DataEvent
from pyflp.flobject.plugin import (
    Plugin,
    FNoteBook2,
    FSoftClipper,
    FBalance,
    Soundgoodizer,
    VSTPlugin,
)

from .enums import InsertSlotEvent

__all__ = ["InsertSlot"]


class InsertSlot(FLObject):
    max_count = 10  # TODO: Older versions had 8, maybe lesser as well

    # * Property
    @property
    def default_name(self) -> Optional[str]:
        """'Fruity Wrapper' for VST/AU plugins. Actual name for native plugins."""
        return getattr(self, "_default_name", None)

    @default_name.setter
    def default_name(self, value: str):
        self.setprop("default_name", value)

    @property
    def icon(self) -> Optional[int]:
        """Icon of the insert slot."""
        return getattr(self, "_icon", None)

    @icon.setter
    def icon(self, value: int):
        self.setprop("icon", value)

    @property
    def color(self) -> Optional[int]:
        """Color of the insert slot."""
        return getattr(self, "_color", None)

    @color.setter
    def color(self, value: int):
        self.setprop("color", value)

    @property
    def index(self) -> Optional[int]:
        """Index (FL12.3+) of a slot, occurs irrespective of whether the slot is used or not."""
        return getattr(self, "_index", None)

    @index.setter
    def index(self, value: int):
        assert value in range(0, InsertSlot.max_count + 1)
        self.setprop("index", value)

    @property
    def enabled(self) -> Optional[bool]:
        """Enabled state of the insert slot."""
        return getattr(self, "_enabled", None)

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    @property
    def mix(self) -> Optional[int]:
        """Dry/Wet mix of the insert slot."""
        return getattr(self, "_mix", None)

    @mix.setter
    def mix(self, value: int):
        self._mix = value

    @property
    def plugin(self) -> Optional[Plugin]:
        return getattr(self, "_plugin", None)

    @plugin.setter
    def plugin(self, value: Plugin):
        self._plugin = value

    @property
    def new(self) -> Optional[bytes]:
        return getattr(self, "_new", None)

    @new.setter
    def new(self, value: bytes):
        self._new = value

    @property
    def name(self) -> Optional[str]:
        """User-given/preset name for stock plugins. Factory name
        for VST/AU plugins, if a user-given name is not given."""
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self.setprop("name", value)

    # * Parsing logic
    def _parse_word_event(self, e: WordEvent) -> None:
        if e.id == InsertSlotEvent.Index:
            self.parse_uint16_prop(e, "index")

    def _parse_dword_event(self, e: DWordEvent):
        if e.id == InsertSlotEvent.Color:
            self.parse_uint32_prop(e, "color")
        elif e.id == InsertSlotEvent.Icon:
            self.parse_uint32_prop(e, "icon")

    def _parse_text_event(self, e: TextEvent):
        if e.id == InsertSlotEvent.DefaultName:
            self.parse_str_prop(e, "default_name")
        elif e.id == InsertSlotEvent.Name:
            self.parse_str_prop(e, "name")

    def _parse_data_event(self, e: DataEvent):
        if e.id == InsertSlotEvent.PluginNew:
            self._events["new"] = e
            self._new = e.data
            # TODO: Parsing similar to ChannelEventID.New (same e IDs)
        elif e.id == InsertSlotEvent.Plugin:
            self._events["plugin"] = e

            if self.default_name == "Fruity soft clipper":
                self._plugin = FSoftClipper()
            elif self.default_name == "Fruity NoteBook 2":
                self._plugin = FNoteBook2()
            elif self.default_name == "Fruity Balance":
                self._plugin = FBalance()
            elif self.default_name == "Soundgoodizer":
                self._plugin = Soundgoodizer()
            elif self.default_name == "Fruity Wrapper":
                self._plugin = VSTPlugin()

            if self.plugin:
                self._plugin.parse_event(e)

    def save(self) -> ValuesView[Event]:
        events = super().save()

        new_event = self._events.get("new")
        if new_event:
            new_event.dump(self._new)

        if self.plugin:
            self.plugin.save()

        return events

    # region Utility methods
    def is_used(self) -> bool:
        """Whether a slot is used or empty."""
        return True if self._events.get("new") else False

    def __init__(self):
        super().__init__()
        assert (
            InsertSlot._count <= InsertSlot.max_count
        ), f"InsertSlot count: {InsertSlot._count} exceeds max_count: {InsertSlot.max_count}"
