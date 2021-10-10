import abc
import enum
import logging
from typing import Union

from pyflp.utils import buflen_to_varint

__all__ = ["Event", "VariableSizedEvent"]


class Event(abc.ABC):
    """Abstract base class representing an event."""

    _count = 0

    @abc.abstractproperty
    def size(self) -> int:
        pass

    @property
    def index(self) -> int:
        return self.__index

    @abc.abstractmethod
    def dump(self, new_data):
        """Converts Python data types into equivalent C types and dumps them to `data`."""
        pass

    def to_raw(self) -> bytes:
        """Used by Project.save(). Overriden by `_VariabledSizedEvent`."""
        return int.to_bytes(self.id, 1, "little") + self.data

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        sid = str(self.id)
        iid = int(self.id)
        if isinstance(self.id, enum.IntEnum):
            return f"{cls} ID: {sid} ({iid})"
        return f"{cls} ID: <{iid}>"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Event):
            raise TypeError(f"Cannot compare equality between an 'Event' and {type(o)}")
        return self.id == o.id and self.data == o.data

    def __ne__(self, o: object) -> bool:
        if not isinstance(o, Event):
            raise TypeError(
                f"Cannot compare inequality between an 'Event' and {type(o)}"
            )
        return self.id != o.id or self.data != o.data

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        self.id = id
        self.data = data
        self.__index = Event._count
        Event._count += 1
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info(f"id: {id}, size: {self.size} count: {self.__class__._count}")
        super().__init__()


class VariableSizedEvent(Event):
    """Implements `Event.size` and `Event.to_raw()` for `TextEvent` and `DataEvent`."""

    @property
    def size(self) -> int:
        if self.data:
            return 1 + len(buflen_to_varint(self.data)) + len(self.data)
        return 2

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        sid = str(self.id)
        iid = int(self.id)
        if isinstance(self.id, enum.IntEnum):
            return f"{cls} ID: {sid} ({iid}), Size: {self.size}"
        return f"{cls} ID: {iid}, Size: {self.size}"

    def to_raw(self) -> bytes:
        id = int.to_bytes(self.id, 1, "little")
        length = buflen_to_varint(self.data) if self.data else b"\x00"
        data = self.data
        return id + length + data if self.data else id + length
