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

"""Contains the types used by MIDI and remote ("internal") controllers."""

from __future__ import annotations

import enum
from typing import cast

import construct as c

from pyflp._events import DATA, EventEnum, StructEventBase
from pyflp._models import EventModel, ModelReprMixin

__all__ = ["RemoteController"]


class MIDIControllerEvent(StructEventBase):
    STRUCT = c.Struct("_u1" / c.GreedyBytes)


class RemoteControllerEvent(StructEventBase):
    STRUCT = c.Struct(
        "_u1" / c.Optional(c.Bytes(2)),  # 2
        "_u2" / c.Optional(c.Byte),  # 3
        "_u3" / c.Optional(c.Byte),  # 4
        "parameter_data" / c.Optional(c.Int16ul),  # 6
        "destination_data" / c.Optional(c.Int16sl),  # 8
        "_u4" / c.Optional(c.Bytes(8)),  # 16
        "_u5" / c.Optional(c.Bytes(4)),  # 20
    ).compile()


@enum.unique
class ControllerID(EventEnum):
    MIDI = (DATA + 18, MIDIControllerEvent)
    Remote = (DATA + 19, RemoteControllerEvent)


class RemoteController(EventModel, ModelReprMixin):
    """![](https://bit.ly/3S0i4Zf)

    *New in FL Studio v3.3.0*.
    """

    @property
    def parameter(self) -> int | None:
        """The ID of the plugin parameter to which controller is linked to."""
        if (
            value := cast(StructEventBase, self.events.first(ControllerID.Remote))["parameter_data"]
            is not None
        ):
            return value & 0x7FFF

    @property
    def controls_vst(self) -> bool | None:
        """Whether `parameter` is linked to a VST plugin.

        None when linked to a plugin parameter on an insert slot.
        """
        if (
            value := cast(StructEventBase, self.events.first(ControllerID.Remote))["parameter_data"]
            is not None
        ):
            return (value & 0x8000) > 0
