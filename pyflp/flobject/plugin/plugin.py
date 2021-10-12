import abc

from pyflp.flobject.flobject import FLObject


__all__ = ["Plugin", "EffectPlugin", "GeneratorPlugin"]


class Plugin(FLObject, abc.ABC):
    """Represents a native or VST2/VST3 effect or instrument.
    Parses only `ChannelEvent.Plugin`/`InsertSlotEvent.Plugin`.
    """

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
