import enum
import datetime
from typing import Optional, Union, Tuple, ValuesView

from pyflp.flobject.flobject import FLObject
from pyflp.utils import FLVersion
from pyflp.event import WordEvent, TextEvent, DataEvent, DWordEvent, ByteEvent, Event

from .enums import MiscEvent

from bytesioex import BytesIOEx

__all__ = ["Misc"]


@enum.unique
class PanningLaw(enum.IntEnum):
    Circular = 0
    Triangular = 1


VALID_PPQS: Tuple = (24, 48, 72, 96, 120, 144, 168, 192, 384, 768, 960)


class Misc(FLObject):
    """Used for storing one time events, which don't fall into any other category."""

    max_count = 1

    # region Properties
    @property
    def ppq(self) -> Optional[int]:
        """Pulses Per Quarter"""
        return getattr(self, "_ppq", None)

    @ppq.setter
    def ppq(self, value: int):
        assert (
            value in VALID_PPQS
        ), f"Invalid PPQ; expected one from {VALID_PPQS}; got {value}"
        self._ppq = value

    @property
    def format(self) -> Optional[int]:
        return getattr(self, "_format", None)

    @format.setter
    def format(self, value: int):
        self._format = value

    @property
    def channel_count(self) -> Optional[int]:
        """Total number of channels in the rack."""
        return getattr(self, "_channel_count", None)

    @channel_count.setter
    def channel_count(self, value: int):
        self._channel_count = value

    @property
    def loop_active(self) -> Optional[bool]:
        """Whether a portion of the song is selected."""
        return getattr(self, "_loop_active", None)

    @loop_active.setter
    def loop_active(self, value: bool):
        self.setprop("loop_active", value)

    @property
    def show_info(self) -> Optional[bool]:
        """Project info -> Show info on opening"""
        return getattr(self, "_show_info", None)

    @show_info.setter
    def show_info(self, value: bool):
        self.setprop("show_info", value)

    @property
    def title(self) -> Optional[str]:
        """Project info -> Title"""
        return getattr(self, "_title", None)

    @title.setter
    def title(self, value: str):
        self.setprop("title", value)

    @property
    def comment(self) -> Optional[str]:
        """Project info -> Comments"""
        return getattr(self, "_comment", None)

    @comment.setter
    def comment(self, value: str):
        self.setprop("comment", value)

    @property
    def url(self) -> Optional[str]:
        return getattr(self, "_url", None)

    @url.setter
    def url(self, value: str):
        self.setprop("url", value)

    @property
    def version(self) -> Optional[str]:
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
        assert (
            len(split) >= 3
        ), "Version should be of the format 'Major.Minor.Revision(.Build)?'."
        self.setprop("version", value)
        FLObject.fl_version = FLVersion(value)
        try:
            temp = int(split[3])
        except IndexError:
            self._log.warning("Version build not specified")
        else:
            # TODO What if this event doesn't exist?
            self.version_build = temp

    @property
    def regname(self) -> Optional[str]:
        """Jumbled up (encrypted maybe) name of the artist's FL Studio username.
        Can find it out decoded in Debug log section of FL.

        *Most pirated versions of FL cause this to be empty.
        IL can then detect projects made from cracked FL easily.*
        """
        return getattr(self, "_regname", None)

    @regname.setter
    def regname(self, value: str):
        self.setprop("regname", value)

    # TODO: Use pathlib.Path instead of str
    @property
    def data_path(self) -> Optional[str]:
        """Project settings -> Data folder"""
        return getattr(self, "_data_path", None)

    @data_path.setter
    def data_path(self, value: str):
        self.setprop("data_path", value)

    @property
    def genre(self) -> Optional[str]:
        """Project info -> Genre"""
        return getattr(self, "_genre", None)

    @genre.setter
    def genre(self, value: str):
        self.setprop("genre", value)

    @property
    def artists(self) -> Optional[str]:
        """Project info -> Author."""
        return getattr(self, "_artists", None)

    @artists.setter
    def artists(self, value: str):
        self.setprop("artists", value)

    @property
    def tempo(self) -> Optional[float]:
        """Initial tempo of the project in BPM."""
        return getattr(self, "_tempo", None)

    @tempo.setter
    def tempo(self, value: float):
        assert 10.0 <= value <= 522.0
        self.setprop("tempo", int(value * 1000))

    # TODO: Fix parsing
    @property
    def start_date(self) -> Optional[int]:
        """The date when the project was started. Stored in microseconds since Delphi epoch (31-December-1899)."""
        return getattr(self, "_start_date", None)

    @start_date.setter
    def start_date(self, value: datetime.datetime):
        self._savetimestamp_data.seek(0)
        seconds = int((value - datetime.datetime(1899, 12, 30)).total_seconds())
        self._savetimestamp_data.write(seconds.to_bytes(8, "little"))
        self._start_date = value

    @property
    def work_time(self) -> Optional[datetime.timedelta]:
        """The total amount of time the artist(s) worked on the project. Stored in microseconds."""
        return getattr(self, "_work_time", None)

    @work_time.setter
    def work_time(self, value: datetime.timedelta):
        self._savetimestamp_data.seek(8)
        seconds = int(value.total_seconds())
        self._savetimestamp_data.write(seconds.to_bytes(8, "little"))
        self._work_time = value

    @property
    def version_build(self) -> Optional[int]:
        """`pyflp.utils.FLVersion.build` as an integer,
        idk why, `MiscEvent.Version` already stores it."""
        return getattr(self, "_version_build", None)

    @version_build.setter
    def version_build(self, value: int):
        self.setprop("version_build", value)

    @property
    def current_pattern_num(self) -> Optional[int]:
        """Currently selected pattern number."""
        return getattr(self, "_current_pattern_num", None)

    @current_pattern_num.setter
    def current_pattern_num(self, value: int):
        self.setprop("current_pattern_num", value)

    @property
    def current_filterchannel_num(self) -> Optional[int]:
        """Currently selected filter channel number."""
        return getattr(self, "_current_filterchannel_num", None)

    @current_filterchannel_num.setter
    def current_filterchannel_num(self, value: int):
        self.setprop("current_filterchannel_num", value)

    @property
    def panning_law(self) -> Union[PanningLaw, int, None]:
        """Project settings -> Advanced -> Panning law."""
        return getattr(self, "_panning_law", None)

    @panning_law.setter
    def panning_law(self, value: Union[PanningLaw, int]):
        self.setprop("panning_law", value)

    @property
    def time_sig_num(self) -> Optional[int]:
        return getattr(self, "_time_sig_num", None)

    @time_sig_num.setter
    def time_sig_num(self, value: int):
        self.setprop("time_sig_num", value)

    @property
    def time_sig_beat(self) -> Optional[int]:
        return getattr(self, "_time_sig_beat", None)

    @time_sig_beat.setter
    def time_sig_beat(self, value: int):
        self.setprop("time_sig_beat", value)

    # TODO: A tuple for this
    @property
    def song_loop_pos(self) -> Optional[int]:
        """If a portion of a song is selected, it is stored as 4 byte integer,
        2b for loop start position and 2b for loop end position"""
        return getattr(self, "_song_loop_pos", None)

    @song_loop_pos.setter
    def song_loop_pos(self, value: int):
        self.setprop("song_loop_pos", value)

    @property
    def play_truncated_notes(self) -> Optional[bool]:
        return getattr(self, "_play_truncated_notes", None)

    @play_truncated_notes.setter
    def play_truncated_notes(self, value: bool):
        self.setprop("play_truncated_notes", value)

    @property
    def shuffle(self) -> Optional[int]:
        """Global channel swing mix (ig)."""
        return getattr(self, "_shuffle", None)

    @shuffle.setter
    def shuffle(self, value: int):
        self.setprop("shuffle", value)

    @property
    def main_pitch(self) -> int:
        return getattr(self, "_main_pitch", None)

    @main_pitch.setter
    def main_pitch(self, value: int):
        self.setprop("main_pitch", value)

    # * Parsing logic
    def _parse_byte_event(self, e: ByteEvent):
        if e.id == MiscEvent.LoopActive:
            self.parse_bool_prop(e, "loop_active")
        elif e.id == MiscEvent.ShowInfo:
            self.parse_bool_prop(e, "show_info")
        elif e.id == MiscEvent.TimeSigNum:
            self.parse_uint8_prop(e, "time_sig_num")
        elif e.id == MiscEvent.TimeSigBeat:
            self.parse_uint8_prop(e, "time_sig_beat")
        elif e.id == MiscEvent.PanningLaw:
            self._events["panning_law"] = e
            data = e.to_uint8()
            try:
                self._panning_law = PanningLaw(data)
            except AttributeError:
                self._panning_law = data  # type: ignore
                self._log.exception(f"Invalid panning law {data}")
        elif e.id == MiscEvent.PlayTruncatedNotes:
            self.parse_bool_prop(e, "play_truncated_notes")
        elif e.id == MiscEvent.Shuffle:
            self.parse_uint8_prop(e, "shuffle")

    def _parse_word_event(self, e: WordEvent) -> None:
        if e.id == MiscEvent.CurrentPatternNum:
            self.parse_uint16_prop(e, "current_pattern_num")
        elif e.id == MiscEvent.MainPitch:
            self.parse_int16_prop(e, "main_pitch")

    def _parse_dword_event(self, e: DWordEvent):
        if e.id == MiscEvent.Tempo:
            self.parseprop(e, "tempo", e.to_uint32() / 1000)
        elif e.id == MiscEvent.CurrentFilterChannelNum:
            self.parse_int32_prop(e, "current_filterchannel_num")
        elif e.id == MiscEvent.VersionBuild:
            self.parse_uint32_prop(e, "version_build")
        elif e.id == MiscEvent.SongLoopPos:
            self.parse_uint32_prop(e, "song_loop_pos")

    def _parse_text_event(self, e: TextEvent):
        if e.id == MiscEvent.Title:
            self.parse_str_prop(e, "title")
        elif e.id == MiscEvent.Comment:
            self.is_rtf_comment = False
            self.parse_str_prop(e, "comment")
        elif e.id == MiscEvent.Url:
            self.parse_str_prop(e, "url")
        elif e.id == MiscEvent._CommentRtf:
            self.is_rtf_comment = True
            self.parse_str_prop(e, "comment")
        elif e.id == MiscEvent.Version:
            self.parse_str_prop(e, "version")
        elif e.id == MiscEvent.RegName:
            self.parse_str_prop(e, "regname")
        elif e.id == MiscEvent.DataPath:
            self.parse_str_prop(e, "data_path")
        elif e.id == MiscEvent.Genre:
            self.parse_str_prop(e, "genre")
        elif e.id == MiscEvent.Artists:
            self.parse_str_prop(e, "artists")

    def _parse_data_event(self, e: DataEvent):
        if e.id == MiscEvent.SaveTimestamp:
            self._events["savetimestamp"] = e
            self._savetimestamp_data = BytesIOEx(e.data)
            # TODO: Raises OverflowError
            # self._start_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(microseconds=self._savetimestamp.read_uint64())
            self._start_date = self._savetimestamp_data.read_uint64()  # type: ignore
            self._work_time = datetime.timedelta(
                microseconds=self._savetimestamp_data.read_uint64()
            )

    # endregion

    def save(self) -> ValuesView[Event]:
        events = super().save()
        savetimestamp = self._events.get("savetimestamp")
        if savetimestamp:
            self._savetimestamp_data.seek(0)
            savetimestamp.dump(self._savetimestamp_data.read())
        return events

    def __init__(self):
        super().__init__()
