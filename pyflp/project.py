from dataclasses import dataclass, field
import io
import os
import logging
from pathlib import Path
import zipfile
from typing import List, Set, Union, ValuesView

from pyflp.event import Event
from pyflp.flobject import (
    Misc,
    Pattern,
    Channel,
    FilterChannel,
    Arrangement,
    Insert,
    FLObject,
)
from pyflp.bytesioex import BytesIOEx
from pyflp.flobject.insert.event import InsertParamsEvent

logging.basicConfig()
log = logging.getLogger(__name__)

__all__ = ["Project"]


@dataclass
class Project:
    _verbose: bool
    events: List[Event] = field(default_factory=list, init=False)
    save_path: Path = field(init=False)
    misc: Misc = field(default_factory=Misc, init=False)
    patterns: List[Pattern] = field(default_factory=list, init=False)
    filterchannels: List[FilterChannel] = field(default_factory=list, init=False)
    channels: List[Channel] = field(default_factory=list, init=False)
    arrangements: List[Arrangement] = field(default_factory=list, init=False)
    inserts: List[Insert] = field(default_factory=list, init=False)
    _unparsed_events: List[Event] = field(default_factory=list, init=False)

    def __post_init__(self):
        log.setLevel(logging.DEBUG if self._verbose else logging.WARNING)

    # * Utilities
    def used_insert_nums(self) -> Set[int]:
        """Returns a set of `Insert` indexes to which channels are routed."""
        ret = set()
        for channel in self.channels:
            i = channel.target_insert
            if i is not None:
                ret.add(i)
        return ret

    def create_zip(self, path: Union[str, Path] = ""):
        """Exports a ZIP looped package of an FLP.

        Args:
            path: The path to save the ZIP to. Defaults to ''.

        Raises:
            AttributeError: When path is default and Project was created from a stream
        """

        # Init
        if isinstance(path, str):
            if not path:
                if not hasattr(self, "save_path"):
                    raise AttributeError(
                        "Optional argument 'path' cannot be default \
                        to create a ZIP for a Project object created through a stram."
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
            # Add FLP to ZIP
            archive.write(str(path.name))

            # Find sampler and audio channels
            for channel in self.channels:
                sample_path = channel.sample_path

                # Check whether sample file exists
                if sample_path:

                    # Resolve locations of stock samples
                    if fl_dir.exists():
                        sample_path = sample_path.replace(
                            r"%FLStudioFactoryData%", str(fl_dir), 1
                        )
                    sp = Path(sample_path)
                    if not sp.exists():
                        log.error(
                            f"File doesn't exist {sample_path} or path string invalid"
                        )
                        continue

                    # Add samples to ZIP
                    parent = sp.parent.absolute()
                    os.chdir(str(parent))
                    archive.write(sp.name)
        os.chdir(cwd)

    # * Save logic
    def __save_state(self) -> List[Event]:
        """Calls `save()` for all `FLObject`s and returns a sorted list of the received events

        Returns:
            List[Event]: A list of events sorted by `Event.index`
        """

        log.debug("__save_state() called")

        event_store: List[Event] = []

        # Misc
        misc_events = list(self.misc.save())
        if misc_events:
            event_store.extend(misc_events)

        # Unparsed/unimplemented events
        if self._unparsed_events:
            event_store.extend(self._unparsed_events)

        for param in (
            "filterchannels",
            "channels",
            "patterns",
            "arrangements",
            "inserts",
        ):
            objs: List[FLObject] = getattr(self, param, None)
            if objs is None:
                log.error(f"self.{param} is empty or None")
                continue
            for obj in objs:
                obj_events: List[Event] = list(obj.save())
                if obj_events:  # ? Remove
                    event_store.extend(obj_events)

        # Insert params event
        for e in self.events:
            if e.id == InsertParamsEvent.ID:
                event_store.append(e)

        # ? Assign event store to self.events
        self.events = event_store

        # Sort the events in ascending order w.r.t index
        event_store.sort(key=lambda event: event.index)
        log.debug("Event store sorted")
        return event_store

    def get_stream(self) -> bytes:
        """Converts the list of events received from `self._save_state()`
        and headers into a single stream. Typically used directly when
        `Project` was parsed from a stream, i.e. save_path is not set.

        Returns:
            bytes: The stream. Used by `save()`.
        """

        log.debug("get_stream() called")

        # Save event state
        event_store = self.__save_state()
        log.debug("Event stored saved")

        # Begin the save process: Stream init
        stream = io.BytesIO()
        log.debug("Save stream initialised")

        # Header
        header = (
            b"FLhd"
            + int.to_bytes(6, 4, "little")
            + self.misc.format.to_bytes(2, "little", signed=True)
            + self.misc.channel_count.to_bytes(2, "little")
            + self.misc.ppq.to_bytes(2, "little")
        )
        stream.write(header)
        log.debug("Wrote header to stream")

        # Data chunk header
        data = BytesIOEx(b"FLdt")
        data.seek(4)

        # Calculate chunk length
        chunklen = 0
        for ev in event_store:
            chunklen += ev.size
        data.write_uint32(chunklen)
        log.debug(f"Save stream chunk length {chunklen}")

        # Dump events
        for ev in event_store:
            data.write(ev.to_raw())
        assert (data.tell() - 8) == chunklen
        log.debug("Dumped events to stream")

        # BytesIOEx -> bytes
        data.seek(0)
        stream.write(data.read())
        stream.seek(0)
        return stream.read()

    # TODO Implement saving for ZIP looped packages
    def save(self, save_path: Union[Path, str] = ""):
        """Saves `Project` to disk.

        Args:
            save_path (Union[Path, str], optional): File path to save to.

        Raises:
            AttributeError: When `Project.save_path` doesn't exist and `save_path` is not set.
            e: Exception which caused the write failed, most proably a permission/file-in-use error.
        """

        # ! raise NotImplementedError for FLPs from ZIPs

        log.debug("save() called")

        # Type checking and init
        if isinstance(save_path, str):
            save_path = Path(save_path)
        if not (hasattr(self, "save_path") or save_path == "."):
            raise AttributeError(
                "Optional argument 'path' cannot be default when \
                Project was parsed from a stream. Use get_stream() instead."
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
        except Exception as e:
            # Rollback
            save_path_bak.rename(save_path)
            log.exception(e)

        with open(save_path, "wb") as fp:
            try:
                fp.write(stream)
            except OSError as e:
                fp.close()
                save_path.unlink()
                if save_path == self.save_path:
                    save_path_bak.rename(self.save_path)
                raise e
