import enum
import datetime
from typing import Optional, ValuesView, Tuple

from pyflp.flobject.flobject import FLObject
from pyflp.bytesioex import BytesIOEx
from pyflp.utils import FLVersion
from pyflp.event import (
    WordEvent,
    TextEvent,
    DataEvent,
    DWordEvent,
    ByteEvent,
    Event
)
from pyflp.flobject.misc.event_id import MiscEventID

__all__ = ['Misc']

@enum.unique
class PanningLaw(enum.IntEnum):
    Circular = 0
    Triangular = 1

VALID_PPQS: Tuple[int] = (
    24,
    48,
    72,
    96,
    120,
    144,
    168,
    192,
    384,
    768,
    960
)

class Misc(FLObject):
    """Used for storing one time events, which don't fall into any other category."""

    max_count = 1

    #region Properties
    @property
    def ppq(self) -> Optional[int]:
        """Pulses Per Quarter"""
        return getattr(self, '_ppq', None)

    @ppq.setter
    def ppq(self, value: int):
        assert value in VALID_PPQS, \
            f"Invalid PPQ; expected one from {VALID_PPQS}; got {value}"
        self._ppq = value
        # TODO: The task of checking whether this changed lies on `Project.save()`

    @property
    def format(self) -> Optional[int]:
        return getattr(self, '_format', None)

    @format.setter
    def format(self, value: int):
        self._format = value
        # TODO: The task of checking whether this changed lies on `Project.save()`

    @property
    def channel_count(self) -> Optional[int]:
        """Total number of channels in the rack."""
        return getattr(self, '_channel_count', None)

    @channel_count.setter
    def channel_count(self, value: int):
        self._channel_count = value
        # TODO: The task of checking whether this changed lies on `Project.save()`

    @property
    def loop_active(self) -> Optional[bool]:
        """Whether a portion of the song is selected."""
        return getattr(self, '_loop_active', None)

    @loop_active.setter
    def loop_active(self, value: bool):
        self.setprop('loop_active', value)

    @property
    def show_info(self) -> Optional[bool]:
        """Project info -> Show info on opening"""
        return getattr(self, '_show_info', None)

    @show_info.setter
    def show_info(self, value: bool):
        self.setprop('show_info', value)

    @property
    def title(self):
        """Project info -> Title"""
        return getattr(self, '_title', None)

    @title.setter
    def title(self, value: str):
        self.setprop('title', value)

    @property
    def comment(self):
        """Project info -> Comments"""
        return getattr(self, '_comment', None)

    @comment.setter
    def comment(self, value: str):
        self.setprop('comment', value)

    @property
    def url(self) -> Optional[str]:
        return getattr(self, '_url', None)

    @url.setter
    def url(self, value: str):
        self.setprop('url', value)

    @property
    def version(self) -> Optional[str]:
        """FL Studio version which was used to save the FLP.
        Changing this to a lower version will not make an FLP load magically
        inside FL Studio, as newer events and/or plugins might have been used.

        Returns:
            Optional[str]: A string of the format 'Major.Minor.Revision.Build'.
        """
        return getattr(self, '_version', None)

    # This one is quite important
    @version.setter
    def version(self, value: str):
        split = value.split('.')
        assert len(split) == 4, "Version string should be of the format 'Major.Minor.Revision.Build'."
        self.setprop('version', value)
        FLObject.fl_version = FLVersion(value)
        self.version_build = int(split[3])

    @property
    def regname(self) -> Optional[str]:
        """Jumbled up (encrypted maybe) name of the artist's FL Studio username.
        Can find it out decoded in Debug log section of FL.

        *Most pirated versions of FL cause this to be empty.
        IL can then detect projects made from cracked FL easily.*
        """
        return getattr(self, '_regname', None)

    @regname.setter
    def regname(self, value: str):
        self.setprop('regname', value)

    # TODO: Use pathlib.Path instead of str
    @property
    def data_path(self) -> Optional[str]:
        """Project settings -> Data folder"""
        return getattr(self, '_data_path', None)

    @data_path.setter
    def data_path(self, value: str):
        self.setprop('data_path', value)

    @property
    def genre(self) -> Optional[str]:
        """Project info -> Genre"""
        return getattr(self, '_genre', None)

    @genre.setter
    def genre(self, value: str):
        self.setprop('genre', value)

    @property
    def artists(self) -> Optional[str]:
        """Project info -> Author."""
        return getattr(self, '_artists', None)

    @artists.setter
    def artists(self, value: str):
        self.setprop('artists', value)

    @property
    def tempo(self) -> Optional[float]:
        """Initial tempo of the project in BPM."""
        return getattr(self, '_tempo', None)

    @tempo.setter
    def tempo(self, value: float):
        assert 10.0 <= value <= 522.0
        self.setprop('tempo', int(value * 1000))

    # TODO: Fix parsing
    @property
    def start_date(self) -> Optional[int]:
        """The date when the project was started. Stored in microseconds since Delphi epoch (31-December-1899)."""
        return getattr(self, '_start_date', None)

    @start_date.setter
    def start_date(self, value: datetime.datetime):
        self._savetimestamp_data.seek(0)
        seconds = int((value - datetime.datetime(1899, 12, 30)).total_seconds())
        self._savetimestamp_data.write(seconds.to_bytes(8, 'little'))
        self._start_date = value

    @property
    def work_time(self) -> Optional[datetime.timedelta]:
        """The total amount of time the artist(s) worked on the project. Stored in microseconds."""
        return getattr(self, '_work_time', None)

    @work_time.setter
    def work_time(self, value: datetime.timedelta):
        self._savetimestamp_data.seek(8)
        seconds = int(value.total_seconds())
        self._savetimestamp_data.write(seconds.to_bytes(8, 'little'))
        self._work_time = value

    @property
    def version_build(self) -> Optional[int]:
        """`pyflp.utils.FLVersion.build` stored as an integer, idk for what reason,
        the `MiscEventID.Version` event already stores it."""
        return getattr(self, '_version_build', None)

    @version_build.setter
    def version_build(self, value: int):
        self.setprop('version_build', value)

    @property
    def current_pattern_num(self) -> Optional[int]:
        """Currently selected pattern number."""
        return getattr(self, '_current_pattern_num', None)

    @current_pattern_num.setter
    def current_pattern_num(self, value: int):
        self.setprop('current_pattern_num', value)

    @property
    def current_filterchannel_num(self) -> Optional[int]:
        """Currently selected filter channel number."""
        return getattr(self, '_current_filterchannel_num', None)

    @current_filterchannel_num.setter
    def current_filterchannel_num(self, value: int):
        self.setprop('current_filterchannel_num', value)

    @property
    def panning_law(self) -> Optional[PanningLaw]:
        """Project settings -> Advanced -> Panning law."""
        return getattr(self, '_panning_law', None)

    @panning_law.setter
    def panning_law(self, value: PanningLaw):
        self.setprop('panning_law', value)

    @property
    def time_sig_num(self) -> Optional[int]:
        return getattr(self, '_time_sig_num', None)

    @time_sig_num.setter
    def time_sig_num(self, value: int):
        self.setprop('time_sig_num', value)

    @property
    def time_sig_beat(self) -> Optional[int]:
        return getattr(self, '_time_sig_beat', None)

    @time_sig_beat.setter
    def time_sig_beat(self, value: int):
        self.setprop('time_sig_beat', value)

    @property
    def song_loop_pos(self) -> Optional[int]:
        """If a portion of a song is selected, it is stored as 4 byte integer,
        2b for loop start position and 2b for loop end position, TODO a tuple for this."""
        return getattr(self, '_song_loop_pos', None)

    @song_loop_pos.setter
    def song_loop_pos(self, value: int):
        self.setprop('song_loop_pos', value)

    @property
    def play_truncated_notes(self) -> Optional[bool]:
        return getattr(self, '_play_truncated_notes', None)

    @play_truncated_notes.setter
    def play_truncated_notes(self, value: bool):
        self.setprop('play_truncated_notes', value)

    @property
    def shuffle(self) -> Optional[int]:
        """Global channel swing mix (ig)."""
        return getattr(self, '_shuffle', None)

    @shuffle.setter
    def shuffle(self, value: int):
        self.setprop('shuffle', value)
    #endregion

    #region Parsing logic
    def _parse_byte_event(self, event: ByteEvent):
        if event.id == MiscEventID.LoopActive:
            self.parse_bool_prop(event, 'loop_active')
        elif event.id == MiscEventID.ShowInfo:
            self.parse_bool_prop(event, 'show_info')
        elif event.id == MiscEventID.TimeSigNum:
            self.parse_uint8_prop(event, 'time_sig_num')
        elif event.id == MiscEventID.TimeSigBeat:
            self.parse_uint8_prop(event, 'time_sig_beat')
        elif event.id == MiscEventID.PanningLaw:
            self._events['panning_law'] = event
            data = event.to_uint8()
            try:
                self._panning_law = PanningLaw(data)
            except AttributeError as e:
                self._panning_law = data
                self._log.error(f"Invalid panning law; expected {PanningLaw.__members__}; got {data}")
        elif event.id == MiscEventID.PlayTruncatedNotes:
            self.parse_bool_prop(event, 'play_truncated_notes')
        elif event.id == MiscEventID.Shuffle:
            self.parse_uint8_prop(event, 'shuffle')

    def _parse_word_event(self, event: WordEvent) -> None:
        if event.id == MiscEventID.CurrentPatternNum:
            self.parse_uint16_prop(event, 'current_pattern_num')

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == MiscEventID.Tempo:
            self.parseprop(event, 'tempo', event.to_uint32() / 1000)
        elif event.id == MiscEventID.CurrentFilterChannelNum:
            self.parse_int32_prop(event, 'current_filterchannel_num')
        elif event.id == MiscEventID.VersionBuild:
            self.parse_uint32_prop(event, 'version_build')
        elif event.id == MiscEventID.SongLoopPos:
            self.parse_uint32_prop(event, 'song_loop_pos')

    def _parse_text_event(self, event: TextEvent):
        if event.id == MiscEventID.Title:
            self.parse_str_prop(event, 'title')
        elif event.id == MiscEventID.Comment:
            self.is_rtf_comment = False
            self.parse_str_prop(event, 'comment')
        elif event.id == MiscEventID.Url:
            self.parse_str_prop(event, 'url')
        elif event.id == MiscEventID._CommentRtf:
            self.is_rtf_comment = True
            self.parse_str_prop(event, 'comment')
        elif event.id == MiscEventID.Version:
            self.parse_str_prop(event, 'version')
        elif event.id == MiscEventID.RegName:
            self.parse_str_prop(event, 'regname')
        elif event.id == MiscEventID.DataPath:
            self.parse_str_prop(event, 'data_path')
        elif event.id == MiscEventID.Genre:
            self.parse_str_prop(event, 'genre')
        elif event.id == MiscEventID.Artists:
            self.parse_str_prop(event, 'artists')

    def _parse_data_event(self, event: DataEvent):
        if event.id == MiscEventID.SaveTimestamp:
            self._events['savetimestamp'] = event
            self._savetimestamp_data = BytesIOEx(event.data)
            # TODO: Raises OverflowError
            # self._start_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(microseconds=self._savetimestamp.read_uint64())
            self._start_date = self._savetimestamp_data.read_uint64()
            self._work_time = datetime.timedelta(microseconds=self._savetimestamp_data.read_uint64())
    #endregion

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")

        savetimestamp = self._events.get('savetimestamp')
        if savetimestamp:
            self._savetimestamp_data.seek(0)
            savetimestamp.dump(self._savetimestamp_data.read())

        return super().save()

    def __init__(self):
        super().__init__()