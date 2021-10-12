import dataclasses
import enum
from typing import List, Optional

from pyflp.flobject.plugin.plugin import Plugin
from pyflp.event import DataEvent
from pyflp.utils import isascii

from bytesioex import BytesIOEx  # type: ignore

PLUGIN_VST = 8, 10


@enum.unique
class PluginChunkEvent(enum.IntEnum):
    """An event inside event, again. Roughly in this order."""

    MIDI = 1
    Flags = 2
    IO = 30
    InputInfo = 31
    OutputInfo = 32
    PluginInfo = 50
    VSTFourCC = 51  # Not present for Waveshells
    GUID = 52  # Exclusive to Waveshells, as I suspected
    _57 = 57  # TODO, not present for Waveshells
    Name = 54
    PluginPath = 55
    Vendor = 56
    State = 53


@dataclasses.dataclass(init=False)
class PluginIOInfo:
    mixer_offset: int
    flags: int


class VSTPlugin(Plugin):
    """VST2/3 (including Waveshells, *maybe AU as well*) plugin data
    (`ChannelEventID.Plugin` & `InsertSlotEventID.Plugin` event).

    [FL Studio Manual Page](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/wrapper.htm#wrapper_pluginsettings)
    """

    # * Properties
    @property
    def midi_in_port(self) -> Optional[int]:
        """MIDI Input Port. Possible values: 0-255. Default: TODO."""
        return getattr(self, "_midi_in_port", None)

    @midi_in_port.setter
    def midi_in_port(self, value: int):
        pass

    @property
    def midi_out_port(self) -> Optional[int]:
        """MIDI Output Port. Possible values: 0-255. Default: TODO."""
        return getattr(self, "_midi_out_port", None)

    @midi_out_port.setter
    def midi_out_port(self, value: int):
        pass

    @property
    def pitch_bend_range(self) -> Optional[int]:
        """VST Wrapper settings -> MIDI -> Send pitch bend range (semitones)."""
        return getattr(self, "_pitch_bend_range", None)

    @pitch_bend_range.setter
    def pitch_bend_range(self, value: int):
        pass

    @property
    def flags(self) -> Optional[int]:
        """VST Wrapper settings, boolean values TODO"""
        return getattr(self, "_flags", None)

    @flags.setter
    def flags(self, value: int):
        pass

    @property
    def num_inputs(self) -> Optional[int]:
        """Number of inputs to a plugin. Depend on the plugin.
        VST Wrapper settings -> Processing -> Connections."""
        return getattr(self, "_num_inputs", None)

    @num_inputs.setter
    def num_inputs(self, value: int):
        pass

    @property
    def num_outputs(self) -> Optional[int]:
        """Number of outputs of a plugin. Depend on the plugin.
        VST Wrapper settings -> Processing -> Connections."""
        return getattr(self, "_num_outputs", None)

    @num_outputs.setter
    def num_outputs(self, value: int):
        pass

    @property
    def input_info(self) -> List[PluginIOInfo]:
        """Input information."""
        return getattr(self, "_input_info", [])

    @input_info.setter
    def input_info(self, value: List[PluginIOInfo]):
        pass

    @property
    def output_info(self) -> List[PluginIOInfo]:
        """Ouput information."""
        return getattr(self, "_output_info", [])

    @output_info.setter
    def output_info(self, value: List[PluginIOInfo]):
        pass

    @property
    def vst_number(self) -> Optional[int]:
        """TODO. Maybe related to Waveshells."""
        return getattr(self, "_vst_number", None)

    @vst_number.setter
    def vst_number(self, value: int):
        pass

    @property
    def fourcc(self) -> Optional[str]:
        """FourCC unique VST ID, as reserved by plugin dev on Steinberg portal."""
        return getattr(self, "_vst_fourcc", None)

    @fourcc.setter
    def fourcc(self, value: str):
        assert len(value) == 4 and isascii(value)

    @property
    def guid(self) -> Optional[bytes]:
        """Waveshell unique plugin ID."""
        return getattr(self, "_guid", None)

    @guid.setter
    def guid(self, value: bytes):
        pass

    @property
    def state(self) -> Optional[bytes]:
        """The actual plugin data. Plugin specific. Can be a list of floats,
        but devs generally use their own format. This is the only data
        present in stock plugin events."""
        return getattr(self, "_state", None)

    @state.setter
    def state(self, value: bytes):
        pass

    @property
    def name(self) -> Optional[str]:
        """User set name for native plugins, factory/user-set name for VSTs."""
        return getattr(self, "_name", None)

    @name.setter
    def name(self, value: str):
        assert isascii(value)

    @property
    def plugin_path(self) -> Optional[str]:
        """The absolute path to the plugin .dll on the disk in ASCII.
        Idk why this is required, FL already creates .fst
        when it discovers a plugin. Maybe only useful for Waveshells."""
        return getattr(self, "_plugin_path", None)

    @plugin_path.setter
    def plugin_path(self, value: str):
        pass  # TODO: What about non-ASCII paths?

    @property
    def vendor(self) -> Optional[str]:
        """Plugin developer name stored in ASCII."""
        return getattr(self, "_vendor", None)

    @vendor.setter
    def vendor(self, value: str):
        assert isascii(value)

    def _parse_data_event(self, event: DataEvent) -> None:
        self._events["data"] = event
        self._data = BytesIOEx(event.data)
        self._kind = self._data.read_i()
        if not self._kind in PLUGIN_VST:
            return

        while True:
            event_id = self._data.read_i()
            if not event_id:
                break
            length = self._data.read_I()
            data = self._data.read(length)

            if event_id == PluginChunkEvent.Vendor:
                self._vendor = data.decode("ascii")
            elif event_id == PluginChunkEvent.PluginPath:
                self._plugin_path = data.decode("ascii")
            elif event_id == PluginChunkEvent.Name:
                self._name = data.decode("ascii")
            elif event_id == PluginChunkEvent.VSTFourCC:
                self._fourcc = data.decode("ascii")
            elif event_id == PluginChunkEvent.State:
                self._state = data
            else:
                self._log.info(f"Unparsed plugin chunk event ID {event_id} found")

    def __init__(self):
        super().__init__()
