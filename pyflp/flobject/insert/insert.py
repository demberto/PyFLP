import enum
from typing import List, Optional, Union
import dataclasses

from pyflp.event import Event, WordEvent, DWordEvent, TextEvent, DataEvent
from pyflp.flobject import FLObject

from .enums import InsertEvent, InsertSlotEvent
from .slot import InsertSlot

from bytesioex import BytesIOEx  # type: ignore

__all__ = ["Insert"]


class InsertFlags(enum.IntFlag):
    None_ = 0
    ReversePolarity = 1 << 0
    SwapLeftRight = 1 << 1
    U2 = 1 << 2
    Enabled = 1 << 3
    DisableThreadedProcessing = 1 << 4
    U5 = 1 << 5
    DockMiddle = 1 << 6
    DockRight = 1 << 7
    U8 = 1 << 8
    U9 = 1 << 9
    ShowSeparator = 1 << 10
    Lock = 1 << 11
    Solo = 1 << 12
    U13 = 1 << 13
    U14 = 1 << 14
    U15 = 1 << 15


@dataclasses.dataclass(init=False)
class InsertEQ:
    low_level: int
    band_level: int
    high_level: int
    low_freq: int
    band_freq: int
    high_freq: int
    low_q: int
    band_q: int
    high_q: int


class Insert(FLObject):
    _count = 0
    max_count = 0  # Will be a given a value by ProjectParser

    # region Properties
    @property
    def name(self) -> Optional[str]:
        """Name of the insert. Event not stored if name not set."""
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        self._setprop("name", value)

    @property
    def routing(self) -> List[bool]:
        """An order collection of booleans, representing how this `Insert` is routed.
        So if the sequence is [0, 1, 1, 0, ...], then this `Insert` is routed to Insert 2, 3.
        """
        return getattr(self, "_routing", [])

    @routing.setter
    def routing(self, value: List[bool]):
        self._setprop("routing", bytes(value))

    @property
    def icon(self) -> Optional[int]:
        """Icon of the insert. Default event is not stored."""
        return getattr(self, "_icon", None)

    @icon.setter
    def icon(self, value: int):
        self._setprop("icon", value)

    @property
    def input(self) -> Optional[int]:
        """Default event is stored."""
        return getattr(self, "_input", None)

    @input.setter
    def input(self, value: int):
        self._setprop("input", value)

    @property
    def output(self) -> Optional[int]:
        """Default event is stored."""
        return getattr(self, "_output", None)

    @output.setter
    def output(self, value: int):
        self._setprop("output", value)

    @property
    def color(self) -> Optional[int]:
        """Color of the insert. Default event is not stored."""
        return getattr(self, "_color", None)

    @color.setter
    def color(self, value: int):
        self._setprop("color", value)

    @property
    def flags(self) -> Union[InsertFlags, int, None]:
        """Stored in a `InsertEvent.Parameters` event. Default event is stored"""
        return getattr(self, "_flags", None)

    @flags.setter
    def flags(self, value: Union[InsertFlags, int]):
        self._parameters_data.seek(0)
        self._parameters_data.write(value.to_bytes(4, "little"))
        self._flags = value

    @property
    def slots(self) -> List[InsertSlot]:
        """Holds `pyflp.flobject.insert.insert_slot.InsertSlot` objects (empty and used)."""
        return getattr(self, "_slots", [])

    @slots.setter
    def slots(self, value: List[InsertSlot]):
        self._slots = value

    @property
    def enabled(self) -> Optional[bool]:
        """Whether `pyflp.flobject.insert.insert.Insert` is enabled in the mixer.
        Obatined from `pyflp.flobject.insert.insert_params_event.InsertParamsEvent`."""
        return getattr(self, "_enabled", None)

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    @property
    def volume(self) -> Optional[int]:
        """Fader value. Obatined from `pyflp.flobject.insert.insert_params_event.InsertParamsEvent`."""
        return getattr(self, "_volume", None)

    @volume.setter
    def volume(self, value: int):
        self._volume = value

    @property
    def pan(self) -> Optional[int]:
        """Obatined from `pyflp.flobject.insert.insert_params_event.InsertParamsEvent`."""
        return getattr(self, "_pan", None)

    @pan.setter
    def pan(self, value: int):
        self._pan = value

    @property
    def stereo_separation(self) -> Optional[int]:
        """Obatined from `pyflp.flobject.insert.insert_params_event.InsertParamsEvent`."""
        return getattr(self, "_stereo_separation", None)

    @stereo_separation.setter
    def stereo_separation(self, value: int):
        self._stereo_separation = value

    @property
    def eq(self) -> Optional[InsertEQ]:
        """3-band post EQ. Obatined from `pyflp.flobject.insert.insert_params_event.InsertParamsEvent`."""
        return getattr(self, "_eq", None)

    @eq.setter
    def eq(self, value: InsertEQ):
        self._eq = value

    @property
    def route_volumes(self) -> List[int]:
        """Like `routing`, stores an ordered collection of route volumes.
        Obatined from `pyflp.flobject.insert.insert_params_event.InsertParamsEvent`."""
        return getattr(self, "_route_volumes", [])

    @route_volumes.setter
    def route_volumes(self, value: List[int]):
        assert len(value) == Insert.max_count
        self._route_volumes = value

    @property
    def locked(self) -> Optional[bool]:
        """Obatined from `pyflp.flobject.insert.insert_params_event.InsertParamsEvent`."""
        return getattr(self, "_locked", None)

    @locked.setter
    def locked(self, value: bool):
        self._parameters_data.seek(4)
        v = 1 if value else 0
        self._parameters_data.write(v.to_bytes(4, "little"))
        self._locked = value

    # * Parsing logic
    def parse_event(self, event: Event) -> None:
        if event.id == InsertSlotEvent.Index:
            self._cur_slot.parse_event(event)  # type: ignore
            self._slots.append(self._cur_slot)  # type: ignore
            if len(self._slots) < InsertSlot.max_count:
                self._cur_slot = InsertSlot()
        elif event.id in (
            InsertSlotEvent.Color,
            InsertSlotEvent.Icon,
            InsertSlotEvent.PluginNew,
            InsertSlotEvent.Plugin,
            InsertSlotEvent.DefaultName,
            InsertSlotEvent.Name,
        ):
            self._cur_slot.parse_event(event)
        else:
            return super().parse_event(event)

    def _parse_word_event(self, event: WordEvent):
        if event.id == InsertEvent.Icon:
            self._parse_uint16_prop(event, "icon")

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == InsertEvent.Input:
            self._parse_int32_prop(event, "input")
        elif event.id == InsertEvent.Color:
            self._parse_uint32_prop(event, "color")
        elif event.id == InsertEvent.Output:
            self._parse_int32_prop(event, "output")

    def _parse_text_event(self, event: TextEvent):
        if event.id == InsertEvent.Name:
            self._parse_str_prop(event, "name")

    def _parse_data_event(self, event: DataEvent):
        if event.id == InsertEvent.Parameters:
            self._events["parameters"] = event
            self._parameters_data = BytesIOEx(event.data)
            flags = self._parameters_data.read_I()
            try:
                self._flags = InsertFlags(flags)
            except AttributeError:
                self._flags = flags
                self._log.error(
                    f"Flags (value: {flags}) could not be converted to InsertFlags"
                )
            self._locked = True if self._parameters_data.read_i() else False
            # 4 more bytes
        elif event.id == InsertEvent.Routing:
            bool_list = []
            for byte in event.data:
                boolean = False if byte == "\x00" else True
                bool_list.append(boolean)
            self._parseprop(event, "routing", bool_list)

    def save(self) -> List[Event]:  # type: ignore
        events = list(super().save())

        # Insert data events
        self._parameters_data.seek(0)
        self._events["parameters"].dump(self._parameters_data.read())

        # Insert slot events
        if self.slots:
            for slot in self.slots:
                events.extend(slot.save())

        return events

    def __init__(self):
        super().__init__()
        InsertSlot._count = 0
        self._slots: List[InsertSlot] = []
        self._cur_slot = InsertSlot()
        self._eq = InsertEQ()
        self._route_volumes = [int()] * Insert.max_count
        assert Insert._count <= Insert.max_count, f"Insert count: {self._count}"
        self.index = Insert._count - 2
