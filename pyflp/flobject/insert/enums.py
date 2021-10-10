import enum

from pyflp.utils import WORD, DWORD, TEXT, DATA

__all__ = ["InsertEvent", "InsertSlotEvent"]


@enum.unique
class InsertEvent(enum.IntEnum):
    Parameters = DATA + 28
    # Slot events come here
    Routing = DATA + 27
    Input = DWORD + 26
    Output = DWORD + 19
    Color = DWORD + 21
    Icon = WORD + 31
    Name = TEXT + 12


@enum.unique
class InsertSlotEvent(enum.IntEnum):
    DefaultName = TEXT + 9
    Name = TEXT + 11
    PluginNew = (
        DATA + 4
    )  # TODO: Plugin wrapper data, windows pos of plugin etc, currently selected plugin wrapper page; minimized, closed or not
    Icon = DWORD + 27
    Color = DWORD
    Plugin = DATA + 5  # Plugin preset data, this is what uses the most space typically
    Index = WORD + 34  # FL 12.3+
