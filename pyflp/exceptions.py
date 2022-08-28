# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""
pyflp.exceptions
================

Contains the exceptions shared across PyFLP.
"""

import sys
from typing import Any, Type

if sys.version_info >= (3, 8):
    from typing import SupportsIndex
else:
    from typing_extensions import SupportsIndex

__all__ = [
    "Error",
    "DataCorrupted",
    "EventIDOutOfRange",
    "InvalidEventChunkSize",
    "UnexpectedType",
    "ValueOutOfBounds",
    "PropertyCannotBeSet",
    "HeaderCorrupted",
    "VersionNotDetected",
    "InvalidValue",
]


class Error(Exception):
    """Base class for PyFLP exceptions.

    Some exceptions derive from standard Python exceptions to ease handling.
    """


class DataCorrupted(Error):
    pass


class EventIDOutOfRange(Error, ValueError):
    def __init__(self, id: int, min_i: int, max_e: int):
        super().__init__(f"Expected ID in {min_i}-{max_e - 1}; got {id} instead")


class InvalidEventChunkSize(Error, TypeError):
    """Raised when a fixed size event is created with a wrong amount of bytes."""

    def __init__(self, expected: int, got: int):
        super().__init__(f"Expected a bytes object of length {expected}; got {got}")


class UnexpectedType(Error, TypeError):
    def __init__(self, expected: Type[Any], got: Type[Any]):
        super().__init__(f"Expected a {expected} object; got a {got} object instead")


class ValueOutOfBounds(Error, IndexError, ValueError):
    def __init__(self, index: SupportsIndex):
        super().__init__(f"{index!r} is out of bounds for the list / underyling event")


class PropertyCannotBeSet(Error, AttributeError):
    def __init__(self, *ids: int):
        if len(ids) > 0:
            msg = f"Property cannot be set as event(s) {ids!r} was / were not found"
        else:
            msg = "Property cannot be set"
        super().__init__(msg)


class HeaderCorrupted(Error, ValueError):
    """Raised when the header chunk contains an unexpected / invalid value."""

    def __init__(self, desc: str):
        """
        Args:
            desc (str): A string containing details about what is corrupted.
        """
        super().__init__(f"Error parsing header: {desc}")


class ExpectedValue(Error, ValueError):
    def __init__(self, invalid: Any, *valid: Any):
        super().__init__(f"Invalid value {invalid!r}; expected one of {valid!r}")


class InvalidValue(Error, ValueError):
    """An alias for ValueError."""


class VersionNotDetected(Error):
    """Raised when the correct string decoder couldn't be decided.

    This happens due to absence of `ProjectID.Version` event or any string
    events occuring before it. Both cases indicated corruption.
    """
