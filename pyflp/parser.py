import logging
import os
import pathlib
from typing import List, Union

from flobject.flobject import FLObject
from flobject.arrangement import Arrangement, ArrangementEventID
from flobject.misc import MiscEventID
from flobject.insert import Insert, InsertEventID
from flobject.channel import Channel, ChannelEventID
from flobject.pattern import Pattern, PatternEventID
from flobject.playlist import PlaylistEventID
from flobject.track import Track, TrackEventID
from flobject.filterchannel import FilterChannel, FilterChannelEventID
from flobject.timemarker import TimeMarker, TimeMarkerEventID
from event import (
    ByteEvent,
    DWordEvent,
    DataEvent,
    Event,
    TextEvent,
    WordEvent
)
from flobject.insertslot import InsertSlotEventID
from utils import (
    BYTE,
    DATA,
    DATA_TEXT_EVENTS,
    DWORD,
    TEXT,
    WORD,
    FLVersion
)
from project import Project
from bytesioex import BytesIOEx

logging.basicConfig()
log = logging.getLogger(__name__)

class ProjectParser:
    _arrangement_events = []
    for events in (ArrangementEventID.__members__.values(),
        TrackEventID.__members__.values(),
        TimeMarkerEventID.__members__.values(),
        PlaylistEventID.__members__.values()
    ):
        _arrangement_events.extend(events)
    
    _insert_events = []
    for events in(InsertEventID.__members__.values(),
        InsertSlotEventID.__members__.values()
    ):
        _insert_events.extend(events)
    
    def __init__(self, verbose: bool = False) -> None:
        self._event_store: List[Event] = list()
        self._verbose = verbose
        if self._verbose:
            FLObject._verbose = True
            log.setLevel(logging.DEBUG if self._verbose else logging.WARNING)
        self._channel_count = 0
    
    def _parse_flhd(self):
        assert self.r.read(4) == b'FLhd'
        assert self.r.read_uint32() == 6
        format = self.r.read_int16()
        assert format == 0
        self._project.misc.format = format
        channel_count = self.r.read_uint16()
        assert channel_count in range(1, 1000)
        self._project.misc.channel_count = channel_count
        ppq = self.r.read_uint16()
        self._project.misc.ppq = ppq
    
    def _parse_fldt(self):
        assert self.r.read(4) == b'FLdt'
        self._chunklen = self.r.read_uint32()
    
    def _build_event_store(self):
        loop = True
        while loop:
            id = self.r.read_uint8()
            # log.debug(f"Discovered event, id: {id}")
            if id != None:
                if id in range(BYTE, WORD):
                    self._event_store.append(ByteEvent(id, self.r.read(1)))
                elif id in range(WORD, DWORD):
                    self._event_store.append(WordEvent(id, self.r.read(2)))
                elif id in range(DWORD, TEXT):
                    self._event_store.append(DWordEvent(id, self.r.read(4)))
                else:
                    varint = self.r.read_varint()
                    if id in range(TEXT, DATA) or id in DATA_TEXT_EVENTS:
                        self._event_store.append(TextEvent(id, self.r.read(varint)))
                    else:
                        self._event_store.append(DataEvent(id, self.r.read(varint)))
            else:
                loop = False
        log.info(f"Event store built; contains {len(self._event_store)} events")

    def _parse_channel(self, ev: Event):
        if ev.id == ChannelEventID.New:
            self._channel_count += 1
            if self._channel_count > self._project.misc.channel_count:
                log.error("Channel count less than channels discovered!")
            self._cur_channel = Channel()
            self._project.channels.append(self._cur_channel)
        self._cur_channel.parse(ev)

    def _parse_pattern(self, ev: Event):
        if ev.id == PatternEventID.New:
            self._cur_pattern = Pattern()
            self._project.patterns.append(self._cur_pattern)
        self._cur_pattern.parse(ev)
    
    def _parse_insert(self, ev: Event):
        if ev.id == InsertEventID.Parameters:
            self._cur_insert = Insert()
            self._project.inserts.append(self._cur_insert)
        self._cur_insert.parse(ev)
    
    def _parse_track(self, ev: Event):
        if ev.id == TrackEventID.Data:
            self._cur_track = Track()
            self._project.tracks.append(self._cur_track)
        self._cur_track.parse(ev)
    
    def _parse_arrangement(self, ev: Event):
        if ev.id == ArrangementEventID.Index:
            self._cur_arrangement = Arrangement()
            self._project.arrangements.append(self._cur_arrangement)
        self._cur_arrangement.parse(ev)

    def _parse_filterchannel(self, ev: Event):
        if ev.id == FilterChannelEventID.Name:
            self._cur_filterchannel = FilterChannel()
            self._project.filterchannels.append(self._cur_filterchannel)
        self._cur_filterchannel.parse(ev)

    def _parse_timemarker(self, ev: Event):
        if ev.id == TimeMarkerEventID.Position:
            self._cur_timemarker = TimeMarker()
            self._project.timemarkers.append(self._cur_timemarker)
        self._cur_timemarker.parse(ev)
    
    def parse(self, flp: Union[str, pathlib.Path, bytes]) -> Project:
        self._project = Project(self._verbose)
        if isinstance(flp, (pathlib.Path, str)):
            if isinstance(flp, pathlib.Path):
                self._project.save_path = flp
            else:
                self._project.save_path = pathlib.Path(flp)
            self.r = BytesIOEx(open(flp, 'rb').read())
        elif isinstance(flp, bytes):
            self.r = BytesIOEx(flp)
        else:
            raise TypeError(f"Cannot parse a file of type {type(flp)}. \
                Only str, pathlib.Path or bytes objects are supported.")
        
        # Init: Verify header integrity and build event store
        self._parse_flhd()
        self._parse_fldt()
        self._build_event_store()
        
        # Step 1: Modify parsing logic based on FL Version
        version_event: TextEvent = self._event_store[0]
        fl_version = FLVersion(version_event.to_str().strip('\0'))
        FLObject.fl_version = fl_version
        version_float = fl_version.as_float()
        if version_float >= 11.5:
            TextEvent.uses_unicode = True
        # TODO: This can be as less as 16. Also insert slots were once 8.
        Insert.max_count = 127 if version_float >= 12.89 else 104

        # Step 2: Build an object model - Assign and parse events
        _cur_parse_mode = 'channel'
        _uses_arrangements = False
        for ev in self._event_store:
            # Misc events
            if ev.id in MiscEventID.__members__.values():
                self._project.misc.parse(ev)
            
            # Filter channel events
            elif ev.id in FilterChannelEventID.__members__.values():
                self._parse_filterchannel(ev)
            
            # Channel events
            elif ev.id in ChannelEventID.__members__.values() and _cur_parse_mode == 'channel':
                self._parse_channel(ev)
            
            # Detect arrangement use, switch to appropriate parse logic
            elif ev.id == ArrangementEventID.Index:
                _uses_arrangements = True
                self._parse_arrangement(ev)
            elif ev.id in ProjectParser._arrangement_events:
                # Arrangements are used, route all events to arrangement
                if _uses_arrangements:
                    self._parse_arrangement(ev)
                elif ev.id in TrackEventID.__members__.values():
                    self._parse_track(ev)
                elif ev.id in TimeMarkerEventID.__members__.values():
                    self._parse_timemarker(ev)
                else:
                    self._project.playlist.parse(ev)
            
            # Insert events, change parse mode
            # Parsing will not happen correctly if this event is not present,
            # or inserts and channel events are mixed together
            elif ev.id == InsertEventID.Parameters:
                log.debug(f"New insert found, index: {ev.index}")
                _cur_parse_mode = 'insert'
                self._parse_insert(ev)
            elif ev.id in ProjectParser._insert_events and _cur_parse_mode == 'insert':
                # log.debug(f" Insert event {ev.id}, index: {ev.index}")
                self._parse_insert(ev)
            
            # Unimplemented events - these will not get parsed
            else:
                # log.info(f"Event {ev.id}, index: {ev.index} not implemented")
                self._project._unparsed_events.append(ev)
        return self._project