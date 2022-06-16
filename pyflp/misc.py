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

import datetime
import enum
from typing import List, Optional

from bytesioex import BytesIOEx, Double

from pyflp._event import (
    ByteEventType,
    DataEventType,
    DWordEventType,
    EventType,
    TextEventType,
    WordEventType,
)
from pyflp._flobject import _FLObject
from pyflp._properties import (
    _BoolProperty,
    _EnumProperty,
    _IntProperty,
    _StrProperty,
    _UIntProperty,
)
from pyflp._validators import _OneOfValidator
from pyflp.constants import DATA, DWORD, TEXT, VALID_PPQS, WORD

__all__ = ["Misc"]


class Misc(_FLObject):
    """Used for storing one time events, which don't fall into any other category.

    [Project Info](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/songsettings_songinfo.htm)
    [Project Settings](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/songsettings_settings.htm)
    """  # noqa

    __DELPHI_EPOCH = datetime.datetime(1899, 12, 30)

    # * Enums
    @enum.unique
    class PanningLaw(enum.IntEnum):
        """Used by `panning_law`."""

        Circular = 0
        Triangular = 2

    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `Misc`."""

        Version = TEXT + 7
        """First event in all FLPs, stored in ASCII for compatibility with older
        FL versions (pre 12.0), so older FL can read this value and show a warning
        before continuing to load. See `Misc.version`."""

        VersionBuild = DWORD + 31
        """See `Misc.version_build`."""

        LoopActive = 9
        """See `Misc.loop_active`."""

        ShowInfo = 10
        """See `Misc.show_info`."""

        Shuffle = 11
        """See `Misc.shuffle`."""

        # _MainVol = 12
        """Obsolete."""

        # _FitToSteps = 13
        """Obsolete."""

        TimeSigNum = 17
        """See `Misc.time_sig_num`."""

        TimeSigBeat = 18
        """See `Misc.time_sig_beat`."""

        PanningLaw = 23
        """See `Misc.panning_law`."""

        Registered = 28
        """See `Misc.registered`."""

        PlayTruncatedNotes = 30
        """See `Misc.play_truncated_notes`."""

        # _Tempo = WORD + 2
        """Obsolete."""

        CurrentPatternNum = WORD + 3
        """See `Misc.cur_pattern`."""

        MainPitch = WORD + 16
        """See `Misc.main_pitch`."""

        # _TempoFine = WORD + 29
        """Obsolete."""

        CurrentFilterChannelNum = DWORD + 18
        """See `Misc.cur_filter`."""

        SongLoopPos = DWORD + 24
        """See `Misc.song_loop_pos`."""

        Tempo = DWORD + 28
        """See `Misc.tempo`."""

        Title = TEXT + 2
        """See `Misc.title`."""

        Comment = TEXT + 3
        """See `Misc.comment`."""

        Url = TEXT + 5
        """See `Misc.url`."""

        _CommentRtf = TEXT + 6
        """See `Misc.comment`. Obsolete."""

        RegName = TEXT + 8
        """see `Misc.regname`. Obsolete."""

        DataPath = TEXT + 10
        """See `Misc.data_path`."""

        Genre = TEXT + 14
        """See `Misc.genre`."""

        Artists = TEXT + 15
        """See `Misc.artists`."""

        SaveTimestamp = DATA + 29
        """See `Misc.work_time` and `Misc.start_date`."""

    @enum.unique
    class Format(enum.IntEnum):
        """File formats used by FL Studio.

        [FLP](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/fformats_project.htm)
        [FSC](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/fformats_other_fsc.htm)
        [FST](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/fformats_other_fst.htm)
        """

        None_ = -1
        """Temporary"""

        Song = 0
        """FL Studio Project file (.flp)."""

        Score = 0x10
        """FL Studio Score File (.fsc). Stores
        pattern notes and controller events."""

        Automation = 24
        """FL Studio State file (.fst). Stores
        controller events and automation channels."""

        ChannelState = 0x20
        """Entire channel (including plugin events). Stores as FST."""

        PluginState = 0x30
        """Events of a native plugin on a channel or insert slot. Stored as FST."""

        GeneratorState = 0x31
        """Plugins events of a VST instrument. Stored as FST."""

        FXState = 0x32
        """Plugin events of a VST effect. Stored as FST."""

        InsertState = 0x40
        """Insert and all its slots. Stored as FST."""

        _Patcher = 0x50
        """Internal format, FLPEdit says it "tells FL Studio to Patcherize".
        Patcher presets are stored with a format of `PluginState`."""

    # * Properties
    ppq: int = _UIntProperty(_OneOfValidator(VALID_PPQS))
    """Pulses Per Quarter."""

    format: Format = _EnumProperty(Format)
    """The format of the the file. See `Format`."""

    channel_count: int = _UIntProperty()
    """Number of channels in the rack.

    For Patcher presets, the total number of plugins used inside it.
    """

    loop_active: bool = _BoolProperty()
    """Whether a portion of the song is selected."""

    show_info: bool = _BoolProperty()
    """Project info -> Show info on opening."""

    title: str = _StrProperty()
    """Project info -> Title."""

    comment: str = _StrProperty()
    """Project info -> Comments."""

    url: str = _StrProperty()
    """Project info -> Web link."""

    @property
    def version(self) -> str:
        """FL Studio version which was used to save the FLP.
        Changing this to a lower version will not make an FLP load magically
        inside FL Studio, as newer events and/or plugins might have been used.

        Returns:
            Optional[str]: A string of the format 'Major.Minor.Revision.Build'.
        """
        return getattr(self, "_version", None)

    # This one is quite important
    @version.setter
    def version(self, value: str):
        split = value.split(".")
        if len(split) not in (3, 4):
            raise ValueError(
                "Version should be of the format 'Major.Minor.Revision(.Build)?'."
            )
        self._events["version"].dump(value)
        self._version = value
        try:
            temp = int(split[3])
        except IndexError:
            pass
        else:
            self.version_build = temp

    regname: str = _StrProperty()
    """Jumbled up name of the artist's FL Studio username.
    Can find it out decoded in Debug log section of FL.

    *Most pirated versions of FL cause this to be stored empty.
    IL can then detect projects made from cracked FL easily.*"""

    # ? Use pathlib.Path instead of str
    data_path: str = _StrProperty()
    """Project settings -> Data folder."""

    genre: str = _StrProperty()
    """Project info -> Genre."""

    artists: str = _StrProperty()
    """Project info -> Author."""

    @property
    def tempo(self) -> Optional[float]:
        """Initial tempo of the project in BPM."""
        return getattr(self, "_tempo", None)

    @tempo.setter
    def tempo(self, value: float):
        if not (10.0 <= value <= 522.0):
            raise ValueError
        v = int(value * 1000)
        self._events["tempo"].dump(v)
        self._tempo = v

    @property
    def start_date(self) -> Optional[datetime.datetime]:
        """The date when the project was started.

        Stored in microseconds since Delphi epoch (31-December-1899).
        """
        return getattr(self, "_start_date", None)

    @start_date.setter
    def start_date(self, value: datetime.datetime):
        self.__stdata.seek(0)
        seconds = (value - self.__DELPHI_EPOCH).total_seconds()
        self.__stdata.write(Double.pack(seconds))
        self._start_date = value

    @property
    def work_time(self) -> Optional[datetime.timedelta]:
        """The total amount of time the artist(s) worked
        on the project. Stored in microseconds."""
        return getattr(self, "_work_time", None)

    @work_time.setter
    def work_time(self, value: datetime.timedelta):
        self.__stdata.seek(8)
        seconds = value.total_seconds()
        self.__stdata.write(Double.pack(seconds))
        self._work_time = value

    version_build: Optional[int] = _IntProperty()
    """`FLVersion.build` as an integer."""

    cur_pattern: Optional[int] = _IntProperty()
    """Currently selected pattern number."""

    cur_filter: Optional[int] = _IntProperty()
    """Currently selected filter channel number."""

    panning_law: Optional[PanningLaw] = _EnumProperty(PanningLaw)
    """Project settings -> Advanced -> Panning law."""

    time_sig_num: Optional[int] = _UIntProperty()
    """Time signature numerator. Project settings -> Time settings."""

    time_sig_beat: Optional[int] = _UIntProperty()
    """Time signature denominator. Project settings -> Time settings."""

    # TODO: A tuple for this
    song_loop_pos: Optional[int] = _UIntProperty()
    """If a portion of a song is selected, it is stored as 4 byte
    integer, 2b for loop start position and 2b for loop end position."""

    play_truncated_notes: Optional[bool] = _BoolProperty()
    """Whether to play truncated notes in pattern clips."""

    shuffle: Optional[int] = _UIntProperty(max_=128)
    """Global channel swing mix (ig). Min: 0, Max: 128, Default: 64."""

    main_pitch: Optional[int] = _IntProperty()
    """Master pitch.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/toolbar_panels.htm#mainpitch_slider)"""  # noqa

    main_volume: Optional[int] = _IntProperty()
    """Master volume."""

    registered: bool = _BoolProperty()
    """Whether project was saved in a purchased copy of FL or in trial mode."""

    # * Parsing logic
    def _parse_byte_event(self, e: ByteEventType):
        if e.id_ == Misc.EventID.LoopActive:
            self._parse_bool(e, "loop_active")
        elif e.id_ == Misc.EventID.ShowInfo:
            self._parse_bool(e, "show_info")
        elif e.id_ == Misc.EventID.TimeSigNum:
            self._parse_B(e, "time_sig_num")
        elif e.id_ == Misc.EventID.TimeSigBeat:
            self._parse_B(e, "time_sig_beat")
        elif e.id_ == Misc.EventID.PanningLaw:
            self._events["panning_law"] = e
            data = e.to_uint8()
            try:
                self._panning_law = self.PanningLaw(data)
            except AttributeError:
                self._panning_law = data
        elif e.id_ == Misc.EventID.PlayTruncatedNotes:
            self._parse_bool(e, "play_truncated_notes")
        elif e.id_ == Misc.EventID.Shuffle:
            self._parse_B(e, "shuffle")
        elif e.id_ == Misc.EventID.Registered:
            self._parse_bool(e, "registered")

    def _parse_word_event(self, e: WordEventType) -> None:
        if e.id_ == Misc.EventID.CurrentPatternNum:
            self._parse_H(e, "cur_pattern")
        elif e.id_ == Misc.EventID.MainPitch:
            self._parse_h(e, "main_pitch")

    def _parse_dword_event(self, e: DWordEventType):
        if e.id_ == Misc.EventID.Tempo:
            self._parseprop(e, "tempo", e.to_uint32() / 1000)
        elif e.id_ == Misc.EventID.CurrentFilterChannelNum:
            self._parse_i(e, "cur_filter")
        elif e.id_ == Misc.EventID.VersionBuild:
            self._parse_I(e, "version_build")
        elif e.id_ == Misc.EventID.SongLoopPos:
            self._parse_I(e, "song_loop_pos")

    def _parse_text_event(self, e: TextEventType):
        if e.id_ == Misc.EventID.Title:
            self._parse_s(e, "title")
        elif e.id_ == Misc.EventID.Comment:
            self._parse_s(e, "comment")
        elif e.id_ == Misc.EventID.Url:
            self._parse_s(e, "url")
        elif e.id_ == Misc.EventID._CommentRtf:
            self._parse_s(e, "comment")
        elif e.id_ == Misc.EventID.Version:
            self._parse_s(e, "version")
        elif e.id_ == Misc.EventID.RegName:
            self._parse_s(e, "regname")
        elif e.id_ == Misc.EventID.DataPath:
            self._parse_s(e, "data_path")
        elif e.id_ == Misc.EventID.Genre:
            self._parse_s(e, "genre")
        elif e.id_ == Misc.EventID.Artists:
            self._parse_s(e, "artists")

    def _parse_data_event(self, e: DataEventType):
        if e.id_ == Misc.EventID.SaveTimestamp:
            self._events["savetimestamp"] = e
            self.__stdata = BytesIOEx(e.data)
            self._start_date = Misc.__DELPHI_EPOCH + datetime.timedelta(
                days=self.__stdata.read_d()
            )
            self._work_time = datetime.timedelta(days=self.__stdata.read_d())

    def _save(self) -> List[EventType]:
        tstamp = self._events.get("savetimestamp")
        if tstamp:
            self.__stdata.seek(0)
            tstamp.dump(self.__stdata.read())
        return super()._save()
