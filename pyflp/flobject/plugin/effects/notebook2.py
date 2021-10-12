from typing import List, Optional
from pyflp.flobject.plugin.plugin import EffectPlugin
from pyflp.event import DataEvent

from bytesioex import BytesIOEx  # type: ignore

__all__ = ["FNoteBook2"]


class FNoteBook2(EffectPlugin):
    # 0,0,0,0 4b
    # current page number 4b
    # page number 4b - data length varint - text in utf16 for each page
    # 255, 255, 255, 255 4b
    # Editing enabled or disabled 1b

    # * Properties
    @property
    def pages(self) -> List[str]:
        """List of strings. One string per page."""
        return getattr(self, "_pages", [])

    @pages.setter
    def pages(self, value: List[str]):
        self._data.seek(8)
        for page_num, page in enumerate(value):
            self._data.write_I(page_num)  # TODO: or page_num + 1?
            wstr = page.encode("utf-16", errors="ignore")
            self._data.write_v(len(wstr))
            self._data.write(wstr)  # NULL bytes are not appended at the end
        self._pages = value

    @property
    def active_page_number(self) -> Optional[int]:
        """Currently selected page number."""
        return getattr(self, "_active_page_number", None)

    @active_page_number.setter
    def active_page_number(self, value: int):
        assert value in range(1, len(self._pages) + 1)  # TODO
        self._data.seek(4)
        self._data.write_I(value)
        self._active_page_number = value

    @property
    def editable(self) -> Optional[bool]:
        """Whether notebook is marked as editable or read-only."""
        return getattr(self, "_editable", None)

    @editable.setter
    def editable(self, value: bool):
        self._data.seek(-1, 2)
        self._data.write_bool(value)
        self._editable = value

    # ! This doesn't work
    def _parse_data_event(self, event: DataEvent) -> None:
        self._data = BytesIOEx(event.data)
        self._data.seek(4)
        self._active_page_number = self._data.read_I()
        while True:
            page_num = self._data.read_i()
            if page_num in (-1, None):
                break
            size = self._data.read_v()
            buffer = self._data.read(size)
            self._pages.append(buffer.decode("utf-16", errors="ignore"))
            print(self._pages)
        self._editable = self._data.read_bool()

    def __init__(self):
        self._pages = []
        super().__init__()
