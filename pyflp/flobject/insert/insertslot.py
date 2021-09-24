from typing import Optional, ValuesView

from pyflp.flobject import FLObject
from pyflp.event import (
    Event,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)
from pyflp.flobject.plugin import (
    Plugin,
    FNoteBook2,
    FSoftClipper,
    FBalance,
    Soundgoodizer,
    VSTPlugin
)
from pyflp.flobject.insert.event_id import InsertSlotEventID

__all__ = ['InsertSlot']

class InsertSlot(FLObject):
    max_count = 10  # TODO: Older versions had 8, maybe lesser as well

    #region Property
    @property
    def default_name(self) -> Optional[str]:
        """'Fruity Wrapper' for VST/AU plugins. Actual name for native plugins."""
        return getattr(self, '_default_name', None)

    @default_name.setter
    def default_name(self, value: str):
        self.setprop('default_name', value)

    @property
    def icon(self) -> Optional[int]:
        return getattr(self, '_icon', None)

    @icon.setter
    def icon(self, value: int):
        self.setprop('icon', value)

    @property
    def color(self) -> Optional[int]:
        return getattr(self, '_color', None)

    @color.setter
    def color(self, value: int):
        self.setprop('color', value)

    @property
    def index(self) -> Optional[int]:
        """Index (FL12.3+) of a slot, occurs irrespective of whether the slot is used or not."""
        return getattr(self, '_index', None)

    @index.setter
    def index(self, value: int):
        assert value in range(0, InsertSlot.max_count + 1)
        self.setprop('index', value)

    @property
    def enabled(self) -> Optional[bool]:
        return getattr(self, '_enabled', None)

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    @property
    def mix(self) -> Optional[int]:
        """Dry/Wet mix"""
        return getattr(self, '_mix', None)

    @mix.setter
    def mix(self, value: int):
        self._mix = value

    @property
    def plugin(self) -> Optional[Plugin]:
        return getattr(self, '_plugin', None)

    @plugin.setter
    def plugin(self, value: Plugin):
        self._plugin = value

    @property
    def new(self) -> Optional[bytes]:
        return getattr(self, '_new', None)

    @new.setter
    def new(self, value: bytes):
        self._new = value
    #endregion

    #region Parsing logic
    def _parse_word_event(self, event: WordEvent) -> None:
        if event.id == InsertSlotEventID.Index:
            self.parse_uint16_prop(event, 'index')

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == InsertSlotEventID.Color:
            self.parse_uint32_prop(event, 'color')
        elif event.id == InsertSlotEventID.Icon:
            self.parse_uint32_prop(event, 'icon')

    def _parse_text_event(self, event: TextEvent):
        if event.id == InsertSlotEventID.DefaultName:
            self.parse_str_prop(event, 'default_name')

    def _parse_data_event(self, event: DataEvent):
        if event.id == InsertSlotEventID.PluginNew:
            self._events['new'] = event
            self._new = event.data
            # TODO: Parsing similar to ChannelEventID.New (same event IDs)
        elif event.id == InsertSlotEventID.Plugin:
            self._events['plugin'] = event
            
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
                self._plugin.parse(event)
    #endregion

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.debug(f"save() called, index: {self.index}")

        new_event = self._events.get('new')
        if new_event:
            self._log.info(f"InsertSlotEventID.PluginNew new size: {len(self._new)} bytes")
            new_event.dump(self._new)

        if self.plugin:
            self.plugin.save()

        return super().save()

    #region Utility methods
    def is_used(self) -> bool:
        """Whether a slot is used or empty. Decided by the presence of `InsertSlotEventID.New` event"""
        return True if self._events.get('new') else False
    #endregion

    def __init__(self):
        super().__init__()
        assert InsertSlot._count <= InsertSlot.max_count, \
            f"InsertSlot count: {InsertSlot._count} exceeds max_count: {InsertSlot.max_count}"