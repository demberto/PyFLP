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

import struct
import warnings
from typing import List

from bytesioex import BytesIOEx

from pyflp._event import EventIDType, _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _IntProperty, _UIntProperty

__all__ = ["PatternNote", "PatternNotesEvent"]


class PatternNote(_FLObject):
    """Represents a note (MIDI event) in a `Pattern`."""

    # * Properties
    position: int = _UIntProperty()
    """Position from pattern start (i.e. 0).
    Proportional to project PPQ. See `Misc.ppq`."""

    flags: int = _UIntProperty()
    """Miscellaneous note related flags. TODO"""

    rack_channel: int = _UIntProperty()
    """Which `Channel` this note is for; since, a single
    pattern can hold notes for multiple channels."""

    duration: int = _UIntProperty()
    """Duration. Proportional to project PPQ. See `Misc.ppq`."""

    key: int = _UIntProperty()
    """The note itself. Single notes: 0-131 (for C0-B10).
    Yet needs 4 bytes, to save stamped chords/scales."""

    fine_pitch: int = _IntProperty(min_=-128, max_=127)
    """Min: -128 (-100 cents), Max: 127 (+100 cents)."""

    u1: int = _IntProperty()
    """TODO: Unknown parameter."""

    release: int = _UIntProperty(max_=128)
    """Min: 0, Max: 128."""

    # See issue #8
    midi_channel: int = _UIntProperty()
    """For note colors, min: 0, max: 15.

    128 for MIDI dragged into the piano roll.
    """

    pan: int = _IntProperty(min_=-64, max_=64)
    """Min: -64, Max: 64."""

    velocity: int = _UIntProperty(max_=128)
    """Min: 0, Max: 128."""

    mod_x: int = _UIntProperty()
    """Mod X. Most probably filter cutoff."""

    mod_y: int = _UIntProperty()
    """Mod Y. Most probably filter resonance."""

    def _save(self) -> bytes:
        return struct.pack(
            "I2H2I2b2Bb3B",
            self.position,
            self.flags,
            self.rack_channel,
            self.duration,
            self.key,
            self.fine_pitch,
            self.u1,
            self.release,
            self.midi_channel,
            self.pan,
            self.velocity,
            self.mod_x,
            self.mod_y,
        )


class PatternNotesEvent(_DataEvent):
    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        self.notes: List[PatternNote] = []
        if len(data) % 24 != 0:  # pragma: no cover
            warnings.warn("Unexpected data size; expected a divisible of 24.")
            return
        r = BytesIOEx(data)
        while True:
            position = r.read_I()  # 4
            if position is None:
                break
            n = PatternNote()
            n.position = position
            n.flags = r.read_H()  # 6
            n.rack_channel = r.read_H()  # 8
            n.duration = r.read_I()  # 12
            n.key = r.read_I()  # 16
            n.fine_pitch = r.read_b()  # 17
            n.u1 = r.read_b()  # 18
            n.release = r.read_B()  # 19
            n.midi_channel = r.read_B()  # 20
            n.pan = r.read_b()  # 21
            n.velocity = r.read_B()  # 22
            n.mod_x = r.read_B()  # 23
            n.mod_y = r.read_B()  # 24
            self.notes.append(n)

    def __repr__(self) -> str:
        return f"<PatternNotesEvent: {len(self.notes)} notes>"
