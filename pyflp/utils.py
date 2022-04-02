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

from dataclasses import dataclass, field


def isascii(s: str) -> bool:
    """str.isascii() for Python 3.6

    Attribution: https://stackoverflow.com/a/18403812
    """
    return len(s) == len(s.encode())


def buflen_to_varint(buffer: bytes) -> bytes:
    ret = bytearray()
    buflen = len(buffer)
    while True:
        towrite = buflen & 0x7F
        buflen >>= 7
        if buflen > 0:
            towrite |= 0x80
        ret.append(towrite)
        if buflen <= 0:
            break
    return bytes(ret)


@dataclass
class FLVersion:
    string: str = field(repr=False)
    major: int = field(init=False)
    minor: int = field(init=False)
    revision: int = field(init=False)
    build: int = field(init=False)

    def __post_init__(self):
        split = self.string.split(".")
        self.major = int(split[0])
        self.minor = int(split[1])
        self.revision = int(split[2])
        try:
            self.build = int(split[3])
        except IndexError:  # pragma: no cover
            pass

    def as_float(self) -> float:
        return float(f"{self.major}.{self.minor}")
