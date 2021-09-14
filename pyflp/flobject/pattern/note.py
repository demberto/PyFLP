from typing import Optional

from pyflp.bytesioex import BytesIOEx

class Note:
    @property
    def position(self) -> Optional[int]:
        return getattr(self, '_position', None)
    
    @position.setter
    def position(self, value: int):
        self._data.seek(0)
        self._data.write_uint32(value)
        self._position = value
    
    @property
    def flags(self) -> Optional[int]:
        return getattr(self, '_flags', None)
    
    @flags.setter
    def flags(self, value: int):
        self._data.seek(4)
        self._data.write_uint16(value)
        self._flags = value
    
    @property
    def rack_channel(self) -> Optional[int]:
        return getattr(self, '_rack_channel', None)
    
    @rack_channel.setter
    def rack_channel(self, value: int):
        self._data.seek(6)
        self._data.write_uint16(value)
        self._rack_channel = value
    
    @property
    def duration(self) -> Optional[int]:
        return getattr(self, '_duration', None)
    
    @duration.setter
    def duration(self, value: int):
        self._data.seek(8)
        self._data.write_uint32(value)
        self._duration = value
    
    @property
    def key(self) -> Optional[int]:
        """0-131 for C0-B10. Yet 4-bytes, to save stamped chords/scales"""
        return getattr(self, '_key', None)
    
    @key.setter
    def key(self, value: int):
        self._data.seek(12)
        self._data.write_uint32(value)
        self._key = value
    
    @property
    def fine_pitch(self) -> Optional[int]:
        return getattr(self, '_fine_pitch', None)
    
    @fine_pitch.setter
    def fine_pitch(self, value: int):
        self._data.seek(16)
        self._data.write_int8(value)
        self._fine_pitch = value
    
    @property
    def release(self) -> Optional[int]:
        return getattr(self, '_release', None)
    
    @release.setter
    def release(self, value: int):
        self._data.seek(18)
        self._data.write_uint8(value)
        self._release = value
    
    @property
    def midi_channel(self) -> Optional[int]:
        return getattr(self, '_midi_channel', None)
    
    @midi_channel.setter
    def midi_channel(self, value: int):
        self._data.seek(19)
        self._data.write_uint8(value)
        self._midi_channel = value
    
    @property
    def pan(self) -> Optional[int]:
        return getattr(self, '_pan', None)
    
    @pan.setter
    def pan(self, value: int):
        self._data.seek(20)
        self._data.write_int8(value)
        self._pan = value
    
    @property
    def velocity(self) -> Optional[int]:
        return getattr(self, '_velocity', None)
    
    @velocity.setter
    def velocity(self, value: int):
        self._data.seek(21)
        self._data.write_uint8(value)
        self._velocity = value
    
    @property
    def mod_x(self) -> Optional[int]:
        return getattr(self, '_mod_x', None)
    
    @mod_x.setter
    def mod_x(self, value: int):
        self._data.seek(22)
        self._data.write_uint8(value)
        self._mod_x = value
    
    @property
    def mod_y(self) -> Optional[int]:
        return getattr(self, '_mod_y', None)
    
    @mod_y.setter
    def mod_y(self, value: int):
        self._data.seek(23)
        self._data.write_uint8(value)
        self._mod_y = value
    
    def parse(self, data: bytes) -> None:
        assert len(data) == 24
        self._data = BytesIOEx(data)
        self._position = self._data.read_uint32()       # 4
        self._flags = self._data.read_uint16()          # 6
        self._rack_channel = self._data.read_uint16()   # 8
        self._duration = self._data.read_uint32()       # 12
        self._key = self._data.read_uint32()            # 16
        self._fine_pitch = self._data.read_int8()       # 17
        self._u1 = self._data.read_int8()               # 18
        self._release = self._data.read_uint8()         # 19
        self._midi_channel = self._data.read_uint8()    # 20
        self._pan = self._data.read_int8()              # 21
        self._velocity = self._data.read_uint8()        # 22
        self._mod_x = self._data.read_uint8()           # 23
        self._mod_y = self._data.read_uint8()           # 24
        
    def save(self) -> bytes:
        self._data.seek(0)
        return self._data.read()