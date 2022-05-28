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

__all__ = [
    "Error",
    "DataCorruptionDetectedError",
    "InvalidHeaderSizeError",
    "InvalidMagicError",
    "OperationNotPermittedError",
]


class Error(Exception):
    """Base class for PyFLP exceptions"""

    def __init__(self, what: str, *args: object) -> None:
        self.__what = what
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{type(self).__doc__}: {self.__what}"

    __str__ = __repr__


class DataCorruptionDetectedError(Error):
    """Possible corruption in event data detected"""


class InvalidHeaderSizeError(Error):
    """Invalid header size"""

    def __init__(self, size: int) -> None:
        super().__init__(size)


class InvalidMagicError(Error):
    """Invalid header magic number"""


class OperationNotPermittedError(Error):
    """Operation not permitted"""
