import io
import logging
import zipfile
from pathlib import Path
from typing import List, Set, Union

from pyflp.flobject import *
from pyflp.event import *
from pyflp.utils import BYTE, DATA, DATA_TEXT_EVENTS, DWORD, TEXT, WORD, FLVersion
from pyflp.project import Project
from bytesioex import BytesIOEx  # type: ignore

log = logging.getLogger(__name__)

__all__ = ["Parser"]


class Parser:
    """FL Studio project file parser."""

    INSERT_EVENTS: List[int] = []
    for enum in (InsertEvent, InsertSlotEvent):
        INSERT_EVENTS.extend(enum.__members__.values())

    ARRANGEMENT_EVENTS: List[int] = []
    for enum in (ArrangementEvent, TrackEvent, PlaylistEvent):
        ARRANGEMENT_EVENTS.extend(enum.__members__.values())

    def __init__(
        self,
        verbose: bool = False,
        handlers: List[logging.Handler] = [],
        verbosity: int = logging.DEBUG,
    ):
        self.__event_store: List[Event] = []
        self.__verbose = verbose

        if verbose:
            logging.root.setLevel(verbosity)
            for handler in handlers:
                logging.root.addHandler(handler)
        self._channel_count = 0

        # Reinitialise static variables
        FLObject._count = 0
        Event._count = 0
        for subclass in FLObject.__subclasses__():
            subclass._count = 0
        self._timemarkers: List[TimeMarker] = []
        self._pattern_indexes: Set[int] = set()

    def __parse_flhd(self):
        """Parses header chunk."""

        # Magic number
        assert self.r.read(4) == b"FLhd"

        # Header size (always 6)
        assert self.r.read_I() == 6

        # Format, TODO enum
        format = self.r.read_h()
        assert format == 0
        self.__project.misc.format = format

        # Channel count
        channel_count = self.r.read_H()
        assert channel_count in range(1, 1000)
        self.__project.misc.channel_count = channel_count
        Channel.max_count = channel_count

        # PPQ
        ppq = self.r.read_H()
        self.__project.misc.ppq = ppq
        Playlist.ppq = ppq

    def __parse_fldt(self):
        """Parses data chunk header."""

        # Magic number
        assert self.r.read(4) == b"FLdt"

        # Combined size of all events
        self._chunklen = self.r.read_I()

    def __build_event_store(self):
        """Gathers all events into a single list."""

        while True:
            id = self.r.read_B()
            if id is None:
                break

            if id in range(BYTE, WORD):
                self.__event_store.append(ByteEvent(id, self.r.read(1)))
            elif id in range(WORD, DWORD):
                self.__event_store.append(WordEvent(id, self.r.read(2)))
            elif id in range(DWORD, TEXT):
                self.__event_store.append(DWordEvent(id, self.r.read(4)))
            else:
                varint = self.r.read_v()
                buf = self.r.read(varint)
                if id in range(TEXT, DATA) or id in DATA_TEXT_EVENTS:
                    if id == MiscEvent.Version:
                        FLObject.fl_version = flv = FLVersion(TextEvent.as_ascii(buf))
                        if flv.as_float() < 11.5:
                            TextEvent.uses_unicode = False
                    self.__event_store.append(TextEvent(id, buf))
                else:
                    self.__event_store.append(DataEvent(id, buf))

        log.info(f"Event store built; contains {len(self.__event_store)} events")

    def __parse_channel(self, ev: Event):
        """Creates and appends `Channel` objects to `Project`.
        Dispatches `ChannelEventID` events for parsing.
        """

        if ev.id == ChannelEvent.New:
            self._channel_count += 1
            if self._channel_count > self.__project.misc.channel_count:
                log.error("Channel count less than channels discovered!")
            self._cur_channel = Channel()
            self.__project.channels.append(self._cur_channel)
        self._cur_channel.parse_event(ev)

    def __parse_pattern(self, ev: Event):
        """Creates and appends `Pattern` objects to `Project`.
        Dispatches `PatternEventID` events to `Pattern` for parsing.
        """

        if ev.id == PatternEvent.New and isinstance(ev, WordEvent):
            # Occurs twice, once with the note events only and later again
            # for metadata (name, color and a few undiscovered properties)
            # New patterns can occur for metadata as well; they are empty.
            index = ev.to_uint16()
            if index in self._pattern_indexes:
                self._cur_pattern = self.__project.patterns[index - 1]
                self._cur_pattern.parse_index1(ev)
                return  # Don't let the event be parsed again!
            else:
                self._pattern_indexes.add(index)
                self._cur_pattern = Pattern()
                self.__project.patterns.append(self._cur_pattern)
        self._cur_pattern.parse_event(ev)

    def __parse_insert(self, ev: Event):
        """Creates and appends `Insert` objects to `Project`.
        Dispatches `InsertEvent` and `InsertSlotEventID` events for parsing.
        """

        if ev.id == InsertEvent.Parameters:
            self._cur_insert = Insert()
            self.__project.inserts.append(self._cur_insert)
        self._cur_insert.parse_event(ev)

    def __parse_arrangement(self, ev: Event):
        """Creates and appends `Arrangement` objects to `Project`.
        Dispatches `ArrangementEventID`, `PlaylistEventID` and
        `TrackEventID` events for parsing.
        """

        if ev.id == ArrangementEvent.Index:
            self._cur_arrangement = Arrangement()
            self.__project.arrangements.append(self._cur_arrangement)

            # Assumes that all timemarker events occur before this event occurs
            self._cur_arrangement.timemarkers = self._timemarkers
            self._timemarkers = []
        self._cur_arrangement.parse_event(ev)

    def __parse_filterchannel(self, ev: Event):
        """Creates and appends `FilterChannel` objects to `Project`.
        Dispatches `FilterChannelEventID` events for parsing.
        """

        if ev.id == FilterChannelEvent.Name:
            self._cur_filterchannel = FilterChannel()
            self.__project.filterchannels.append(self._cur_filterchannel)
        self._cur_filterchannel.parse_event(ev)

    def __parse_timemarker(self, ev: Event):
        if ev.id == TimeMarkerEvent.Position:
            self._cur_timemarker = TimeMarker()
            self._timemarkers.append(self._cur_timemarker)
        self._cur_timemarker.parse_event(ev)

    def get_events(
        self, flp: Union[str, Path, bytes, io.BufferedIOBase]
    ) -> List[Event]:
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
        self.__project = Project(self.__verbose)
        if isinstance(flp, (Path, str)):
            if isinstance(flp, Path):
                self.__project.save_path = flp
            else:
                self.__project.save_path = Path(flp)
            self.r = BytesIOEx(open(flp, "rb").read())
        elif isinstance(flp, io.BufferedIOBase):
            flp.seek(0)
            self.r = BytesIOEx(flp.read())
        elif isinstance(flp, bytes):
            self.r = BytesIOEx(flp)
        else:
            raise TypeError(
                f"Cannot parse a file of type {type(flp)}. \
                Only str, Path or bytes objects are supported."
            )

        # * Init: Verify header integrity and build event store
        self.__parse_flhd()
        self.__parse_fldt()
        self.__build_event_store()

        return self.__event_store

    def parse(self, flp: Union[str, Path, bytes, io.BufferedIOBase]) -> Project:
        """Parses an FLP. Use `parse_zip` for ZIP looped packages instead."""

        # * Argument validation
        self.__project.events = self.get_events(flp)

        # * Modify parsing logic as per FL version
        # TODO: This can be as less as 16. Also insert slots were once 8.
        Insert.max_count = 127 if FLObject.fl_version.as_float() >= 12.89 else 104

        # * Build an object model
        # TODO: Parse in multiple layers
        cur_parse_mode = "channel"
        for ev in self.__project.events:
            if ev.id in MiscEvent.__members__.values():
                ev.id = MiscEvent(ev.id)
                self.__project.misc.parse_event(ev)
            elif ev.id in FilterChannelEvent.__members__.values():
                ev.id = FilterChannelEvent(ev.id)
                self.__parse_filterchannel(ev)
            elif ev.id in PatternEvent.__members__.values():
                ev.id = PatternEvent(ev.id)
                self.__parse_pattern(ev)
            elif (
                ev.id in ChannelEvent.__members__.values()
                and cur_parse_mode == "channel"
            ):
                ev.id = ChannelEvent(ev.id)
                self.__parse_channel(ev)
            elif ev.id in TimeMarkerEvent.__members__.values():
                ev.id = TimeMarkerEvent(ev.id)
                self.__parse_timemarker(ev)
            elif ev.id in Parser.ARRANGEMENT_EVENTS:
                for enum in TrackEvent, ArrangementEvent, PlaylistEvent:
                    if ev.id in enum.__members__.values():
                        ev.id = enum(ev.id)
                        break
                self.__parse_arrangement(ev)

            # Insert events, change _cur_parse_mode, as InsertSlotEventID shares event IDs
            # with ChannelEventID. Parsing will not happen correctly if this event is not
            # presnt, or inserts and channel events are mixed together.
            elif ev.id == InsertEvent.Parameters:
                ev.id = InsertEvent.Parameters
                cur_parse_mode = "insert"
                self.__parse_insert(ev)

            # Rest of the insert events
            elif ev.id in Parser.INSERT_EVENTS and cur_parse_mode == "insert":
                for id_ in Parser.INSERT_EVENTS:
                    if ev.id == id_:
                        ev.id = id_
                        break
                self.__parse_insert(ev)

            # Dreadful event, idk how to implement property setters for this
            elif ev.id == InsertParamsEvent.ID:
                insert_params_ev = InsertParamsEvent(ev.data)
                if not insert_params_ev.parse(self.__project.inserts):
                    self.__project._unparsed_events.append(ev)

            # Unimplemented events - these will not get parsed
            else:
                log.warning(f"Event {ev.id}, index: {ev.index} not implemented")
                self.__project._unparsed_events.append(ev)

        # * Post-parse steps
        # Now dispatch all playlist events to track, Playlist can be empty as well
        # Cannot parse playlist events in arrangement, because certain FL versions
        # dump only used tracks even while using arrangements. This is not the case anymore
        for arrangement in self.__project.arrangements:
            if arrangement.playlist:
                for idx, track in enumerate(arrangement.tracks):
                    items = arrangement.playlist.items.get(idx)
                    if items:
                        track.items = items
                    arrangement.playlist.items = {}

        return self.__project

    def parse_zip(
        self, zip_file: Union[zipfile.ZipFile, str, Path], name: str = ""
    ) -> Project:
        """Parses an FLP inside a ZIP and returns a `Project` object.

        Args:
            zip_file (Union[zipfile.ZipFile, str]): The path to the ZIP file or ZipFile object.
            name (str, optional): If the ZIP has multiple FLPs, you need to specify the name of the FLP to parse
        """

        flp = None

        if isinstance(zip_file, str):
            zp = zipfile.ZipFile(zip_file, "r")
        else:
            # TODO: Mypy gives errors
            zp = zip_file  # type: ignore

        if name == "":
            # Find the file with .flp extension
            flps = []
            file_names = zp.namelist()
            for file_name in file_names:
                if file_name.endswith(".flp"):
                    flps.append(file_name)
            if not len(flps) == 1:
                if not flps:
                    e = "No FLP files found inside ZIP"
                elif len(flps) > 1:
                    e = "Optional parameter name cannot be default when more than one FLP exists in ZIP"
                log.critical(e)
                raise Exception(zp, e)
            else:
                name = flps[0]

        flp = zp.open(name, "r").read()  # type: ignore
        log.info(f"FLP {name} found in ZIP")

        return self.parse(flp)
