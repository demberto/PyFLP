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
"""

from __future__ import annotations

import io
import os
import logging
import sys
from typing import Any, BinaryIO

import construct as c

from pyflp._adapters import StdEnum
from pyflp._events import (
    DATA,
    DWORD,
    NEW_TEXT_IDS,
    TEXT,
    WORD,
    AnyEvent,
    AsciiEvent,
    EventEnum,
    EventTree,
    IndexedEvent,
    UnicodeEvent,
    UnknownEvent,
)
from pyflp.plugin import PluginID, get_event_by_internal_name
from pyflp.project import VALID_PPQS, FileFormat, Project, ProjectID
from pyflp.types import FLVersion

if sys.version_info < (3, 11):  # https://github.com/Bobronium/fastenum/issues/2
    import fastenum

    fastenum.enable()  # 33% faster parse()

__all__ = ["parse", "save"]

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())


FLP = c.Struct(
    hdr_magic=c.Const(b"FLhd"),
    hdr_size=c.Const(c.Int32ul.build(6)),
    format=StdEnum[FileFormat](c.Int16sl),
    n_channels=c.Int16ul,
    ppq=c.OneOf(c.Int16ul, VALID_PPQS),
    data_magic=c.Const(b"FLdt"),
    event_data=c.Prefixed(c.Int32ul, c.GreedyBytes),
    _=c.Terminated,
).compile()


def parse(file: Any) -> Project:
    """Parses an FL Studio file (projects, presets, scores).

    If you get an error from :module:`construct`, the
    header is corrupted or there are trailing bytes.

    Args:
        file: Path / stream / buffer to an FL Studio file.
    """
    if isinstance(file, BinaryIO):
        flp = FLP.parse_stream(file)
    elif os.path.isfile(file):
        flp = FLP.parse_file(file)
    else:
        flp = FLP.parse(file)

    stream = io.BytesIO(flp["event_data"])
    plug_name = None
    event_type: type[AnyEvent] | None = None
    str_type: type[AsciiEvent] | type[UnicodeEvent] | None = None
    events: list[AnyEvent] = []

    while stream.tell() < len(flp["event_data"]):
        event_type = None
        id = EventEnum(c.Int8ul.parse_stream(stream))

        if id < WORD:
            value = stream.read(1)
        elif id < DWORD:
            value = stream.read(2)
        elif id < TEXT:
            value = stream.read(4)
        else:
            size = c.VarInt.parse_stream(stream)
            value = stream.read(size)

        if id == ProjectID.FLVersion:
            string = value.decode("ascii").rstrip("\0")
            if FLVersion.from_str(string) >= FLVersion(11, 5):
                str_type = UnicodeEvent
            else:
                str_type = AsciiEvent

        for enum_ in EventEnum.__subclasses__():
            if id in enum_:
                event_type = getattr(enum_(id), "type")
                break

        if event_type is None:
            if id in range(TEXT, DATA) or id.value in NEW_TEXT_IDS:
                if str_type is None:  # pragma: no cover
                    raise TypeError("Failed to determine string encoding")
                event_type = str_type

                if id == PluginID.InternalName:
                    plug_name = event_type(id, value).value
            elif id == PluginID.Data and plug_name is not None:
                event_type = get_event_by_internal_name(plug_name)
            else:
                event_type = UnknownEvent

        try:
            event = event_type(id, value)
        except c.ConstructError as exc:
            logger.exception(exc)
            logger.error(f"Failed to parse {id!r} event. Report this issue.")
            event = UnknownEvent(id, value, failed=True)
        events.append(event)

    return Project(
        EventTree(init=(IndexedEvent(r, e) for r, e in enumerate(events))),
        channel_count=flp["n_channels"],
        format=flp["format"],
        ppq=flp["ppq"],
    )


def save(project: Project, file: str | os.PathLike[Any] | BinaryIO) -> None:
    """Save a :class:`Project` back into a file or stream.

    Caution:
        Always have a backup ready, just in case 😉
    """
    fields: dict[str, Any] = {"ppq": project.ppq, "format": project.format}

    try:
        fields["n_channels"] = len(project.channels)
    except Exception as exc:
        logger.exception(exc)
        logger.error("Failed to calculate number of channels")
        fields["n_channels"] = project.channel_count

    fields["event_data"] = b"".join(bytes(event) for event in project.events)

    if isinstance(file, BinaryIO):
        FLP.build_stream(fields, file)
    else:
        FLP.build_file(fields, file)
