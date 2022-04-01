import abc
from typing import Optional, ValuesView

from bytesioex import BytesIOEx

from pyflp._event import _DataEventType, _EventType
from pyflp._flobject import _FLObject


class _Plugin(_FLObject, abc.ABC):
    """Represents a native or VST2/VST3 effect or instrument.
    Parses only `ChannelEvent.Plugin`/`InsertSlotEvent.Plugin`."""

    _chunk_size: Optional[int] = None
    """Expected size of event data passed to `parse_event`.
    Parsing is skipped in case the size is not equal to this."""

    def _save(self) -> ValuesView[_EventType]:
        self._r.seek(0)
        self._events["plugin"].dump(self._r.read())
        return super()._save()

    def _parse_data_event(self, e: _DataEventType) -> None:
        self._events["plugin"] = e
        if self._chunk_size is not None:
            dl = len(e.data)
            if dl != self._chunk_size:  # pragma: no cover
                return
        self._r = BytesIOEx(e.data)


class _EffectPlugin(_Plugin):
    """Represents a native or VST2/VST3 effect. Used by `InsertSlot.plugin`."""


class _SynthPlugin(_Plugin):
    """Represents a native or VST2/VST3 instrument. Used by `Channel.plugin`."""
