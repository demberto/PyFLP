import logging
import zipfile
import pathlib
from typing import List, Union

from pyflp.flobject import *
from pyflp.event import *
from pyflp.utils import (
    BYTE,
    DATA,
    DATA_TEXT_EVENTS,
    DWORD,
    TEXT,
    WORD,
    FLVersion
)
from pyflp.project import Project
from pyflp.bytesioex import BytesIOEx

logging.basicConfig()
log = logging.getLogger(__name__)

__all__ = ['Parser']

class Parser:
    #region Insert events
    INSERT_EVENTS = []
    for events in(InsertEventID.__members__.values(),
                  InsertSlotEventID.__members__.values()):
        INSERT_EVENTS.extend(events)
    #endregion

    #region Arrangement events
    ARRANGEMENT_EVENTS = []
    for events in (ArrangementEventID.__members__.values(),
                   TrackEventID.__members__.values(),
                   PlaylistEventID.__members__.values()):
        ARRANGEMENT_EVENTS.extend(events)
    #endregion

    def __init__(self, verbose: bool = False) -> None:
        self._event_store: List[Event] = list()
        self._verbose = verbose
        if self._verbose:
            FLObject._verbose = True
            log.setLevel(logging.DEBUG if self._verbose else logging.WARNING)

        self._channel_count = 0

        # Appended to an arrangement when it is created
        self._timemarkers: List[TimeMarker] = list()

    def _parse_flhd(self):
        """Parses header chunk."""

        # Magic number
        assert self.r.read(4) == b'FLhd'

        # Header size (always 6)
        assert self.r.read_uint32() == 6

        # Format, TODO enum
        format = self.r.read_int16()
        assert format == 0
        self._project.misc.format = format

        # Channel count
        channel_count = self.r.read_uint16()
        assert channel_count in range(1, 1000)
        self._project.misc.channel_count = channel_count
        Channel.max_count = channel_count

        # PPQ
        ppq = self.r.read_uint16()
        self._project.misc.ppq = ppq
        Playlist.ppq = ppq

    def _parse_fldt(self):
        """Parses data chunk header."""

        # Magic number
        assert self.r.read(4) == b'FLdt'

        # Combined size of all events
        self._chunklen = self.r.read_uint32()

    def _build_event_store(self):
        """Gathers all events into a single list."""

        while True:
            id = self.r.read_uint8()
            if id is None:
                break

            log.debug(f"Discovered event, id: {id}")
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

        log.info(f"Event store built; contains {len(self._event_store)} events")

    def _parse_channel(self, ev: Event):
        """Creates and appends :class:`Channel` objects to :class:`Project`.
        Dispatches :class:`ChannelEventID` events for parsing.
        """

        if ev.id == ChannelEventID.New:
            self._channel_count += 1
            if self._channel_count > self._project.misc.channel_count:
                log.error("Channel count less than channels discovered!")
            self._cur_channel = Channel()
            self._project.channels.append(self._cur_channel)
        self._cur_channel.parse(ev)

    def _parse_pattern(self, ev: Event):
        """Creates and appends :class:`Pattern` objects to :class:`Project`.
        Dispatches :class:`PatternEventID` events for parsing.
        """

        if ev.id == PatternEventID.New:
            # Occurs twice, once with the note events only and later again
            # for metadata (name, color and a few undiscovered properties)
            # New patterns can occur for metadata as well; they are empty.
            ev: WordEvent = ev      # For syntax highlighting below
            index = ev.to_uint16()
            existing = tuple(pattern.index for pattern in self._project.patterns)
            if index not in existing:
                self._cur_pattern = Pattern()
                self._project.patterns.append(self._cur_pattern)
        self._cur_pattern.parse(ev)

    def _parse_insert(self, ev: Event):
        """Creates and appends :class:`Insert` objects to :class:`Project`.
        Dispatches :class:`InsertEventID` and :class:`InsertSlotEventID` events for parsing.
        """

        if ev.id == InsertEventID.Parameters:
            self._cur_insert = Insert()
            self._project.inserts.append(self._cur_insert)
        self._cur_insert.parse(ev)

    def _parse_arrangement(self, ev: Event):
        """Creates and appends :class:`Arrangement` objects to :class:`Project`.
        Dispatches :class:`ArrangementEventID`, :class:`PlaylistEventID` and
        :class:`TrackEventID` events for parsing.
        """

        if ev.id == ArrangementEventID.Index:
            self._cur_arrangement = Arrangement()
            self._project.arrangements.append(self._cur_arrangement)

            # Assumes that all timemarker events occur before this event occurs
            self._cur_arrangement.timemarkers = self._timemarkers
            self._timemarkers = []
        self._cur_arrangement.parse(ev)

    def _parse_filterchannel(self, ev: Event):
        """Creates and appends :class:`FilterChannel` objects to :class:`Project`.
        Dispatches :class:`FilterChannelEventID` events for parsing.
        """

        if ev.id == FilterChannelEventID.Name:
            self._cur_filterchannel = FilterChannel()
            self._project.filterchannels.append(self._cur_filterchannel)
        self._cur_filterchannel.parse(ev)

    def _parse_timemarker(self, ev: Event):
        if ev.id == TimeMarkerEventID.Position:
            self._cur_timemarker = TimeMarker()
            self._timemarkers.append(self._cur_timemarker)
        self._cur_timemarker.parse(ev)

    def parse(self, flp: Union[str, pathlib.Path, bytes]) -> Project:
        """Parses an FLP (stream, ZipFile or file), creates a :class:`Project` object and returns it."""
        
        #region Argument validation
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
        #endregion

        #region Init: Verify header integrity and build event store
        self._parse_flhd()
        self._parse_fldt()
        self._build_event_store()
        #endregion

        #region Step 1: Modify parsing logic based on FL Version
        version_event: TextEvent = self._event_store[0]
        fl_version = FLVersion(version_event.to_str().strip('\0'))
        FLObject.fl_version = fl_version
        version_float = fl_version.as_float()
        if version_float >= 11.5:
            TextEvent.uses_unicode = True
        # TODO: This can be as less as 16. Also insert slots were once 8.
        Insert.max_count = 127 if version_float >= 12.89 else 104
        #endregion

        #region Step 2: Build an object model - Assign and parse events
        # TODO: Parse in multiple layers
        _cur_parse_mode = 'channel'
        for ev in self._event_store:
            if ev.id in MiscEventID.__members__.values(): self._project.misc.parse(ev)
            elif ev.id in FilterChannelEventID.__members__.values(): self._parse_filterchannel(ev)
            elif ev.id in PatternEventID.__members__.values(): self._parse_pattern(ev)
            elif ev.id in ChannelEventID.__members__.values() and _cur_parse_mode == 'channel': self._parse_channel(ev)
            elif ev.id in TimeMarkerEventID.__members__.values(): self._parse_timemarker(ev)
            elif ev.id in Parser.ARRANGEMENT_EVENTS: self._parse_arrangement(ev)

            # Insert events, change _cur_parse_mode, as InsertSlotEventID shares event IDs
            # with ChannelEventID. Parsing will not happen correctly if this event is not
            # presnt, or inserts and channel events are mixed together.
            elif ev.id == InsertEventID.Parameters:
                _cur_parse_mode = 'insert'
                self._parse_insert(ev)
            elif ev.id in Parser.INSERT_EVENTS and _cur_parse_mode == 'insert': self._parse_insert(ev)

            # Dreadful event, idk how to implement property setters for this
            elif ev.id == InsertParamsEvent.ID:
                insert_params_ev = InsertParamsEvent(ev.data)
                if not insert_params_ev.parse(self._project.inserts):
                    self._project._unparsed_events.append(ev)

            # Unimplemented events - these will not get parsed
            else:
                log.info(f"Event {ev.id}, index: {ev.index} not implemented")
                self._project._unparsed_events.append(ev)
        #endregion

        #region Post-parse steps
        # Now dispatch all playlist events to track, Playlist can be empty as well
        # Cannot parse playlist events in arrangement, because certain FL versions
        # dump only used tracks even while using arrangements. This is not the case anymore
        for arrangement in self._project.arrangements:
            for idx, track in enumerate(arrangement.tracks):
                items = arrangement.playlist._playlist_events.get(idx)
                if items:
                    track.items = items
            arrangement.playlist._playlist_events = {}
        #endregion

        return self._project

    def parse_zip(self, zip_file: Union[zipfile.ZipFile, str], name: str = '') -> Project:
        """Parses an FLP inside a ZIP and returns a :class:`Project` object.

        :param zip_file: The path to the ZIP file or a :class:`zipfile.ZipFile`
        :param name: If the ZIP has multiple FLPs, you need to specify the name of the FLP to parse
        """
        
        flp = None
        
        if isinstance(zip_file, str):
            zip_file = zipfile.ZipFile(zip_file, 'r')
        
        if name == '':
            # Find the file with .flp extension
            flps = []
            file_names = zip_file.namelist()
            for file_name in file_names:
                if file_name.endswith('.flp'):
                    flps.append(file_name)
            if not len(flps) == 1:
                if not flps:
                    error_str = "No FLP files found inside ZIP"
                elif len(flps) > 1:
                    error_str = "Optional parameter name cannot be default when more than one FLP exists in ZIP"
                log.critical(error_str)
                raise Exception(zip_file, error_str)
            else:
                name = flps[0]
        
        flp = zip_file.open(name, 'r').read()
        log.info(f"FLP {name} found in ZIP")
        
        return self.parse(flp)
