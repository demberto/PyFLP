# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

import enum
from typing import List, Optional

import colour

from pyflp._event import (
    DataEventType,
    DWordEventType,
    EventType,
    TextEventType,
    WordEventType,
)
from pyflp._flobject import _FLObject
from pyflp._properties import (
    _BoolProperty,
    _ColorProperty,
    _IntProperty,
    _StrProperty,
    _UIntProperty,
)
from pyflp.constants import DATA, DWORD, TEXT, WORD
from pyflp.plugin._plugin import _Plugin
from pyflp.plugin.effects.balance import FBalance
from pyflp.plugin.effects.fast_dist import FFastDist
from pyflp.plugin.effects.notebook2 import FNoteBook2
from pyflp.plugin.effects.send import FSend
from pyflp.plugin.effects.soft_clipper import FSoftClipper
from pyflp.plugin.effects.soundgoodizer import Soundgoodizer
from pyflp.plugin.effects.stereo_enhancer import FStereoEnhancer
from pyflp.plugin.vst import VSTPlugin


class InsertSlot(_FLObject):
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

    color: Optional[colour.Color] = _ColorProperty()

    index: Optional[int] = _UIntProperty()
    """Index (FL12.3+); occurs irrespective of whether slot is used or not."""

    enabled: Optional[bool] = _BoolProperty()
    """Enabled state of the insert slot. Obtained from `InsertParamsEvent`."""

    mix: Optional[int] = _UIntProperty(max_=12800)
    """Dry/Wet mix of the insert slot. Obtained from `InsertParamsEvent`.
    Min: 0 (0%), Max: 12800 (100%), Default: 12800 (100%)."""

    @property
    def plugin(self) -> Optional[_Plugin]:
        """Plugin parameters and preset data, this
        is what uses the most space typically."""
        return getattr(self, "_plugin", None)

    @plugin.setter
    def plugin(self, value: _Plugin) -> None:
        self._plugin = value

    @property
    def new(self) -> Optional[bytes]:
        return getattr(self, "_new", None)

    @new.setter
    def new(self, value: bytes) -> None:
        self._new = value

    name: Optional[str] = _StrProperty()
    """User-given/preset name for stock plugins. Factory name
    for VST/AU plugins, if a user-given name is not given."""

    # * Parsing logic
    def _parse_word_event(self, e: WordEventType) -> None:
        if e.id_ == InsertSlot.EventID.Index:
            self._parse_H(e, "index")

    def _parse_dword_event(self, e: DWordEventType) -> None:
        if e.id_ == InsertSlot.EventID.Color:
            self._parse_color(e, "color")
        elif e.id_ == InsertSlot.EventID.Icon:
            self._parse_I(e, "icon")

    def _parse_text_event(self, e: TextEventType) -> None:
        if e.id_ == InsertSlot.EventID.DefaultName:
            self._parse_s(e, "default_name")
        elif e.id_ == InsertSlot.EventID.Name:
            self._parse_s(e, "name")

    def _parse_data_event(self, e: DataEventType) -> None:
        if e.id_ == InsertSlot.EventID.PluginNew:
            self._events["new"] = e
            self._new = e.data
            # TODO: Parsing similar to ChannelEventID.New (same IDs)
        elif e.id_ == InsertSlot.EventID.Plugin:
            n = self.default_name
            if n == "Fruity Soft Clipper":
                plugin = FSoftClipper()
            elif n == "Fruity NoteBook 2":
                plugin = FNoteBook2()
            elif n == "Fruity Balance":
                plugin = FBalance()
            elif n == "Soundgoodizer":
                plugin = Soundgoodizer()
            elif n == "Fruity Stereo Enhancer":
                plugin = FStereoEnhancer()
            elif n == "Fruity Fast Dist":
                plugin = FFastDist()
            elif n == "Fruity Send":
                plugin = FSend()
            elif n == "Fruity Wrapper":
                plugin = VSTPlugin()
            else:
                plugin = _Plugin()
            self._parse_flobject(e, "plugin", plugin)

    def _save(self) -> List[EventType]:
        new_event = self._events.get("new")
        if new_event:
            new_event.dump(self._new)

        if self.plugin:
            self.plugin._save()

        return super()._save()

    # * Utility methods
    def is_used(self) -> bool:
        """Whether a slot is used or empty."""
        return True if self._events.get("new") else False

    def get_name(self) -> Optional[str]:
        """Returns the name that will be shown in FL."""
        return self.name or self.default_name
