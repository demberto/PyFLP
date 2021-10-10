"""
.. include:: ../README.md
.. include:: ../docs/flp-format.md
.. include:: ../docs/how-does-it-work.md
"""
__docformat__ = "restructuredtext"

import logging

logging.basicConfig(
    format="[%(levelname)s] %(name)s <%(module)s.%(funcName)s>  %(message)s"
)

from .parser import *
from .project import *
