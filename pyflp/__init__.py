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

"""
PyFLP - FL Studio project file parser
=====================================

Load a project file:

    >>> import pyflp
    >>> project = pyflp.parse("/path/to/parse.flp")

Save the project:

    >>> pyflp.save(project, "/path/to/save.flp")

Full docs are available at https://pyflp.rtfd.io.
"""  # noqa

from __future__ import annotations

import os
import pathlib

from bytesioex import BytesIOEx

from ._events import (
    DATA,
    DWORD,
    NEW_TEXT_IDS,
    TEXT,
    WORD,
    AnyEvent,
    AsciiEvent,
    EventEnum,
    U8Event,
    U16Event,
    U32Event,
    UnicodeEvent,
    UnknownDataEvent,
)
from .exceptions import HeaderCorrupted, VersionNotDetected
from .plugin import PluginID, get_event_by_internal_name
from .project import VALID_PPQS, FileFormat, Project, ProjectID

__all__ = ["parse", "save"]
__version__ = "2.0.0a1"


def parse(file: str | pathlib.Path) -> Project:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # pylint: disable=too-complex
    """Parse an FL Studio project file.

    Args:
        file (str | pathlib.Path): Path to the FLP.

    Raises:
        HeaderCorrupted: When an invalid value is found in the file header.
        VersionNotDetected: A correct string type couldn't be determined.

    Returns:
        Project: The parsed object.
    """
    with open(file, "rb") as flp:
        stream = BytesIOEx(flp.read())

    events: list[AnyEvent] = []

    if stream.read(4) != b"FLhd":  # 4
        raise HeaderCorrupted("Unexpected header chunk magic; expected 'FLhd'")

    if stream.read_I() != 6:  # 8
        raise HeaderCorrupted("Unexpected header chunk size; expected 6")

    format = stream.read_H()  # 10
    try:
        format = FileFormat(format)
    except ValueError as exc:
        raise HeaderCorrupted("Unsupported project file format") from exc

    channel_count = stream.read_H()  # 12
    if channel_count is None:
        raise HeaderCorrupted("Channel count couldn't be read")
    if channel_count < 0:
        raise HeaderCorrupted("Channel count can't be less than zero")

    ppq = stream.read_H()  # 14
    if ppq not in VALID_PPQS:
        raise HeaderCorrupted("Invalid PPQ")

    if stream.read(4) != b"FLdt":  # 18
        raise HeaderCorrupted("Unexpected data chunk magic; expected 'FLdt'")

    events_size = stream.read_I()  # 22
    if events_size is None:
        raise HeaderCorrupted("Data chunk size couldn't be read")

    stream.seek(0, os.SEEK_END)
    file_size = stream.tell()
    if file_size != events_size + 22:
        raise HeaderCorrupted("Data chunk size corrupted")

    plug_name = None
    str_type = None
    stream.seek(22)  # Back to start of events
    while True:
        event_type: type[AnyEvent] | None = None
        id = stream.read_B()
        if id is None:
            break

        if id < WORD:
            value = stream.read(1)
        elif id < DWORD:
            value = stream.read(2)
        elif id < TEXT:
            value = stream.read(4)
        else:
            value = stream.read(stream.read_v())

        if id == ProjectID.FLVersion:
            parts = value.decode("ascii").rstrip("\0").split(".")
            if [int(part) for part in parts][0:2] >= [11, 5]:
                str_type = UnicodeEvent
            else:
                str_type = AsciiEvent

        for enum_type in EventEnum.__subclasses__():
            if id in enum_type:
                event_type = getattr(enum_type(id), "type")
                break

        if event_type is None:
            if id < WORD:
                event_type = U8Event
            elif id < DWORD:
                event_type = U16Event
            elif id < TEXT:
                event_type = U32Event
            elif id < DATA or id in NEW_TEXT_IDS:
                if str_type is None:
                    raise VersionNotDetected
                event_type = str_type

                if id == PluginID.InternalName:
                    plug_name = event_type(id, value).value
            elif id == PluginID.Data and plug_name is not None:
                event_type = get_event_by_internal_name(plug_name) or UnknownDataEvent
            else:
                event_type = UnknownDataEvent

        events.append(event_type(id, value))

    return Project(*events, channel_count=channel_count, format=format, ppq=ppq)


def save(project: Project, file: str):
    """Save a parsed project back into a file.

    Args:
        project (Project): The object returned by `parse`.
        file (str): The file in which the contents of `project` are serialised back.
    """
    stream = BytesIOEx()
    stream.write(b"FLhd")  # 4
    stream.write_I(6)  # 8
    stream.write_h(project.format)  # 10
    stream.write_H(project.channel_count)  # 12
    stream.write_H(project.ppq)  # 14
    stream.write(b"FLdt")  # 18
    stream.seek(4, 1)  # leave space for total event size

    events_size = 0
    for event in project.events_astuple():
        events_size += len(event)
        stream.write(bytes(event))

    stream.seek(18)
    stream.write_I(events_size)

    with open(file, "wb") as flp:
        flp.write(stream.getvalue())
