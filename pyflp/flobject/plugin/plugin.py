import abc
from bytesioex import BytesIOEx
from pyflp.event import Event, DataEvent

from pyflp.flobject.flobject import FLObject

__all__ = ["Plugin", "EffectPlugin", "GeneratorPlugin"]


class Plugin(FLObject, abc.ABC):
    """Represents a native or VST2/VST3 effect or instrument.
    Parses only `ChannelEvent.Plugin`/`InsertSlotEvent.Plugin`.
    """

    # Not actually used by subclasses but provided for syntax highlighting below
    def _parse_data_event(self, event: DataEvent) -> None:
        self._events["data"] = event
        self._data = BytesIOEx(event.data)
        return super()._parse_data_event(event)

    def save(self) -> Event:  # type: ignore
        event = super().save()
        self._data.seek(0)
        buffer = self._data.read()
        self._events["data"].dump(buffer)
        return tuple(event)[0]  # ! How to avoid this?

    def __init__(self):
        super().__init__()


class EffectPlugin(Plugin):
    """Represents a native or VST2/VST3 effect.
    Used by `pyflp.flobject.insert.insert_slot.InsertSlot.plugin`."""

    def __init__(self):
        super().__init__()


class GeneratorPlugin(Plugin):
    """Represents a native or VST2/VST3 instrument.
    Used by `pyflp.flobject.channel.channel.Channel.plugin`."""

    def __init__(self):
        super().__init__()
