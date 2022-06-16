# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

from typing import List, Optional

from pyflp._event import DataEventType
from pyflp.plugin._plugin import _EffectPlugin

__all__ = ["FNoteBook2"]


class FNoteBook2(_EffectPlugin):
    """Implements Fruity Notebook 2.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20NoteBook%202.htm)
    """

    # 0,0,0,0 4b
    # active page number 4b
    # page number 4b - (data length / 2) varint - text in utf16 for each page
    # 255, 255, 255, 255 4b
    # Editing enabled or disabled 1b

    def __repr__(self) -> str:
        return "<Fruity Notebook 2 {}, {}, {}>".format(
            f"{len(self.pages)} pages",
            f"active_page_number={self.active_page}",
            f"editable={self.editable}",
        )

    # * Properties
    @property
    def pages(self) -> List[str]:
        """List of strings. One string per page."""
        return self._pages

    @pages.setter
    def pages(self, value: List[str]) -> None:
        self._r.seek(8)
        for page_num, page in enumerate(value):
            self._r.write_I(page_num)  # TODO: or page_num + 1?
            wstr = page.encode("utf-16", errors="ignore")
            self._r.write_v(len(wstr))
            self._r.write(wstr)  # NULL bytes are not appended at the end
        self._pages = value

    @property
    def active_page(self) -> Optional[int]:
        """Currently selected page number."""
        return getattr(self, "_active_page", None)

    @active_page.setter
    def active_page(self, value: int) -> None:
        num_pages = len(self._pages) + 1
        if value not in range(1, num_pages):
            raise ValueError(f"Expected a value in (1, {num_pages})")
        self._r.seek(4)
        self._r.write_I(value)
        super()._setprop("active_page", value)

    @property
    def editable(self) -> Optional[bool]:
        """Whether notebook is editable or read-only."""
        return getattr(self, "_editable", None)

    @editable.setter
    def editable(self, value: bool) -> None:
        self._r.seek(-1, 2)
        self._r.write_bool(value)
        super()._setprop("editable", value)

    def _parse_data_event(self, e: DataEventType) -> None:
        super()._parse_data_event(e)
        r = self._r
        r.seek(4)
        self._active_page = r.read_I()
        while True:
            page_num = r.read_i()
            if page_num == -1:
                break
            size = r.read_v()
            buffer = r.read(size * 2)
            self._pages.append(buffer.decode("utf-16", errors="ignore"))
        self._editable = r.read_bool()

    def __init__(self) -> None:
        self._pages = []
        super().__init__()
