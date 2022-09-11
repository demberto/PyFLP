# type: ignore

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from pyflp._base import EventEnum, NestedProp, ROProperty  # noqa
from pyflp.plugin import PluginProp  # noqa

project = "PyFLP"
copyright = "2022, demberto"
author = "demberto"
release = "2.0.0"
extensions = [
    "hoverxref.extension",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.duration",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_inline_tabs",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"
autodoc_inherit_docstrings = False
autodoc_default_options = {
    "undoc-members": True,
    "exclude-members": "INTERNAL_NAME",
    "show-inheritance": True,
}
needs_sphinx = "5.0"
hoverxref_auto_ref = True
coverage_ignore_pyobjects = ["[A-Z][A-z0-9]*Event"]
html_static_path = ["img"]
napoleon_preprocess_types = True
napoleon_attr_annotations = True
html_permalinks_icon = "<span>#</span>"

# TODO Replace New in FL Studio... with custom HTML elements
# def iconize_flstudio(app, what, name, obj, options, lines):
#     for idx, line in enumerate(lines):
#         lines[idx] = line.replace("FL Studio v", "🥭 ")


# TODO https://stackoverflow.com/q/73674809
def descriptor_annotations(app, what, name, obj, options, signature, return_annotation):
    if isinstance(obj, NestedProp):
        return ("", f"{obj._type.__name__} | None")
    elif isinstance(obj, PluginProp):
        return ("", "AnyPlugin | None")
    elif (
        isinstance(obj, ROProperty)
        and return_annotation is None
        and not isinstance(obj, property)
        and what == "attribute"
    ):
        return ("", f"{obj.__orig_class__.__args__[0].__name__} | None")


def include_obsolete_ids(app, what, name, obj, skip, options):
    if isinstance(obj, EventEnum):
        return False


def show_model_dunders(app, what, name, obj, skip, options):
    if name in ("__getitem__", "__setitem__", "__iter__", "__len__"):
        return False


def setup(app):
    # app.connect("autodoc-process-docstring", iconize_flstudio)
    app.connect("autodoc-process-signature", descriptor_annotations)
    app.connect("autodoc-skip-member", include_obsolete_ids)
    app.connect("autodoc-skip-member", show_model_dunders)
