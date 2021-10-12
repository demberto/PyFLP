import logging
from typing import TypeVar

logging.basicConfig()

from .event import Event
from .byte import *
from .word import *
from .dword import *
from .text import *
from .data import *

EventType = TypeVar("EventType", bound=Event)
