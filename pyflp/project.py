import dataclasses
import io
import os
import logging
import pathlib
import zipfile
from typing import List, Set, Union

from pyflp.event import Event
from pyflp.flobject import (
    Misc,
    Pattern,
    Channel,
    FilterChannel,
    Arrangement,
    Insert,
    FLObject
)
from pyflp.flobject.channel.channel import ChannelKind
from pyflp.bytesioex import BytesIOEx

logging.basicConfig()
log = logging.getLogger(__name__)

@dataclasses.dataclass
class Project:
    _verbose: bool

    save_path: pathlib.Path = dataclasses.field(init=False)
    misc: Misc = dataclasses.field(default_factory=Misc, init=False)
    patterns: List[Pattern] = dataclasses.field(default_factory=list, init=False)
    filterchannels: List[FilterChannel] = dataclasses.field(default_factory=list, init=False)
    channels: List[Channel] = dataclasses.field(default_factory=list, init=False)
    arrangements: List[Arrangement] = dataclasses.field(default_factory=list, init=False)
    inserts: List[Insert] = dataclasses.field(default_factory=list, init=False)
    _unparsed_events: List[Event] = dataclasses.field(default_factory=list, init=False)

    def __post_init__(self):
        log.setLevel(logging.DEBUG if self._verbose else logging.WARNING)

    #region Utilities
    def used_insert_nums(self) -> Set[int]:
        """Returns a `Set` of used `Insert` indexes."""
        ret = set()
        for channel in self.channels:
            ret.add(channel.target_insert)

    def create_zip(self, path: Union[str, pathlib.Path] = ''):
        """Equivalent to a "ZIP looped package" in FL Studio.

        Args:
            path (Union[str, pathlib.Path], optional): The path to save the ZIP to. Defaults to ''.

        Raises:
            AttributeError: When path is default and Project was created from a stream
        """

        # Init
        if isinstance(path, str):
            if not path:
                if not hasattr(self, 'save_path'):
                    raise AttributeError("Optional argument 'path' cannot be default \
                        to create a ZIP for a Project object created through a stram.")
                path = pathlib.Path(self.save_path)
            path = pathlib.Path(path)
        path.suffix = '.zip'
        path = os.fspath(path)

        with zipfile.ZipFile(path, 'x') as archive:
            # Add FLP to ZIP
            archive.write(os.fspath(self.save_path))

            # Find sampler and audio channels
            for channel in self.channels:
                if channel.kind in (ChannelKind.Sampler, ChannelKind.Audio):
                    sample_path = getattr(channel, 'sample_path')

                    # Check whether sample file exists
                    if not os.path.exists(sample_path):
                        log.error(f"File doesn't exist {sample_path} or path string invalid")
                        continue

                    # Add samples to ZIP
                    archive.write(os.fspath(sample_path))
    #endregion

    #region Save logic
    def _save_state(self) -> List[Event]:
        """Calls `save()` for all `FLObject`s and returns a sorted list of the received events

        Returns:
            List[Event]: [description]
        """

        event_store: List[Event] = []

        # Misc
        misc_events = self.misc.save()
        if misc_events:
            event_store.extend(misc_events)

        # Unparsed/unimplemented events
        if self._unparsed_events:
            event_store.extend(self._unparsed_events)

        for param in ('filterchannels', 'channels', 'patterns', 'arrangements', 'inserts'):
            objs: List[FLObject] = getattr(self, param, None)
            if objs is None:
                log.error(f"self.{param} is empty or None")
                continue
            for obj in objs:
                obj_events: List[Event] = list(obj.save())
                if obj_events:
                    event_store.extend(obj_events)

        # Sort the events in ascending order w.r.t index
        event_store.sort(key=lambda event: event.index)

        return event_store

    def get_stream(self) -> bytes:
        """Converts the list of events received from `self._save_state()` and headers into a single stream.
        Typically used directly when Project was parsed from a stream, i.e. save_path is not set.

        Returns:
            bytes: The stream. Used by `save()`
        """

        # Save event state
        event_store = self._save_state()

        # Begin the save process: Stream init
        stream = io.BytesIO()

        # Header
        header = b'FLhd' \
            + int.to_bytes(6, 4, 'little') \
            + self.misc.format.to_bytes(2, 'little', signed=True) \
            + self.misc.channel_count.to_bytes(2, 'little') \
            + self.misc.ppq.to_bytes(2, 'little')
        stream.write(header)

        # Data chunk header
        data = BytesIOEx(b'FLdt')
        data.seek(4)

        # Calculate chunk length
        chunklen = 0
        for ev in event_store:
            chunklen += ev.size
        data.write_uint32(chunklen)

        # Dump events
        for ev in event_store:
            data.write(ev.to_raw())
        assert (data.tell() - 8) == chunklen

        # BytesIOEx to bytes
        data.seek(0)
        stream.write(data.read())
        stream.seek(0)
        return stream.read()

    def save(self, save_path: Union[pathlib.Path, str] = ''):
        """Save `Project` to the disk.

        Args:
            save_path (Union[pathlib.Path, str], optional): File path to save to. Defaults to ''.

        Raises:
            AttributeError: When Project.save_path doesn't exist and save_path is not set
            e: Exception which caused the write failed, most proably a permission/file-in-use error.
        """

        # Type checking and init
        if isinstance(save_path, str):
            save_path = pathlib.Path(save_path)
        if not (hasattr(self, 'save_path') or save_path == '.'):
            raise AttributeError("Optional argument 'path' cannot be default when \
                Project was parsed from a stream. Use get_stream() instead.")
        if hasattr(self, 'save_path'):
            if save_path == pathlib.Path('.'):
                save_path = self.save_path
                suffix = save_path.suffix if save_path.suffix else ''
                save_path_bak = save_path.with_suffix(f'{suffix}.bak')
                if save_path_bak.exists():
                    save_path_bak.unlink()
                save_path.rename(save_path_bak)

        stream = self.get_stream()
        with open(save_path, 'wb') as fp:
            try:
                fp.write(stream)
            except OSError as e:
                fp.close()
                save_path.unlink()
                if save_path == self.save_path:
                    save_path_bak.rename(self.save_path)
                raise e
    #endregion