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

"""Event implementations for FL Studio stock effects.

These effects have an implementation:
- Fruity Balance
- Fruity Fast Dist
- Fruity NoteBook 2
- Fruity Send
- Fruity Soft Clipper
- Fruity Stereo Enhancer
- Soundgoodizer
"""

from .balance import FBalance
from .fast_dist import FFastDist
from .notebook2 import FNoteBook2
from .send import FSend
from .soft_clipper import FSoftClipper
from .stereo_enhancer import FStereoEnhancer
from .soundgoodizer import Soundgoodizer
