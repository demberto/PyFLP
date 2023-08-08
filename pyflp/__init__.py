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

import logging
import os
import sys
from typing import Any, BinaryIO

import construct as c

from pyflp._adapters import StdEnum, AsciiAdapter, UnicodeAdapter, SimpleAdapter
from pyflp._events import DATA, DWORD, NEW_TEXT_IDS, TEXT, WORD, AnyEvent, Event, EventEnum
from pyflp.plugin import INTERNAL_NAMES, PluginID
from pyflp.project import VALID_PPQS, FileFormat, FLVersion, Project, ProjectID

if sys.version_info < (3, 11):  # https://github.com/Bobronium/fastenum/issues/2
    import fastenum

    fastenum.enable()  # 33% faster parse()

__all__ = ["parse", "save"]

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())


FLP = c.Struct(
    header=c.Struct(
        magic=c.Const(b"FLhd"),
        size=c.Const(c.Int32ul.build(6)),
        format=StdEnum(FileFormat, c.Int16sl),
        n_channels=c.Int16ul,
        ppq=c.OneOf(c.Int16ul, VALID_PPQS),
    ),
    data=c.Struct(
        magic=c.Const(b"FLdt"),
        events=c.Prefixed(
            c.Int32ul,
            c.GreedyRange(
                c.Struct(
                    id=StdEnum(EventEnum, c.Int8ul),
                    data=c.IfThenElse(
                        c.this.id >= TEXT,
                        c.Prefixed(c.VarInt, c.GreedyBytes),
                        c.IfThenElse(
                            c.this.id >= DWORD,
                            c.Bytes(4),
                            c.IfThenElse(c.this.id >= WORD, c.Bytes(2), c.Bytes(1)),
                        ),
                    ),
                )
            ),
        ),
    ),
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

    plug_name = None
    struct: c.Construct[Any, Any] | None = None
    str_adapter: SimpleAdapter[str, str] | None = None
    events: list[AnyEvent] = []

    for event in flp["data"]["events"]:
        struct = None
        id: EventEnum = event["id"]
        data: bytes = event["data"]

        if id == ProjectID.FLVersion:
            string = data.decode("ascii").rstrip("\0")
            if FLVersion.from_str(string) >= FLVersion(11, 5):
                str_adapter = UnicodeAdapter
            else:
                str_adapter = AsciiAdapter

        for enum_ in EventEnum.__subclasses__():
            if id in enum_:
                struct = enum_(id)._struct_  # type: ignore
                break

        if struct is None:
            if id in range(TEXT, DATA) or id.value in NEW_TEXT_IDS:
                if str_adapter is None:  # pragma: no cover
                    raise TypeError("Failed to determine string encoding")
                struct = str_adapter

                if id == PluginID.InternalName:
                    plug_name = Event[str](id, data, struct).value
            elif id == PluginID.Data and plug_name is not None:
                struct = INTERNAL_NAMES.get(plug_name, c.GreedyBytes)
        else:
            struct = c.GreedyBytes

        try:
            event = Event(id, data, struct)
        except c.ConstructError as exc:
            logger.exception(exc)
            logger.error(f"Failed to parse {id!r} event. Report this issue.")
            event = Event(id, data, c.GreedyBytes)
        events.append(event)

    return Project(
        events=events, channel_count=flp["n_channels"], format=flp["format"], ppq=flp["ppq"]
    )


def save(project: Project, file: str | os.PathLike[str] | BinaryIO) -> None:
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
