"""Parses insert params event. Occurs after all insert events."""

import enum
import logging
from typing import List

from pyflp.bytesioex import BytesIOEx
from pyflp.event import DataEvent
from pyflp.utils import DATA
from pyflp.flobject.insert.insert import Insert

logging.basicConfig()
log = logging.getLogger(__name__)

@enum.unique
class InsertParamEventID(enum.IntEnum):
    """Events inside event, nice design IL"""
    SlotEnabled = 0
    # SlotVolume = 1
    SlotMix = 1
    SendLevelStart = 64     # 64 - 191 are send level events
    Volume = 192
    Pan = 193
    StereoSeparation = 194
    LowLevel = 208
    BandLevel = 209
    HighLevel = 210
    LowFreq = 216
    BandFreq = 217
    HighFreq = 218
    LowQ = 224
    BandQ = 225
    HighQ = 226

class InsertParamsEvent(DataEvent):
    _verbose = False
    
    ID = DATA + 15 
    
    def __repr__(self) -> str:
        # No need to print data for this big ass event
        return f"InsertParamsEvent (Index: {self.index})"
    
    def __init__(self, data: bytes):
        log.setLevel(logging.DEBUG) if self._verbose else log.setLevel(logging.WARNING)
        log.debug("__init__() called")
        super().__init__(InsertParamsEvent.ID, data)
    
    def parse(self, inserts: List[Insert]) -> bool:
        """Returns `False` if validation fails"""
        if not len(self.data) % 12 == 0:
            log.error(f"Cannot parse InsertParamsEvent, skipping it. \
                        This should not happen, contact me!")
            return False
        data = BytesIOEx(self.data)
        
        while True:
            u1 = data.read_int32()              # 4
            if u1 is not None: break
            id = data.read_uint8()              # 5
            data.seek(1, 1)                     # 6
            channel_data = data.read_uint16()   # 8
            message_data = data.read_int32()    # 12
            
            slot_id = channel_data & 0x3F
            insert_id = (channel_data >> 6) & 0x7F
            insert_type = channel_data >> 13    # TODO
            insert = inserts[insert_id]
            
            log.debug(f"Insert param event, id: {id}")
            if id == InsertParamEventID.SlotEnabled:
                insert.slots[slot_id].enabled = True if message_data != 0 else False
            elif id == InsertParamEventID.SlotMix:
                insert.slots[slot_id].mix = message_data
            elif id == InsertParamEventID.Volume:
                insert.volume = message_data
            elif id == InsertParamEventID.Pan:
                insert.pan = message_data
            elif id == InsertParamEventID.StereoSeparation:
                insert.stereo_separation = message_data
            elif id == InsertParamEventID.LowLevel:
                insert.eq.low_level = message_data
            elif id == InsertParamEventID.BandLevel:
                insert.eq.band_level = message_data
            elif id == InsertParamEventID.HighLevel:
                insert.eq.high_level = message_data
            elif id == InsertParamEventID.LowFreq:
                insert.eq.low_freq = message_data
            elif id == InsertParamEventID.BandFreq:
                insert.eq.band_freq = message_data
            elif id == InsertParamEventID.HighFreq:
                insert.eq.high_freq = message_data
            elif id == InsertParamEventID.LowQ:
                insert.eq.low_q = message_data
            elif id == InsertParamEventID.BandQ:
                insert.eq.band_q = message_data
            elif id == InsertParamEventID.HighQ:
                insert.eq.high_q = message_data
            elif id in range(InsertParamEventID.SendLevelStart, Insert.max_count + 1):
                route_id = id - InsertParamEventID.SendLevelStart
                insert.route_volumes[route_id] = message_data
            else:
                log.info(f"New insert param event ID discovered: {id}, contact me!")
        return True