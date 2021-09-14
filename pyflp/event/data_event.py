import enum
from typing import Union

from pyflp.event.event import VariableSizedEvent
from pyflp.utils import DATA

class DataEvent(VariableSizedEvent):
    """Represents a variable sized event used for storing a blob of data,
    consists of a collection of POD types like int, bool, float, sometimes ASCII strings.
    Its size is determined by the event and also FL version sometimes.
    The task of parsing is completely handled by one of the FLObject subclasses,
    hence no `to_*` conversion method is provided.
 
	Raises:
		TypeError & ValueError
	"""
    
    def __repr__(self) -> str:
        return f"DataEvent ID: {self.id} Data: {self.data} (Index: {self.index})"
    
    def dump(self, new_bytes: bytes):
        """Use this method over directly setting self.data for type-safety."""
        if not isinstance(new_bytes, bytes):
            raise TypeError(f"Expected a bytes object; got a {type(new_bytes)} object")
        self.data = new_bytes

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if id < DATA:
            raise ValueError(f"Expected an event ID from 209 to 255; got {id}")
        super().__init__(id, data)
