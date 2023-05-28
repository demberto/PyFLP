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

"""Contains the class (and types it uses) used by the parser and serializer."""

from __future__ import annotations

import datetime
import enum
import math
import pathlib
from typing import Final, Literal, cast

import construct as c
import construct_typed as ct
from typing_extensions import TypedDict, Unpack

from pyflp._descriptors import EventProp, KWProp
from pyflp._events import (
    DATA,
    DWORD,
    TEXT,
    WORD,
    AnyEvent,
    AsciiEvent,
    BoolEvent,
    EventEnum,
    EventTree,
    I16Event,
    I32Event,
    StructEventBase,
    U8Event,
    U32Event,
)
from pyflp._models import EventModel
from pyflp.arrangement import ArrangementID, Arrangements, ArrangementsID, TrackID
from pyflp.channel import ChannelID, ChannelRack, DisplayGroupID, RackID
from pyflp.exceptions import PropertyCannotBeSet
from pyflp.mixer import InsertID, Mixer, MixerID, SlotID
from pyflp.pattern import PatternID, Patterns, PatternsID
from pyflp.plugin import PluginID
from pyflp.timemarker import TimeMarkerID
from pyflp.types import FLVersion

__all__ = ["PanLaw", "Project", "FileFormat", "VALID_PPQS"]

_DELPHI_EPOCH: Final = datetime.datetime(1899, 12, 30)
MIN_TEMPO: Final = 10.000
"""Minimum tempo (in BPM) FL Studio supports."""

VALID_PPQS: Final = (24, 48, 72, 96, 120, 144, 168, 192, 384, 768, 960)
"""PPQs / timebase supported by FL Studio as of its latest version."""


class TimestampEvent(StructEventBase):
    STRUCT = c.Struct("created_on" / c.Float64l, "time_spent" / c.Float64l).compile()


@enum.unique
class PanLaw(ct.EnumBase):
    """Used by :attr:`Project.pan_law`."""

    Circular = 0
    Triangular = 2


@enum.unique
class FileFormat(enum.IntEnum):
    """File formats used by FL Studio.

    *New in FL Studio v2.5.0*: FST (FL Studio state) file format.
    """

    None_ = -1
    """Temporary file."""

    Project = 0
    """FL Studio project (.flp)."""

    Score = 0x10
    """FL Studio score (.fsc). Stores pattern notes and controller events."""

    Automation = 24
    """Stores controller events and automation channels as FST."""

    ChannelState = 0x20
    """Entire channel (including plugin events). Stored as FST."""

    PluginState = 0x30
    """Events of a native plugin on a channel or insert slot. Stored as FST."""

    GeneratorState = 0x31
    """Plugins events of a VST instrument. Stored as FST."""

    FXState = 0x32
    """Plugin events of a VST effect. Stored as FST."""

    InsertState = 0x40
    """Insert and all its slots. Stored as FST."""

    _ProbablyPatcher = 0x50  # * Patcher presets are stored as `PluginState`.


class ProjectID(EventEnum):
    LoopActive = (9, BoolEvent)
    ShowInfo = (10, BoolEvent)
    _Volume = (12, U8Event)
    PanLaw = (23, U8Event)
    Licensed = (28, BoolEvent)
    _TempoCoarse = WORD + 2
    Pitch = (WORD + 16, I16Event)
    _TempoFine = WORD + 29  #: 3.4.0+
    CurGroupId = (DWORD + 18, I32Event)
    Tempo = (DWORD + 28, U32Event)
    FLBuild = (DWORD + 31, U32Event)
    Title = TEXT + 2
    Comments = TEXT + 3
    Url = TEXT + 5
    _RTFComments = TEXT + 6  #: 1.2.10+
    FLVersion = (TEXT + 7, AsciiEvent)
    Licensee = TEXT + 8  #: 1.3.9+
    DataPath = TEXT + 10  #: 9.0+
    Genre = TEXT + 14  #: 5.0+
    Artists = TEXT + 15  #: 5.0+
    Timestamp = (DATA + 29, TimestampEvent)


class _ProjectKW(TypedDict):
    channel_count: int
    ppq: int
    format: FileFormat


class Project(EventModel):
    """Represents an FL Studio project."""

    def __init__(self, events: EventTree, **kw: Unpack[_ProjectKW]) -> None:
        super().__init__(events, **kw)

    def __repr__(self) -> str:
        return f"<Project(format={self.format!r}, version={self.version!r}>"

    def __str__(self) -> str:
        return f"FL Studio v{self.version!s} {self.format.name}"  # type: ignore

    @property
    def arrangements(self) -> Arrangements:
        """Provides an iterator over arrangements and other related properties."""
        arrnew_occured = False

        def select(e: AnyEvent) -> Literal[True] | None:
            nonlocal arrnew_occured

            if e.id == ArrangementID.New:
                arrnew_occured = True

            # * Prevents accidentally passing on Pattern's timemarkers
            # TODO This logic will still be incorrect if arrangement's
            # timemarkers occur before ArrangementID.New event.
            if e.id in TimeMarkerID and arrnew_occured:
                return True

            if e.id in (*ArrangementID, *ArrangementsID, *TrackID):
                return True

        return Arrangements(
            self.events.subtree(select),
            channels=self.channels,
            patterns=self.patterns,
            version=self.version,
        )

    artists = EventProp[str](ProjectID.Artists)
    """Authors / artists info. to be embedded in exported WAV & MP3.

    :menuselection:`Options --> &Project info --> Author`

    *New in FL Studio v5.0.*
    """

    @property
    def channel_count(self) -> int:
        """Number of channels in the rack.

        For Patcher presets, the total number of plugins used inside it.

        Raises:
            ValueError: When a value less than zero is tried to be set.
        """
        return self._kw["channel_count"]

    @channel_count.setter
    def channel_count(self, value: int) -> None:
        if value < 0:
            raise ValueError("Channel count cannot be less than zero")
        self._kw["channel_count"] = value

    @property
    def channels(self) -> ChannelRack:
        """Provides an iterator over channels and channel rack properties."""

        def select(e: AnyEvent) -> bool | None:
            if e.id == InsertID.Flags:
                return False

            if e.id in (*ChannelID, *DisplayGroupID, *PluginID, *RackID):
                return True

        return ChannelRack(
            self.events.subtree(select),
            channel_count=self.channel_count,
        )

    comments = EventProp[str](ProjectID.Comments, ProjectID._RTFComments)
    """Comments / project description / summary.

    :menuselection:`Options --> &Project info --> Comments`

    Caution:
        Very old versions of FL used to store comments in RTF (Rich Text Format).
        PyFLP makes no efforts to parse that and stores it like a normal string
        as it is. It is upto you to extract the text out of it.
    """

    # Stored as a duration in days since the Delphi epoch (30 Dec, 1899).
    @property
    def created_on(self) -> datetime.datetime | None:
        """The local date and time on which this project was created.

        Located at the bottom of :menuselection:`Options --> &Project info` page.
        """
        if ProjectID.Timestamp in self.events.ids:
            event = cast(TimestampEvent, self.events.first(ProjectID.Timestamp))
            return _DELPHI_EPOCH + datetime.timedelta(days=event["created_on"])

    format = KWProp[FileFormat]()
    """Internal format marker used by FL Studio to distinguish between types."""

    @property
    def data_path(self) -> pathlib.Path | None:
        """The absolute path used by FL to store all your renders.

        :menuselection:`Options --> &Project general settings --> Data folder`

        *New in FL Studio v9.0.0.*
        """
        if ProjectID.DataPath in self.events.ids:
            return pathlib.Path(self.events.first(ProjectID.DataPath).value)

    @data_path.setter
    def data_path(self, value: str | pathlib.Path) -> None:
        if ProjectID.DataPath not in self.events.ids:
            raise PropertyCannotBeSet(ProjectID.DataPath)

        if isinstance(value, pathlib.Path):
            value = str(value)

        path = "" if value == "." else value
        self.events.first(ProjectID.DataPath).value = path

    genre = EventProp[str](ProjectID.Genre)
    """Genre of the song to be embedded in exported WAV & MP3.

    :menuselection:`Options --> &Project info --> Genre`

    *New in FL Studio v5.0*.
    """

    licensed = EventProp[bool](ProjectID.Licensed)
    """Whether the project was last saved with a licensed copy of FL Studio.

    Tip:
        Setting this to `True` and saving back the FLP will make it load the
        next time in a trial version of FL if it wouldn't open before.
    """

    # Internally, this is jumbled up. Thanks to @codecat/libflp for decode algo.
    @property
    def licensee(self) -> str | None:
        """The license holder's username who last saved the project file.

        If saved with a trial version this is empty.

        Tip:
            As of the latest version, FL doesn't check for the contents of
            this for deciding whether to open or not when in trial version.

        *New in FL Studio v1.3.9*.
        """
        if ProjectID.Licensee in self.events.ids:
            event = self.events.first(ProjectID.Licensee)
            licensee = bytearray()
            for idx, char in enumerate(event.value):
                c1 = ord(char) - 26 + idx
                c2 = ord(char) + 49 + idx
                for num in c1, c2:
                    if chr(num).isalnum():
                        licensee.append(num)
                        break

            return licensee.decode("ascii")

    @licensee.setter
    def licensee(self, value: str) -> None:
        if self.version < FLVersion(1, 3, 9):
            pass

        if ProjectID.Licensee not in self.events.ids:
            raise PropertyCannotBeSet(ProjectID.Licensee)

        event = self.events.first(ProjectID.Licensee)
        licensee = bytearray()
        for idx, char in enumerate(value):
            c1 = ord(char) + 26 - idx
            c2 = ord(char) - 49 - idx
            for cp in c1, c2:
                if 0 < cp <= 127:
                    licensee.append(cp)
                    break
        event.value = licensee.decode("ascii")

    looped = EventProp[bool](ProjectID.LoopActive)
    """Whether a portion of the playlist is selected."""

    main_pitch = EventProp[int](ProjectID.Pitch)
    """:guilabel:`Master pitch` (in cents). Min = -1200. Max = +1200. Defaults to 0."""

    main_volume = EventProp[int](ProjectID._Volume)
    """*Changed in FL Studio v1.7.6*: Can be upto 125% (+5.6dB) now."""

    @property
    def mixer(self) -> Mixer:
        """Provides an iterator over inserts and other mixer related properties."""
        inserts_began = False

        def select(e: AnyEvent) -> Literal[True] | None:
            nonlocal inserts_began
            if e.id in (*MixerID, *InsertID, *SlotID):
                # TODO Find a more reliable to detect when inserts start.
                inserts_began = True
                return True

            if inserts_began and e.id in PluginID:
                return True

        return Mixer(self.events.subtree(select), version=self.version)

    @property
    def patterns(self) -> Patterns:
        """Returns a collection of patterns and other related properties."""
        arrnew_occured = False

        def select(e: AnyEvent) -> Literal[True] | None:
            nonlocal arrnew_occured

            if e.id == ArrangementID.New:
                arrnew_occured = True

            # * Prevents accidentally passing on Arrangement's timemarkers
            elif e.id in TimeMarkerID and not arrnew_occured:
                return True

            elif e.id in (*PatternID, *PatternsID):
                return True

        return Patterns(self.events.subtree(select))

    pan_law = EventProp[PanLaw](ProjectID.PanLaw)
    """Whether a circular or a triangular pan law is used for the project.

    :menuselection:`Options -> &Project general settings -> Advanced -> Panning law`
    """

    @property
    def ppq(self) -> int:
        """Pulses per quarter.

        ![](https://bit.ly/3F0UrMT)

        :menuselection:`Options --> &Project general settings --> Timebase (PPQ)`.

        Note:
            All types of lengths, positions and offsets internally use the PPQ
            as a multiplying factor.

        Danger:
            Don't try to set this property, it affects all the length, position
            and offset calculations used for deciding the placement of playlist,
            automations, timemarkers and patterns.

            When you change this in FL, it recalculates all the above. It is
            beyond PyFLP's scope to properly recalculate the timings.

        Raises:
            ValueError: When a value not in ``VALID_PPQS`` is tried to be set.

        *Changed in FL Studio v2.1.1*: Defaults to ``96``.
        """
        return self._kw["ppq"]

    @ppq.setter
    def ppq(self, value: int) -> None:
        if value not in VALID_PPQS:
            raise ValueError(f"Expected one of {VALID_PPQS}; got {value} instead")
        self._kw["ppq"] = value

    show_info = EventProp[bool](ProjectID.ShowInfo)
    """Whether to show a banner while the project is loading inside FL Studio.

    :menuselection:`Options --> &Project info --> Show info on opening`

    The banner shows the :attr:`title`, :attr:`artists`, :attr:`genre`,
    :attr:`comments` and :attr:`url`.
    """

    title = EventProp[str](ProjectID.Title)
    """Name of the song / project.

    :menuselection:`Options --> &Project info --> Title`
    """

    # Stored internally as the actual BPM * 1000 as an integer.
    @property
    def tempo(self) -> int | float | None:
        """Tempo at the current position of the playhead (in BPM).

        ![](https://bit.ly/3MKdAEO)

        Raises:
            TypeError: When a fine-tuned tempo (``float``) isn't
                supported. Use an ``int`` (coarse tempo) value.
            PropertyCannotBeSet: If underlying event isn't found.
            ValueError: When a tempo outside the allowed range is set.

        * *Changed in FL Studio v1.4.2*: Max tempo increased to ``999`` (int).
        * *New in FL Studio v3.4.0*: Fine tuned tempo (a float).
        * *Changed in FL Studio v11*: Max tempo limited to ``522.000``.
            Probably when tempo automations
        """
        if ProjectID.Tempo in self.events.ids:
            return self.events.first(ProjectID.Tempo).value / 1000

        tempo = None
        if ProjectID._TempoCoarse in self.events.ids:
            tempo = self.events.first(ProjectID._TempoCoarse).value
        if ProjectID._TempoFine in self.events.ids:
            tempo += self.events.first(ProjectID._TempoFine).value / 1000
        return tempo

    @tempo.setter
    def tempo(self, value: int | float) -> None:
        if self.tempo is None:
            raise PropertyCannotBeSet(ProjectID.Tempo, ProjectID._TempoCoarse, ProjectID._TempoFine)

        max_tempo = 999.0 if FLVersion(1, 4, 2) <= self.version < FLVersion(11) else 522.0

        if isinstance(value, float) and self.version < FLVersion(3, 4, 0):
            raise TypeError("Expected an 'int' object got a 'float' instead")

        if float(value) > max_tempo or float(value) < MIN_TEMPO:
            raise ValueError(f"Invalid tempo {value}; expected {MIN_TEMPO}-{max_tempo}")

        if ProjectID.Tempo in self.events.ids:
            self.events.first(ProjectID.Tempo).value = int(value * 1000)

        if ProjectID._TempoFine in self.events.ids:
            tempo_fine = int((value - math.floor(value)) * 1000)
            self.events.first(ProjectID._TempoFine).value = tempo_fine

        if ProjectID._TempoCoarse in self.events.ids:
            self.events.first(ProjectID._TempoCoarse).value = math.floor(value)

    @property
    def time_spent(self) -> datetime.timedelta | None:
        """Time spent on the project since its creation.

        ![](https://bit.ly/3TsBzdM)

        Located at the bottom of :menuselection:`Options --> &Project info` page.
        """
        if ProjectID.Timestamp in self.events.ids:
            event = cast(TimestampEvent, self.events.first(ProjectID.Timestamp))
            return datetime.timedelta(days=event["time_spent"])

    url = EventProp[str](ProjectID.Url)
    """:menuselection:`Options --> &Project info --> Web link`."""

    # Internally represented as a string with a format of
    # `major.minor.patch.build?` *where `build` is optional, since older
    # versions of FL didn't follow the same versioning scheme*.
    #
    # To maintain backward compatibility with FL Studio prior to v11.5 which
    # stored strings in ASCII, this event is always stored with ASCII data,
    # even if the rest of the strings use Windows Unicode (UTF16).
    @property
    def version(self) -> FLVersion:
        """The version of FL Studio which was used to save the file.

        ![](https://bit.ly/3TD3BU0)

        Located at the top of :menuselection:`Help --> &About` page.

        Caution:
            Changing this to a lower version will not make a file load magically
            inside FL Studio, as newer events and/or plugins might have been used.

        Raises:
            PropertyCannotBeSet: This error should NEVER occur; if it does,
                it indicates possible corruption.
            ValueError: When a string with an invalid format is tried to be set.
        """
        event = cast(AsciiEvent, self.events.first(ProjectID.FLVersion))
        return FLVersion(*tuple(int(part) for part in event.value.split(".")))

    @version.setter
    def version(self, value: FLVersion | str | tuple[int, ...]) -> None:
        if ProjectID.FLVersion not in self.events.ids:
            raise PropertyCannotBeSet(ProjectID.FLVersion)

        if isinstance(value, FLVersion):
            parts = [value.major, value.minor, value.patch]
            if value.build is not None:
                parts.append(value.build)
        elif isinstance(value, str):
            parts = [int(part) for part in value.split(".")]
        else:
            parts = list(value)

        if len(parts) < 3 or len(parts) > 4:
            raise ValueError("Expected format: major.minor.build.patch?")

        version = ".".join(str(part) for part in parts)
        self.events.first(ProjectID.FLVersion).value = version
        if len(parts) == 4 and ProjectID.FLBuild in self.events.ids:
            self.events.first(ProjectID.FLBuild).value = parts[3]
