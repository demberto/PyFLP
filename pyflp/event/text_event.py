import enum
from typing import Union

from pyflp.event.event import VariableSizedEvent
from pyflp.utils import TEXT, DATA, DATA_TEXT_EVENTS

__all__ = ['TextEvent']

class TextEvent(VariableSizedEvent):
    """Represents a variable sized event used for storing strings.

	Raises:
		TypeError
	"""

    # ProjectParser will change this.
    uses_unicode = True

    def __repr__(self) -> str:
        return f"TextEvent ID: {self.id} Data: {self.to_str()} (Index: {self.index})"

    def dump(self, new_str: str):
        if not isinstance(new_str, str):
            raise TypeError(f"Expected an str object; got {type(new_str)}")
        # Version event (199) is always ASCII
        if TextEvent.uses_unicode and self.id != 199:
            self.data = new_str.encode('utf-16', errors='ignore') + b'\0\0'
        else:
            self.data = new_str.encode('ascii', errors='ignore') + b'\0'

    def to_str(self) -> str:
        if TextEvent.uses_unicode and self.id != 199:
            return self.data.decode('utf-16', errors='ignore').strip('\0')
        return self.data.decode('ascii', errors='ignore').strip('\0')

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id not in range(TEXT, DATA) and id not in DATA_TEXT_EVENTS:
            raise ValueError(f"Unexpected ID: {id}")
        super().__init__(id, data)