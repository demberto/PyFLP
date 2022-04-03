import enum
from typing import Optional, ValuesView

import colour

from pyflp.constants import DATA, DWORD, TEXT, WORD
from pyflp.event import DataEvent, TextEvent, WordEvent, _DWordEventType, _EventType
from pyflp.flobject import _FLObject
from pyflp.plugin.effects.balance import FBalance
from pyflp.plugin.effects.fast_dist import FFastDist
from pyflp.plugin.effects.notebook2 import FNoteBook2
from pyflp.plugin.effects.send import FSend
from pyflp.plugin.effects.soft_clipper import FSoftClipper
from pyflp.plugin.effects.soundgoodizer import Soundgoodizer
from pyflp.plugin.effects.stereo_enhancer import FStereoEnhancer
from pyflp.plugin.plugin import _Plugin
from pyflp.plugin.vst import VSTPlugin
from pyflp.properties import (
    _BoolProperty,
    _ColorProperty,
    _IntProperty,
    _StrProperty,
    _UIntProperty,
)
from pyflp.validators import _IntValidator, _UIntValidator


class InsertSlot(_FLObject):
    max_count = 10  # TODO: Older versions had 8, maybe lesser as well

    def __init__(self):
        super().__init__()
        assert (
            self._count <= self.max_count
        ), f"InsertSlot count={self._count} exceeds max_count={self.max_count}"

    @enum.unique
    class EventID(enum.IntEnum):
        """Event IDs used by `InsertSlot`."""

        DefaultName = TEXT + 9
        """See `InsertSlot.default_name`."""

        Name = TEXT + 11
        """See `InsertSlot.name`. Not stored if slot is empty."""

        # Plugin wrapper data, windows pos of plugin etc, currently
        # selected plugin wrapper page; minimized, closed or not
        PluginNew = DATA + 4  # TODO
        """See `InsertSlot.new`. Not stored if slot is empty."""

        Icon = DWORD + 27
        """See `InsertSlot.icon`. Not stored if slot is empty."""

        Color = DWORD
        """See `InsertSlot.color`. Not stored if slot is empty."""

        Plugin = DATA + 5
        """See `InsertSlot.plugin`. Not stored if slot is empty."""

        Index = WORD + 34
        """See `InsertSlot.index`. New in FL 12.3."""

    # * Properties
    default_name: Optional[str] = _StrProperty()
    """'Fruity Wrapper' for VST/AU plugins. Factory name for native plugins."""

    icon: Optional[int] = _IntProperty()
    """Icon."""

    color: Optional[colour.Color] = _ColorProperty()
    """Color."""

    index: Optional[int] = _UIntProperty(_IntValidator(0, max_count))
    """Index (FL12.3+); occurs irrespective of whether slot is used or not."""

    enabled: Optional[bool] = _BoolProperty()
    """Enabled state of the insert slot. Obtained from `InsertParamsEvent`."""

    mix: Optional[int] = _UIntProperty(_UIntValidator(12800))
    """Dry/Wet mix of the insert slot. Obtained from `InsertParamsEvent`.
    Min: 0 (0%), Max: 12800 (100%), Default: 12800 (100%)."""

    @property
    def plugin(self) -> Optional[_Plugin]:
        """Plugin parameters and preset data, this
        is what uses the most space typically."""
        return getattr(self, "_plugin", None)

    @plugin.setter
    def plugin(self, value: _Plugin):
        self._plugin = value

    @property
    def new(self) -> Optional[bytes]:
        return getattr(self, "_new", None)

    @new.setter
    def new(self, value: bytes):
        self._new = value

    name: Optional[str] = _StrProperty()
    """User-given/preset name for stock plugins. Factory name
    for VST/AU plugins, if a user-given name is not given."""

    # * Parsing logic
    def _parse_word_event(self, e: WordEvent) -> None:
        if e.id == InsertSlot.EventID.Index:
            self._parse_H(e, "index")

    def _parse_dword_event(self, e: _DWordEventType):
        if e.id == InsertSlot.EventID.Color:
            self._parse_color(e, "color")
        elif e.id == InsertSlot.EventID.Icon:
            self._parse_I(e, "icon")

    def _parse_text_event(self, e: TextEvent):
        if e.id == InsertSlot.EventID.DefaultName:
            self._parse_s(e, "default_name")
        elif e.id == InsertSlot.EventID.Name:
            self._parse_s(e, "name")

    def _parse_data_event(self, e: DataEvent):
        if e.id == InsertSlot.EventID.PluginNew:
            self._events["new"] = e
            self._new = e.data
            # TODO: Parsing similar to ChannelEventID.New (same IDs)
        elif e.id == InsertSlot.EventID.Plugin:
            n = self.default_name
            if n == "Fruity Soft Clipper":
                plugin = FSoftClipper()
            elif n == "Fruity NoteBook 2":
                plugin = FNoteBook2()
            elif n == "Fruity Balance":
                plugin = FBalance()
            elif n == "Soundgoodizer":
                plugin = Soundgoodizer()
            elif n == "Fruity Fast Dist":
                plugin = FFastDist()
            elif n == "Fruity Stereo Enhancer":
                plugin = FStereoEnhancer()
            elif n == "Fruity Send":
                plugin = FSend()
            elif n == "Fruity Wrapper":
                plugin = VSTPlugin()
            else:
                plugin = _Plugin()
            self._parse_flobject(e, "plugin", plugin)

    def _save(self) -> ValuesView[_EventType]:
        events = super()._save()

        new_event = self._events.get("new")
        if new_event:
            new_event.dump(self._new)

        if self.plugin:
            self.plugin._save()

        return events

    # * Utility methods
    def is_used(self) -> bool:
        """Whether a slot is used or empty."""
        return True if self._events.get("new") else False

    def get_name(self) -> Optional[str]:
        """Returns the name that will be shown in FL."""
        if self.name:
            return self.name
        return self.default_name
