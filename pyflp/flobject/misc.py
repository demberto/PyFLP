import enum
import dataclasses
import datetime
from typing import Optional

from pyflp.flobject.flobject import *
from pyflp.bytesioex import BytesIOEx
from pyflp.utils import *

@enum.unique
class PanningLaw(enum.IntEnum):
    Circular = 0
    Triangular = 1

@enum.unique
class MiscEventID(enum.IntEnum):
    Version = TEXT + 7
    VersionBuild = DWORD + 31
    LoopActive = 9
    ShowInfo = 10
    #Shuffle = 11
    #_MainVol = 12
    #_FitToSteps = 13
    #TimeSigNum = 17
    #TimeSigBeat = 18
    PanningLaw = 23
    #PlayTruncatedNotes = 30
    #_Tempo = WORD + 2
    CurrentPatternNum = WORD + 3
    #_MainPitch = WORD + 16
    #_TempoFine = WORD + 29
    CurrentFilterChannelNum = DWORD + 18
    #SongLoopPos = DWORD + 24
    Tempo = DWORD + 28
    Title = TEXT + 2
    Comment = TEXT + 3
    Url = TEXT + 5
    _CommentRtf = TEXT + 6
    RegName = TEXT + 8
    DataPath = TEXT + 10
    Genre = TEXT + 14
    Artists = TEXT + 15
    SaveTimestamp = DATA + 28

@dataclasses.dataclass
class Misc(FLObject):
    ppq: int = dataclasses.field(init=False)
    format: int = dataclasses.field(init=False)
    channel_count: int = dataclasses.field(init=False)
    
    _count = 0
    max_count = 1

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
        return getattr(self, '_regname', None)

    @regname.setter
    def regname(self, value: str):
        self.setprop('regname', value)

    # TODO: Use pathlib.Path instead of str
    @property
    def data_path(self) -> Optional[str]:
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
        """Project info -> Author.
        I like to call it 'artists' because it is not a book :)
        """
        return getattr(self, '_artists', None)

    @artists.setter
    def artists(self, value: str):
        self.setprop('artists', value)

    @property
    def tempo(self) -> Optional[float]:
        """BPM"""
        return getattr(self, '_tempo', None)

    @tempo.setter
    def tempo(self, value: float):
        assert 10.0 <= value <= 522.0
        self.setprop('tempo', int(value * 1000))

    # TODO: Fix parsing
    @property
    def start_date(self) -> Optional[int]:
        return getattr(self, '_start_date', None)

    @start_date.setter
    def start_date(self, value: datetime.datetime):
        self._savetimestamp_data.seek(0)
        seconds = int((value - datetime.datetime(1899, 12, 30)).total_seconds())
        self._savetimestamp_data.write(seconds.to_bytes(8, 'little'))
        self._start_date = value

    @property
    def work_time(self) -> Optional[datetime.timedelta]:
        return getattr(self, '_work_time', None)

    @work_time.setter
    def work_time(self, value: datetime.timedelta):
        self._savetimestamp_data.seek(8)
        seconds = int(value.total_seconds())
        self._savetimestamp_data.write(seconds.to_bytes(8, 'little'))
        self._work_time = value

    @property
    def version_build(self) -> Optional[int]:
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
        """Currently selected pattern number."""
        return getattr(self, '_panning_law', None)

    @panning_law.setter
    def panning_law(self, value: PanningLaw):
        self.setprop('panning_law', value)

    def _parse_byte_event(self, event: ByteEvent):
        if event.id == MiscEventID.LoopActive:
            self._events['loop_active'] = event
            self._loop_active = event.to_bool()
        elif event.id == MiscEventID.ShowInfo:
            self._events['show_info'] = event
            self._show_info = event.to_bool()
        elif event.id == MiscEventID.PanningLaw:
            self._events['panning_law'] = event
            try:
                self._panning_law = PanningLaw(event.to_uint8())
            except AttributeError as e:
                self._log.error(f"Invalid panning law; expected {PanningLaw.__members__.values()}; got {event.to_uint8()}")

    def _parse_word_event(self, event: WordEvent) -> None:
        if event.id == MiscEventID.CurrentPatternNum:
            self._events['current_pattern_num'] = event
            self._current_pattern_num = event.to_uint16()

    def _parse_dword_event(self, event: DWordEvent):
        if event.id == MiscEventID.Tempo:
            self._events['tempo'] = event
            self._tempo = event.to_uint32() / 1000
        elif event.id == MiscEventID.CurrentFilterChannelNum:
            self._events['current_filterchannel_num'] = event
            self._current_filterchannel_num = event.to_int32()
        elif event.id == MiscEventID.VersionBuild:
            self._events['version_build'] = event
            self._version_build = event.to_uint32()

    def _parse_text_event(self, event: TextEvent):
        if event.id == MiscEventID.Title:
            self._events['title'] = event
            self._title = event.to_str()
        elif event.id == MiscEventID.Comment:
            self._events['comment'] = event
            self._comment = event.to_str()
        elif event.id == MiscEventID.Url:
            self._events['url'] = event
            self._url = event.to_str()
        elif event.id == MiscEventID._CommentRtf:
            self._events['comment'] = event
            self._comment = event.to_str()
        elif event.id == MiscEventID.Version:
            self._events['version'] = event
            self._version = event.to_str()
        elif event.id == MiscEventID.RegName:
            self._events['regname'] = event
            self._regname = event.to_str()
        elif event.id == MiscEventID.DataPath:
            self._events['data_path'] = event
            self._data_path = event.to_str()
        elif event.id == MiscEventID.Genre:
            self._events['genre'] = event
            self._genre = event.to_str()
        elif event.id == MiscEventID.Artists:
            self._events['artists'] = event
            self._artists = event.to_str()

    def _parse_data_event(self, event: DataEvent):
        if event.id == MiscEventID.SaveTimestamp:
            self._events['savetimestamp'] = event
            self._savetimestamp_data = BytesIOEx(event.data)
            # TODO: Raises OverflowError
            # self._start_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(microseconds=self._savetimestamp.read_uint64())
            self._start_date = self._savetimestamp_data.read_uint64()
            self._work_time = datetime.timedelta(microseconds=self._savetimestamp_data.read_uint64())

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        _savetimestamp_ev = self._events.get('savetimestamp')
        if _savetimestamp_ev:
            self._savetimestamp_data.seek(0)
            _savetimestamp_ev.dump(self._savetimestamp_data.read())
        else:
            self._log.info("Save timestamp event absent")
        return super().save()

    def __init__(self):
        super().__init__()
        self._log.info("__init__()")