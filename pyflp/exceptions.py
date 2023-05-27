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

"""Contains the exceptions used by and shared across PyFLP."""

from __future__ import annotations

import enum

__all__ = [
    "Error",
    "NoModelsFound",
    "EventIDOutOfRange",
    "InvalidEventChunkSize",
    "PropertyCannotBeSet",
    "HeaderCorrupted",
    "VersionNotDetected",
    "ModelNotFound",
    "DataCorrupted",
]


class Error(Exception):
    """Base class for PyFLP exceptions.

    It is not guaranteed that exceptions raised from PyFLP always subclass Error.
    This is done to prevent duplication of exceptions. All exceptions raised by
    a function (in its body) explicitly are documented.

    Some exceptions derive from standard Python exceptions to ease handling.
    """


class EventIDOutOfRange(Error, ValueError):
    """An event is created with an ID out of its allowed range."""

    def __init__(self, id: int, *expected: int) -> None:
        super().__init__(f"Expected ID in {expected!r}; got {id!r} instead")


class InvalidEventChunkSize(Error, BufferError):
    """A fixed size event is created with a wrong amount of bytes."""

    def __init__(self, expected: int, got: int) -> None:
        super().__init__(f"Expected a bytes object of length {expected}; got {got}")


class PropertyCannotBeSet(Error, AttributeError):
    def __init__(self, *ids: enum.Enum | int) -> None:
        super().__init__(f"Event(s) {ids!r} was / were not found")


class DataCorrupted(Error):
    """Base class for parsing exceptions."""


class HeaderCorrupted(DataCorrupted, ValueError):
    """Header chunk contains an unexpected / invalid value.

    Args:
        desc: A string containing details about what is corrupted.
    """

    def __init__(self, desc: str) -> None:
        super().__init__(f"Error parsing header: {desc}")


class NoModelsFound(DataCorrupted, LookupError):
    """Model's `__iter__` method fails to generate any model."""


class ModelNotFound(DataCorrupted, IndexError):
    """An invalid index is passed to model's `__getitem__` method."""


class VersionNotDetected(DataCorrupted):
    """String decoder couldn't be decided due to absence of project version."""
