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

import io
import os
import platform
import warnings
import zipfile
from pathlib import Path
from typing import List, Optional, Set, Union

from bytesioex import BytesIOEx

from pyflp._event import EventType
from pyflp.arrangement.arrangement import Arrangement
from pyflp.channel.channel import Channel
from pyflp.channel.filter import Filter
from pyflp.controllers import Controller
from pyflp.exceptions import DataCorruptionDetectedError
from pyflp.insert.event import InsertParamsEvent
from pyflp.insert.insert import Insert
from pyflp.misc import Misc
from pyflp.pattern.pattern import Pattern

__all__ = ["Project"]


class Project:
    __slots__ = (
        "events",
        "save_path",
        "misc",
        "patterns",
        "filters",
        "channels",
        "arrangements",
        "inserts",
        "controllers",
        "_unparsed_events",
    )

    def __init__(self) -> None:
        self.events: List[EventType] = []
        self.save_path: Optional[Path] = None
        self.misc = Misc()
        self.patterns: List[Pattern] = []
        self.filters: List[Filter] = []
        self.channels: List[Channel] = []
        self.arrangements: List[Arrangement] = []
        self.inserts: List[Insert] = []
        self.controllers: List[Controller] = []
        self._unparsed_events: List[EventType] = []

    def __repr__(self) -> str:
        return "<Project {}, {}, {}, {}, {}, {}, {}>".format(
            f'version="{self.misc.version}"',
            f"{len(self.channels)} channels",
            f"{len(self.patterns)} patterns",
            f"{len(self.used_insert_nums())} inserts used",
            f"{self.slots_used()} insert slots occupied",
            f"{len(self.controllers)} controllers",
            f"{len(self.events)} events ({len(self._unparsed_events)} unparsed)",
        )

    # * Utilities
    def used_insert_nums(self) -> Set[int]:
        """Returns a set of `Insert` indexes to which channels are routed."""
        ret = set()
        for channel in self.channels:
            i = channel.target_insert
            if i is not None:
                ret.add(i)
        return ret

    def slots_used(self) -> int:
        """Returns the total number of slots used across all inserts."""
        ret = int()
        for insert in self.inserts:
            for slot in insert.slots:
                if slot.is_used():
                    ret += 1
        return ret

    def create_zip(self, path: Union[str, Path] = "") -> None:
        """Exports a ZIP looped package of an FLP.
        Importing stock sample Works only on Windows

        Args:
            path: The path to save the ZIP to.

        Raises:
            AttributeError: When path is default and Project was created from a stream
        """

        # Init
        if isinstance(path, str):
            if not path:
                if not hasattr(self, "save_path"):
                    raise AttributeError(
                        "Optional argument 'path' cannot be default to create "
                        "a ZIP for a Project object created through a stream."
                    )
                path = Path(self.save_path)
            path = Path(path)
        p = os.fspath(path.with_suffix(".zip"))

        # Get FL Studio install dir for copying stock samples
        il = Path(os.environ["PROGRAMFILES"]) / "Image-Line"
        asio = il / "FL Studio ASIO"
        shared = il / "Shared"
        fl_dir = Path()
        for dir in il.iterdir():
            if dir in (asio, shared):
                continue
            else:
                fl_dir = dir
                break

        cwd = os.getcwd()
        os.chdir(str(path.parent))
        with zipfile.ZipFile(p, "x") as archive:
            system = platform.system()

            # Add FLP to ZIP
            archive.write(str(path.name))

            # Find sampler and audio channels
            for channel in self.channels:
                sample_path = channel.sample_path

                # Check whether sample file exists
                if sample_path:

                    # Check existence of stock samples and Windows
                    if (
                        sample_path.find(r"%FLStudioFactoryData") != -1
                        and system != "Windows"
                    ):
                        warnings.warn(
                            f"Cannot import stock samples from {system}. "
                            "Only Windows is supported currently.",
                            RuntimeWarning,
                        )

                    # Resolve locations of stock samples
                    if fl_dir.exists():
                        sample_path = sample_path.replace(
                            r"%FLStudioFactoryData%", str(fl_dir), 1
                        )
                    else:
                        warnings.warn(
                            "Importing stock samples requires FL Studio "
                            f"installed at {str(fl_dir)}. Skipping sample"
                        )
                    sp = Path(sample_path)
                    if not sp.exists():
                        warnings.warn(f"File {sample_path} doesn't exist")
                        continue

                    # Add samples to ZIP
                    parent = sp.parent.absolute()
                    os.chdir(str(parent))
                    archive.write(sp.name)
        os.chdir(cwd)

    # * Save logic
    def __save_state(self) -> List[EventType]:
        """Calls `_save` for all `_FLObject`s and returns a sorted list of the received events

        Returns:
            List[Event]: A list of events sorted by `Event.index`
        """
        from pyflp._flobject import _FLObject

        event_store: List[EventType] = []

        # Misc
        misc_events = list(self.misc._save())
        if misc_events:
            event_store.extend(misc_events)

        # Unparsed/unimplemented events
        if self._unparsed_events:
            event_store.extend(self._unparsed_events)

        for param in (
            "filters",
            "channels",
            "patterns",
            "arrangements",
            "inserts",
            "controllers",
        ):
            objs: List[_FLObject] = getattr(self, param)
            for obj in objs:
                event_store.extend(obj._save())

        # Insert params event
        for e in self.events:
            if e.id_ == InsertParamsEvent.ID:
                event_store.append(e)

        # ? Assign event store to self.events
        self.events = event_store

        # Sort the events in ascending order w.r.t index
        event_store.sort(key=lambda event: event.index)
        return event_store

    def get_stream(self) -> bytes:
        """Converts the list of events received from `self._save_state()`
        and headers into a single stream. Typically used directly when
        `Project` was parsed from a stream, i.e. `save_path` is not set.

        Returns:
            bytes: The stream. Used by `save()`.
        """

        # Save event state
        event_store = self.__save_state()

        # Begin the save process: Stream init
        stream = io.BytesIO()

        # Header
        header = (
            b"FLhd"
            + int.to_bytes(6, 4, "little")
            + self.misc.format.to_bytes(2, "little", signed=True)
            + self.misc.channel_count.to_bytes(2, "little")
            + self.misc.ppq.to_bytes(2, "little")
        )
        stream.write(header)

        # Data chunk header
        data = BytesIOEx(b"FLdt")
        data.seek(4)

        # Calculate chunk length
        chunklen = 0
        for ev in event_store:
            chunklen += ev.size
        data.write_I(chunklen)

        # Dump events
        for ev in event_store:
            data.write(ev.to_raw())
        if (data.tell() - 8) != chunklen:
            raise DataCorruptionDetectedError

        # BytesIOEx -> bytes
        data.seek(0)
        stream.write(data.read())
        stream.seek(0)
        return stream.read()

    # TODO Implement saving for ZIP looped packages
    def save(self, save_path: Union[Path, str] = "") -> None:
        """Saves `Project` to disk.

        Args:
            save_path (Union[Path, str], optional): File path to save to.

        Raises:
            AttributeError: When `Project.save_path` \
            doesn't exist and `save_path` is not set.
            OSError: Exception which caused the write failed, \
            most proably a permission/file-in-use error.
        """

        # Type checking and init
        if isinstance(save_path, str):
            save_path = Path(save_path)
        if not (hasattr(self, "save_path") or save_path == "."):
            raise AttributeError(
                "Optional argument 'path' cannot be default when Parser "
                "was initialised from a stream. Use get_stream() instead."
            )
        if hasattr(self, "save_path"):
            if save_path == Path("."):
                save_path = self.save_path
                suffix = save_path.suffix if save_path.suffix else ""
                save_path_bak = save_path.with_suffix(f"{suffix}.bak")
                if save_path_bak.exists():
                    save_path_bak.unlink()
                save_path.rename(save_path_bak)
        try:
            stream = self.get_stream()
        except Exception:
            # Rollback
            save_path_bak.rename(save_path)

        with open(save_path, "wb") as fp:
            try:
                fp.write(stream)
            except OSError as e:
                fp.close()
                save_path.unlink()
                if save_path == self.save_path:
                    save_path_bak.rename(self.save_path)
                raise e
