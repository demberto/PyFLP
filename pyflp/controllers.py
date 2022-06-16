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
from typing import Optional  # , Union

from bytesioex import BytesIOEx

from pyflp._event import EventIDType, _DataEvent

# from pyflp.exceptions import OperationNotPermittedError
from pyflp._flobject import _FLObject
from pyflp._properties import _BoolProperty, _EnumProperty, _IntProperty, _UIntProperty
from pyflp.constants import DATA

__all__ = ["RemoteController", "RemoteControllerEvent"]


class Controller(_FLObject):
    pass


class RemoteController(Controller):
    ID = DATA + 19

    class Kind(enum.Enum):
        Channel = enum.auto()
        InsertSlot = enum.auto()

    kind: Kind = _EnumProperty(Kind)
    """Whether controller is for a channel or insert slot."""

    param: Optional[int] = _UIntProperty()
    """The ID of the plugin parameter to which controller is linked to."""

    is_vst_param: Optional[bool] = _BoolProperty()
    """Whether `parameter` is linked to a VST or not. `None` for
    controllers linked to a plugin parameter on an insert slot."""

    insert: Optional[int] = _IntProperty()
    """Insert index of the `slot_id`."""

    slot: Optional[int] = _UIntProperty()
    """Slot index of the plugin whose parameter is linked to controller."""

    def parse_event(self, e: "RemoteControllerEvent") -> None:
        self.__rce = self._events["rce"] = e
        self._kind = e.kind
        if self._kind == RemoteController.Kind.Channel:
            self._param = e.param
            self._is_vst_param = e.is_vst_param
        else:
            self._insert = e.insert
            self._slot = e.slot


class RemoteControllerEvent(_DataEvent):
    CHUNK_SIZE = 20

    def __init__(self, index: int, id_: EventIDType, data: bytes) -> None:
        super().__init__(index, id_, data)
        r = BytesIOEx(data)
        self.u1 = r.read_H()
        self.u2 = r.read_B()
        self.u3 = r.read_B()
        self.__param = r.read_H()
        self.__dest = r.read_h()
        self.u4 = r.read_Q()

        if self.__dest & 2000 == 0:
            self.kind = RemoteController.Kind.Channel
            self.param = self.__param & 0x7FFF
            self.is_vst_param = True if self.__param & 0x8000 > 0 else False
        else:
            self.kind = RemoteController.Kind.InsertSlot
            self.insert = (self.__dest & 0x0FF0) >> 6
            self.slot = self.__dest & 0x003F


# def dump(self, n: str, v: Union[RemoteController.Kind, int, bool]):
#     r = self.__r
#     if n == "kind":
#         pass
#     elif n == "param":
#         if self.kind != RemoteController.Kind.Channel:
#             raise OperationNotPermittedError(
#                 "'param' cannot be set when controller is linked to a channel."
#             )

#     elif n == "is_vst_param":
#         if self.kind != RemoteController.Kind.Channel:
#             raise OperationNotPermittedError(
#                 "'is_vst_param' cannot be set when controller is linked to channel."
#             )
#     elif n == "insert":
#         if self.kind != RemoteController.Kind.InsertSlot:
#             raise OperationNotPermittedError(
#                 "'insert' cannot be set when controller is linked to an insert slot."
#             )
#     elif n == "slot":
#         if self.kind != RemoteController.Kind.InsertSlot:
#             raise OperationNotPermittedError(
#                 "'slot' cannot be set when controller is linked to an insert slot."
#             )
#     r.seek(0)
#     super().dump(r.read())


# class MIDIControllerEvent(DataEvent):
#     pass


# class MIDIController(Controller):
#     pass
