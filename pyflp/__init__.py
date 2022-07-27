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

"""
PyFLP - FL Studio project file parser
=====================================

To load a project file:

    >>> import pyflp
    >>> project = pyflp.parse("/path/to/parse.flp")

To save a project back:

    >>> pyflp.save(project, "/path/to/save.flp")

Full docs are available at https://pyflp.rtfd.io.
"""

from .reader import parse
from .writer import save
