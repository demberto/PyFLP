import dataclasses
import enum
from typing import List, Optional, ValuesView

from pyflp.event import Event
from pyflp.flobject.plugin.plugin import Plugin
from pyflp.event import DataEvent
from pyflp.utils import DATA
from pyflp.bytesioex import BytesIOEx

@enum.unique
class PluginChunkEventID(enum.IntEnum):
    """An event inside event, again. Roughly in this order"""
    MIDI = 1
    Flags = 2
    IO = 30
    InputInfo = 31
    OutputInfo = 32
    PluginInfo = 50
    VSTFourCC = 51      # Not present for Waveshells
    GUID = 52           # Exclusive to Waveshells, as I suspected
    _57 = 57            # TODO, not present for Waveshells
    Name = 54
    PluginPath = 55
    Vendor = 56
    State = 53

@dataclasses.dataclass(init=False)
class PluginIOInfo:
    mixer_offset: int
    flags: int

class VSTPlugin(Plugin):
    """Parses a VST2/3 plugin (including Waveshells) data 
    (ChannelEventID.PluginData & InsertSlotEventID.PluginData event)"""
    
    ID = DATA + 5
    
    @property
    def midi_in_port(self) -> Optional[int]:
        return getattr(self, '_midi_in_port', None)
    
    @midi_in_port.setter
    def midi_in_port(self, value: int):
        pass
    
    @property
    def midi_out_port(self) -> Optional[int]:
        return getattr(self, '_midi_out_port', None)
    
    @midi_out_port.setter
    def midi_out_port(self, value: int):
        pass
    
    @property
    def pitch_bend_range(self) -> Optional[int]:
        return getattr(self, '_pitch_bend_range', None)
    
    @pitch_bend_range.setter
    def pitch_bend_range(self, value: int):
        pass

    @property
    def flags(self) -> Optional[int]:
        return getattr(self, '_flags', None)
    
    @flags.setter
    def flags(self, value: int):
        pass

    @property
    def num_inputs(self) -> Optional[int]:
        return getattr(self, '_num_inputs', None)
    
    @num_inputs.setter
    def num_inputs(self, value: int):
        pass
    
    @property
    def num_outputs(self) -> Optional[int]:
        return getattr(self, '_num_outputs', None)
    
    @num_outputs.setter
    def num_outputs(self, value: int):
        pass

    @property
    def input_info(self) -> List[PluginIOInfo]:
        return getattr(self, '_input_info', [])
    
    @input_info.setter
    def input_info(self, value: List[PluginIOInfo]):
        pass
    
    @property
    def output_info(self) -> List[PluginIOInfo]:
        return getattr(self, '_output_info', [])
    
    @output_info.setter
    def output_info(self, value: List[PluginIOInfo]):
        pass

    @property
    def vst_number(self) -> Optional[int]:
        return getattr(self, '_vst_number', None)
    
    @vst_number.setter
    def vst_number(self, value: int):
        pass
    
    @property
    def vst_fourcc(self) -> Optional[str]:
        """FourCC unique VST ID, as reserved by plugin dev"""
        return getattr(self, '_vst_fourcc', None)
    
    @vst_fourcc.setter
    def vst_fourcc(self, value: str):
        assert len(value) == 4 and value.isascii()

    @property
    def guid(self) -> Optional[bytes]:
        """Used by Waveshells to identify the correct plugin"""
        return getattr(self, '_guid', None)
    
    @guid.setter
    def guid(self, value: bytes):
        pass

    @property
    def data(self) -> Optional[bytes]:
        """The actual plugin data"""
        return getattr(self, '_data', None)
    
    @data.setter
    def data(self, value: bytes):
        pass

    @property
    def name(self) -> Optional[str]:
        """User set name for native plugins, real/user-set name for VSTs"""
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        assert value.isascii()

    @property
    def plugin_path(self) -> Optional[str]:
        """The absolute path to the plugin .dll on the artists' device.
        I really don't understand why this is required, FL already creates .fst
        when it discovers a plugin. Also VST plugins do have a unique FourCC."""
        return getattr(self, '_plugin_path', None)
    
    @plugin_path.setter
    def plugin_path(self, value: str):
        pass    # TODO: What about non-ASCII paths?

    @property
    def vendor(self) -> Optional[str]:
        """Plugin developer name"""
        return getattr(self, '_vendor', None)
    
    @vendor.setter
    def vendor(self, value: str):
        assert value.isascii()
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._plugin_data.seek(0)
        self._events['plugin'].dump(self._plugin_data.read())
        return super().save()

    def _parse_data_event(self, event: DataEvent) -> None:
        if event.id == VSTPlugin.ID:
            self._events['plugin'] = event
            self._plugin_data = BytesIOEx(event.data)
            self._kind = self._plugin_data.read_int32()
            if not self._kind == 10:
                # Not a VST plugin
                return
            
            # Here we go again
            while True:
                event_id = self._plugin_data.read_int32()
                if not event_id:
                    break
                length = self._plugin_data.read_uint64()
                data = self._plugin_data.read(length)
                
                if event_id == PluginChunkEventID.Vendor:
                    self._vendor = data.decode('ascii')
                elif event_id == PluginChunkEventID.PluginPath:
                    self._plugin_path = data.decode('ascii')
                elif event_id == PluginChunkEventID.Name:
                    self._name = data.decode('ascii')
                elif event_id == PluginChunkEventID.VSTFourCC:
                    self._vst_fourcc = data.decode('ascii')
                elif event_id == PluginChunkEventID.State:
                    self._data = data
                else:
                    self._log.info(f"Unparsed plugin chunk event ID {event_id} found")