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

"""Contains the types used by MIDI and remote controllers."""

from __future__ import annotations

import enum
from typing import cast

from ._base import (
    DATA,
    EventEnum,
    ModelReprMixin,
    SingleEventModel,
    StructBase,
    StructEventBase,
)

__all__ = ["RemoteController"]


class _RemoteControllerStruct(StructBase):
    PROPS = {
        "_u1": 2,  # 2
        "_u2": 1,  # 3
        "_u3": 1,  # 4
        "parameter_data": "H",  # 6
        "destination_data": "h",  # 8
        "_u4": 8,  # 16
        "_u5": 4,  # 20
    }


class RemoteControllerEvent(StructEventBase):
    STRUCT = _RemoteControllerStruct


@enum.unique
class ControllerID(EventEnum):
    Remote = (DATA + 19, RemoteControllerEvent)


class RemoteController(SingleEventModel, ModelReprMixin):
    """![](https://bit.ly/3S0i4Zf)

    *New in FL Studio v3.3.0*.
    """

    @property
    def parameter(self) -> int | None:
        """The ID of the plugin parameter to which controller is linked to."""
        value = cast(_RemoteControllerStruct, self._event)["parameter_data"]
        if value is not None:
            return value & 0x7FFF

    @property
    def controls_vst(self) -> bool | None:
        """Whether `parameter` is linked to a VST plugin.

        None when linked to a plugin parameter on an insert slot.
        """
        value = cast(_RemoteControllerStruct, self._event)["parameter_data"]
        if value is not None:
            return (value & 0x8000) > 0
