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
import io
import zipfile
from pathlib import Path
from typing import List, Optional, Set, Union

from bytesioex import BytesIOEx

from pyflp._event import (
    EventIDType,
    EventList,
    EventType,
    _ByteEvent,
    _ColorEvent,
    _DataEvent,
    _DWordEvent,
    _TextEvent,
    _WordEvent,
)
from pyflp._flobject import MaxInstances
from pyflp._utils import FLVersion
from pyflp.arrangement.arrangement import Arrangement
from pyflp.arrangement.playlist import Playlist
from pyflp.arrangement.timemarker import TimeMarker
from pyflp.arrangement.track import Track, TrackDataEvent
from pyflp.channel.channel import Channel
from pyflp.channel.delay import ChannelDelayEvent
from pyflp.channel.envlfo import ChannelEnvelopeLFOEvent
from pyflp.channel.filter import Filter
from pyflp.channel.fx import ChannelFX
from pyflp.channel.level_offsets import ChannelLevelOffsetsEvent
from pyflp.channel.levels import ChannelLevelsEvent
from pyflp.channel.parameters import ChannelParametersEvent
from pyflp.channel.polyphony import ChannelPolyphonyEvent
from pyflp.channel.tracking import ChannelTrackingEvent
from pyflp.constants import (
    BYTE,
    DATA,
    DATA_MAGIC,
    DATA_TEXT_EVENTS,
    DWORD,
    HEADER_MAGIC,
    HEADER_SIZE,
    TEXT,
    WORD,
)
from pyflp.controllers import RemoteController, RemoteControllerEvent
from pyflp.exceptions import InvalidHeaderSizeError, InvalidMagicError
from pyflp.insert.event import InsertParamsEvent
from pyflp.insert.insert import Insert
from pyflp.insert.parameters import InsertParametersEvent
from pyflp.insert.slot import InsertSlot
from pyflp.misc import Misc
from pyflp.pattern.controller import PatternControllersEvent
from pyflp.pattern.note import PatternNotesEvent
from pyflp.pattern.pattern import Pattern
from pyflp.plugin.vst import VSTPluginEvent
from pyflp.project import Project

__all__ = ["Parser"]

INSERT_EVENTS: List[enum.IntEnum] = []
for en in (Insert.EventID, InsertSlot.EventID):
    INSERT_EVENTS.extend(en.__members__.values())

ARRANGEMENT_EVENTS: List[enum.IntEnum] = []
for en in (Arrangement.EventID, Track.EventID, Playlist.EventID):
    ARRANGEMENT_EVENTS.extend(en.__members__.values())

CHANNEL_EVENTS: List[enum.IntEnum] = []
for en in (Channel.EventID, ChannelFX.EventID):
    CHANNEL_EVENTS.extend(en.__members__.values())

COLOR_EVENTS = (
    Channel.EventID.Color,
    Pattern.EventID.Color,
    Insert.EventID.Color,
    InsertSlot.EventID.Color,
)


class Parser:
    """FL Studio project file parser."""

    def __init__(self):
        self.__events = EventList()
        self.__channel_count = 0
        self.__max_counts = MaxInstances()
        self.__fl_version: Optional[FLVersion] = None
        self.__uses_unicode = True

        # Timemarkers can occur anywhere before an arrangement
        # In that case, store them here temporarily until an
        # arrangement gets initialised.
        self.__tms: List[TimeMarker] = []

        # See `__parse_pattern` below for details.
        self.__pat_indexes: Set[int] = set()

        # If current plugin default name is "Fruity Wrapper", this is True.
        # `__build_event_store` will instantiate `VSTPluginEvent`.
        self.__cur_plug_is_vst = False

    def __build_event_store(self) -> None:
        """Gathers all events into a single list."""

        def add_dwordevent(id_: EventIDType, buf: bytes) -> None:
            if id_ in COLOR_EVENTS:
                typ = _ColorEvent
            else:
                typ = _DWordEvent
            self.__events.append(typ, id_, buf)

        def add_textevent(id_: EventIDType, buf: bytes) -> None:
            if id_ == Misc.EventID.Version:
                self.__fl_version = FLVersion(_TextEvent.as_ascii(buf))
                if self.__fl_version.as_float() < 11.5:
                    self.__uses_unicode = False
            ev = self.__events.create(_TextEvent, id_, buf, self.__uses_unicode)
            if (
                id_ in (InsertSlot.EventID.DefaultName, Channel.EventID.DefaultName)
                and ev.to_str() == "Fruity Wrapper"
            ):
                self.__cur_plug_is_vst = True
            self.__events.append_event(ev)

        def add_dataevent(id_: EventIDType, buf: bytes) -> None:
            if id_ == Track.EventID.Data:
                typ = TrackDataEvent
            elif id_ == Channel.EventID.Delay:
                typ = ChannelDelayEvent
            elif id_ == Channel.EventID.Polyphony:
                typ = ChannelPolyphonyEvent
            elif id_ == Channel.EventID.Levels:
                typ = ChannelLevelsEvent
            elif id_ == Channel.EventID.Tracking:
                typ = ChannelTrackingEvent
            elif id_ == Channel.EventID.LevelOffsets:
                typ = ChannelLevelOffsetsEvent
            elif id_ == Channel.EventID.Parameters:
                typ = ChannelParametersEvent
            elif id_ == Channel.EventID.EnvelopeLFO:
                typ = ChannelEnvelopeLFOEvent
            elif id_ in (Channel.EventID.Plugin, InsertSlot.EventID.Plugin):
                if self.__cur_plug_is_vst:
                    typ = VSTPluginEvent
                    self.__cur_plug_is_vst = False
                else:
                    typ = _DataEvent
            elif id_ == Insert.EventID.Parameters:
                typ = InsertParametersEvent
            elif id_ == Pattern.EventID.Controllers:
                typ = PatternControllersEvent
            elif id_ == Pattern.EventID.Notes:
                typ = PatternNotesEvent
            elif id_ == RemoteController.ID:
                typ = RemoteControllerEvent
            else:
                typ = _DataEvent
            self.__events.append(typ, id_, buf)

        while True:
            evid = self.__r.read_B()
            if evid is None:
                break

            if evid in range(BYTE, WORD):
                self.__events.append(_ByteEvent, evid, self.__r.read(1))
            elif evid in range(WORD, DWORD):
                self.__events.append(_WordEvent, evid, self.__r.read(2))
            elif evid in range(DWORD, TEXT):
                add_dwordevent(evid, self.__r.read(4))
            else:
                varint = self.__r.read_v()
                buf = self.__r.read(varint)
                if evid in range(TEXT, DATA) or evid in DATA_TEXT_EVENTS:
                    add_textevent(evid, buf)
                else:
                    add_dataevent(evid, buf)

    def __parse_channel(self, ev: EventType) -> None:
        """Creates and appends `Channel` objects to `Project`.
        Dispatches `ChannelEventID` events for parsing."""

        if ev.id_ == Channel.EventID.New:
            self.__channel_count += 1
            self.__cur_ch = Channel()
            self.__proj.channels.append(self.__cur_ch)
        self.__cur_ch.parse_event(ev)

    def __parse_pattern(self, ev: EventType) -> None:
        """Creates and appends `Pattern` objects to `Project`.
        Dispatches `PatternEventID` events to `Pattern` for parsing."""

        if ev.id_ == Pattern.EventID.New and isinstance(ev, _WordEvent):
            # Occurs twice, once with the note events only and later again
            # for metadata (name, color and a few undiscovered properties)
            # New patterns can occur for metadata as well; they are empty.
            index = ev.to_uint16()
            if index in self.__pat_indexes:
                for pattern in self.__proj.patterns:
                    if pattern.index == index:
                        self.__cur_pat = pattern
                self.__cur_pat.parse_index1(ev)
                return  # Don't let the event be parsed again!
            else:
                self.__pat_indexes.add(index)
                self.__cur_pat = Pattern()
                self.__proj.patterns.append(self.__cur_pat)
        self.__cur_pat.parse_event(ev)

    def __parse_insert(self, ev: EventType) -> None:
        """Creates and appends `Insert` objects to `Project`. Dispatches
        `InsertEvent` and `InsertSlotEventID` events for parsing."""

        self.__cur_ins.parse_event(ev)
        if (
            ev.id_ == Insert.EventID.Output
            and len(self.__proj.inserts) < self.__max_counts.inserts
        ):
            self.__proj.inserts.append(self.__cur_ins)
            self.__cur_ins = Insert(self.__proj, self.__max_counts)

    def __parse_arrangement(self, ev: EventType) -> None:
        """Creates and appends `Arrangement` objects to `Project`. Dispatches
        `ArrangementEventID`, `PlaylistEventID` and `TrackEventID` events
        for parsing."""

        if ev.id_ == Arrangement.EventID.New:
            self.__cur_arr = Arrangement(self.__proj)
            self.__proj.arrangements.append(self.__cur_arr)

        # I have found timemarkers occuring randomly (mixed with channel events)
        # before ArrangementEventID.Index in certains version of FL 20.0-20.1.
        # i.e the order before was TimeMarkers -> Playlist -> Tracks.
        # Now it is in the order: Playlist -> TimeMarkers -> Tracks.
        if ev.id_ == Track.EventID.Data and not self.__cur_arr.timemarkers:
            self.__cur_arr._timemarkers = self.__tms
            self.__tms = []
        self.__cur_arr.parse_event(ev)

    def __parse_filter(self, ev: EventType) -> None:
        """Creates and appends `Filter` objects to `Project`.
        Dispatches `FilterEventID` events for parsing."""

        if ev.id_ == Filter.EventID.Name:
            self.__cur_flt: Filter = Filter()
            self.__proj.filters.append(self.__cur_flt)
        self.__cur_flt.parse_event(ev)

    def __parse_timemarker(self, ev: EventType) -> None:
        if ev.id_ == TimeMarker.EventID.Position:
            self.__cur_tm = TimeMarker()
            self.__tms.append(self.__cur_tm)
        self.__cur_tm.parse_event(ev)

    def get_events(
        self, flp: Union[str, Path, bytes, io.BufferedIOBase]
    ) -> List[EventType]:
        """Just get the events; don't parse

        Why does this method exist?
        - FLP format has changed a lot over the years;
        nobody except IL can parse it properly, PyFLP needs a
        specific event structure.
        - In the event of failure, user can at least get the events.
        - [FLPInspect](https://github.com/demberto/flpinspect) and
        [FLPInfo](https://github.com/demberto/flpinfo) can still
        display some minimal information based on the events.
        """
        # * Argument validation
        self.__proj = proj = Project()
        if isinstance(flp, (Path, str)):
            if isinstance(flp, Path):
                self.__proj.save_path = flp
            else:
                self.__proj.save_path = Path(flp)
            self.__r = BytesIOEx(open(flp, "rb").read())
        elif isinstance(flp, io.BufferedIOBase):
            flp.seek(0)
            self.__r = BytesIOEx(flp.read())
        elif isinstance(flp, bytes):
            self.__r = BytesIOEx(flp)
        else:
            raise TypeError(
                f"Cannot parse a file of type {type(flp)}. \
                Only str, Path or bytes objects are supported."
            )

        r = self.__r
        hdr_magic = r.read(4)
        if hdr_magic != HEADER_MAGIC:
            raise InvalidMagicError(hdr_magic)
        hdr_size = r.read_I()
        if hdr_size != HEADER_SIZE:
            raise InvalidHeaderSizeError(hdr_size)
        proj.misc.format = Misc.Format(r.read_h())
        proj.misc.channel_count = r.read_H()
        proj.misc.ppq = r.read_H()
        data_magic = r.read(4)
        if data_magic != DATA_MAGIC:
            raise InvalidMagicError(data_magic)
        _ = r.read_I()  # Combined size of all events
        self.__build_event_store()

        return self.__events

    def parse(self, flp: Union[str, Path, bytes, io.BufferedIOBase]) -> Project:
        """Parses an FLP. Use `parse_zip` for ZIP looped packages instead."""

        # * Argument validation
        self.__proj.events = self.get_events(flp)

        # * Modify parsing logic as per FL version
        # TODO: This can be as less as 16. Also insert slots were once 8.
        self.__max_counts.inserts = 127 if self.__fl_version.as_float() > 12.89 else 104
        self.__cur_ins = Insert(self.__proj, self.__max_counts)

        # * Build an object model
        # TODO: Parse in multiple layers
        parse_channel = True
        for ev in self.__proj.events:
            if ev.id_ in Misc.EventID.__members__.values():
                self.__proj.misc.parse_event(ev)
            elif ev.id_ in Filter.EventID.__members__.values():
                self.__parse_filter(ev)
            elif ev.id_ == RemoteController.ID:
                controller = RemoteController()
                controller.parse_event(ev)
                self.__proj.controllers.append(controller)
            elif ev.id_ in Pattern.EventID.__members__.values():
                self.__parse_pattern(ev)
            elif ev.id_ in CHANNEL_EVENTS and parse_channel:
                self.__parse_channel(ev)
            elif ev.id_ in TimeMarker.EventID.__members__.values():
                self.__parse_timemarker(ev)
            elif ev.id_ in ARRANGEMENT_EVENTS:
                parse_channel = False
                self.__parse_arrangement(ev)
            elif ev.id_ in INSERT_EVENTS and not parse_channel:
                self.__parse_insert(ev)
            elif ev.id_ == InsertParamsEvent.ID:
                ev.id_ = InsertParamsEvent.ID

                # Append the last insert first
                self.__proj.inserts.append(self.__cur_ins)
                insert_params_ev = InsertParamsEvent(ev)
                if not insert_params_ev.parse(self.__proj.inserts):
                    self.__proj._unparsed_events.append(ev)
            else:
                self.__proj._unparsed_events.append(ev)

        # * Post-parse steps
        # Now move all playlist events to track, Playlist can be empty as well
        # Cannot parse playlist events in arrangement, because certain FL versions
        # dump only used tracks. This is not the case anymore.
        for arrangement in self.__proj.arrangements:
            if arrangement.playlist:
                for idx, track in enumerate(arrangement.tracks):
                    items = arrangement.playlist.items.get(idx)
                    if items:
                        track._items = items
                    arrangement.playlist._items = {}

        # Re-arrange patterns by index
        self.__proj.patterns.sort(key=lambda pat: pat.index - 1)

        return self.__proj

    def parse_zip(self, zip_file, name: str = "") -> Project:
        """Parses an FLP inside a ZIP.

        Args:
            zip_file (Union[zipfile.ZipFile, str, bytes, Path, io.BufferedIOBase]):
                The path to the ZIP file, stream, Path, file-like or a ZipFile
                object.
            name (str, optional): If the ZIP has multiple FLPs, you need
                to specify the name of the FLP to parse.

        Raises:
            TypeError: When `zip_file` points to a ZIP or stream containing no
                files with an extension of .flp.
            TypeError: When `name` is empty and `zip_file` points to a ZIP or
                stream containing more than one FLP.

        Returns:
            Project: The parsed object.
        """

        flp = None

        if isinstance(zip_file, (str, bytes, io.BufferedIOBase, Path)):
            zp = zipfile.ZipFile(zip_file, "r")
        else:
            zp = zip_file

        if name == "":
            # Find the file with .flp extension
            flps = []
            file_names = zp.namelist()
            for file_name in file_names:
                if file_name.endswith(".flp"):
                    flps.append(file_name)
            if not len(flps) == 1:  # pragma: no cover
                if not flps:
                    raise TypeError("No FLP files found inside ZIP.", zp)
                elif len(flps) > 1:
                    raise TypeError(
                        "Optional parameter 'name' cannot be empty "
                        "when more than one FLP exists in ZIP",
                        zp,
                    )
            else:
                name = flps[0]

        flp = zp.open(name, "r").read()
        return self.parse(flp)
