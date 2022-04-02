import dataclasses
import enum
from typing import Any, List, Optional, Union, ValuesView

from bytesioex import BytesIOEx, UInt, ULong

from pyflp._event import _DataEvent, _VariableSizedEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _BytesProperty, _IntProperty, _StrProperty, _UIntProperty
from pyflp._validators import _StrValidator, _UIntValidator
from pyflp.plugin._plugin import _Plugin


class _QWordVariableEvent(_VariableSizedEvent):
    @property
    def size(self) -> int:
        if self.data:
            return 9 + len(self.data)
        return 9

    def dump(self, new_data: Union[str, bytes]):
        if not isinstance(new_data, (bytes, str)):
            raise TypeError("Expected a bytes or an str object")
        if isinstance(new_data, str):
            self.data = new_data.encode("ascii")
        else:
            self.data = new_data

    def to_raw(self) -> bytes:
        id = UInt.pack(self.id)
        data = self.data

        # IL chose to use 8 byte integers for a VST plugin parameters
        # sub-event when the entire data chunk size is stored in 4 😂
        length = ULong.pack(len(data))

        return id + length + data if data else id + length

    def __init__(self, id: "_VSTPluginParser.EventID", data: bytes):
        super().__init__(id, data)


class _VSTPluginParser(_FLObject):
    @enum.unique
    class EventID(enum.IntEnum):
        """An event inside event, again. Roughly in this order."""

        # Purposely named like this; don't like it, but this
        # is the easiest solution for _VSTPluginEvent.dump()
        midi = 1
        flags = 2
        io = 30
        input_infos = 31
        output_infos = 32
        plugin_infos = 50
        fourcc = 51  # Not present for Waveshells
        guid = 52  # Exclusive to Waveshells, as I suspected
        _57 = 57  # TODO, not present for Waveshells
        name = 54
        plugin_path = 55
        vendor = 56
        state = 53

    def __init__(self) -> None:
        super().__init__()
        self.vendor = self.plugin_path = self.name = None
        self.fourcc = self.guid = self.state = None

    def parse_event(self, e: _QWordVariableEvent) -> None:
        data = e.data
        self._events[str(e.id).split(".")[-1]] = e
        if e.id == self.EventID.vendor:
            self.vendor = data.decode("ascii")
        elif e.id == self.EventID.plugin_path:
            self.plugin_path = data.decode("ascii")
        elif e.id == self.EventID.name:
            self.name = data.decode("ascii")
        elif e.id == self.EventID.fourcc:
            self.fourcc = data.decode("ascii")
        elif e.id == self.EventID.guid:
            self.guid = data.decode("ascii")
        elif e.id == self.EventID.state:
            self.state = data


class VSTPluginEvent(_DataEvent):
    def __init__(self, id, data: bytes):
        super().__init__(id, data)
        self.parser = _VSTPluginParser()
        r = BytesIOEx(data)
        self.kind = r.read_i()
        if self.kind not in VSTPlugin.PLUGIN_VST:
            return

        while True:
            eid = r.read_i()
            if eid is None:
                break
            length = r.read_Q()
            data = r.read(length)
            event = _QWordVariableEvent(_VSTPluginParser.EventID(eid), data)
            self.parser.parse_event(event)

        self.name = self.parser.name
        self.vendor = self.parser.vendor
        self.plugin_path = self.parser.plugin_path
        self.state = self.parser.state
        self.fourcc = self.parser.fourcc
        self.guid = self.parser.guid

    def dump(self, n: str, v: Union[str, bytes]):
        self.parser._events[n].dump(v)


class VSTPlugin(_Plugin):
    """VST2/3 (including Waveshells, *maybe AU as well*) plugin data
    (`ChannelEventID.Plugin` & `InsertSlotEventID.Plugin` event).

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/wrapper.htm#wrapper_pluginsettings)
    """

    PLUGIN_VST = 8, 10

    @dataclasses.dataclass(init=False)
    class PluginIOInfo:
        mixer_offset: int
        flags: int

    # TODO
    def _setprop(self, n: str, v: Any):
        if n not in ("name", "vendor", "plugin_path", "fourcc", "state", "guid"):
            raise NotImplementedError
        self.__vpe.dump(n, v)
        super()._setprop(n, v)

    # * Properties
    midi_in: Optional[int] = _UIntProperty(_UIntValidator(255))
    """MIDI Input Port. Min: 0, Max: 255, Default: TODO."""

    midi_out: Optional[int] = _UIntProperty(_UIntValidator(255))
    """MIDI Output Port. Min: 0, Max: 255, Default: TODO."""

    pb_range: Optional[int] = _UIntProperty()
    """VST Wrapper settings -> MIDI -> Send pitch bend range (semitones)."""

    flags: Optional[int] = _IntProperty()
    """VST Wrapper settings, boolean values TODO"""

    inputs: Optional[int] = _UIntProperty()
    """Number of inputs to a plugin. Depend on the plugin.
    VST Wrapper settings -> Processing -> Connections."""

    outputs: Optional[int] = _UIntProperty()
    """Number of outputs of a plugin. Depend on the plugin.
    VST Wrapper settings -> Processing -> Connections."""

    @property
    def input_infos(self) -> List[PluginIOInfo]:
        """Input information."""
        return getattr(self, "_input_infos", [])

    @property
    def output_info(self) -> List[PluginIOInfo]:
        """Ouput information."""
        return getattr(self, "_output_info", [])

    vst_number: Optional[int] = _UIntProperty()
    """TODO. Maybe related to Waveshells."""

    fourcc: Optional[str] = _StrProperty(
        _StrValidator(minsize=4, maxsize=4, mustascii=True)
    )
    """FourCC e.g. "GtYc" or "Syl1" - a unique VST ID, as
    reserved by plugin dev on Steinberg portal (in ASCII)."""

    guid: Optional[str] = _StrProperty(_StrValidator(minsize=16, mustascii=True))
    """Waveshell unique plugin ID. Minimum size: 16."""

    state: bytes = _BytesProperty()
    """The actual plugin data. Plugin specific. Can be a list
    of floats/ints, but devs generally use their own format."""

    name: str = _StrProperty(_StrValidator(mustascii=True))
    """Factory name for VSTs (in ASCII)."""

    plugin_path: str = _StrProperty(_StrValidator(mustascii=True))
    """The absolute path to the plugin .dll on the disk in ASCII. *Why is
    this required? FL already creates a .fst when it discovers a plugin.*"""

    vendor: str = _StrProperty(_StrValidator(mustascii=True))
    """Plugin developer name (in ASCII)."""

    def parse_event(self, e: VSTPluginEvent) -> None:
        super()._parse_data_event(e)
        self.__vpe = e
        self._kind = e.kind
        self._name = e.name
        self._vendor = e.vendor
        self._plugin_path = e.plugin_path
        self._state = e.state
        self._fourcc = e.fourcc
        self._guid = e.guid

    # TODO: Improve this part
    def _save(self) -> ValuesView[VSTPluginEvent]:
        new = bytearray(UInt.pack(self._kind))
        events = self.__vpe.parser._events
        for attr in events.keys():
            new.extend(events[attr].to_raw())
        self.__vpe.data = new
        return super()._save()
