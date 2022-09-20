# type: ignore

from __future__ import annotations

import enum
import inspect
import os
import re
import sys

sys.path.insert(0, os.path.abspath(".."))

import m2r2

from pyflp._base import EventEnum, EventProp, ModelBase, NestedProp, StructProp

BITLY_LINK = re.compile(r"!\[.*\]\((https://bit\.ly/[A-z0-9]*)\)")
NEW_IN_FL = re.compile(r"\*New in FL Studio v([^\*]*)\*[\.:](.*)")
EVENT_ID_DOC = re.compile(r"([0-9\.]*)\+")
FL_BADGE = "https://img.shields.io/badge/FL%20Studio-{}+-5f686d?labelColor=ff7629&style=for-the-badge"
GHUC_PREFIX = "https://raw.githubusercontent.com/demberto/PyFLP/master/docs/"

project = "PyFLP"
copyright = "2022, demberto"
author = "demberto"
release = "2.0.0a0"
extensions = [
    "hoverxref.extension",
    "m2r2",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.duration",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_toolbox",
    "sphinx_toolbox.github",
    "sphinx_toolbox.sidebar_links",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"
autodoc_inherit_docstrings = False
autodoc_default_options = {
    "undoc-members": True,
    "exclude-members": "INTERNAL_NAME",
    "no-value": True,
}
needs_sphinx = "5.0"
hoverxref_auto_ref = True
coverage_ignore_pyobjects = ["[A-Z][A-z0-9]*Event"]
napoleon_preprocess_types = True
napoleon_attr_annotations = True
html_permalinks_icon = "<span>#</span>"
github_username = author
github_repository = project


def badge_flstudio(app, what, name, obj, options, lines):
    for line in lines:
        if name.split(".")[-2].endswith("ID"):  # Event ID member
            match = EVENT_ID_DOC.fullmatch(line)
        else:
            match = NEW_IN_FL.fullmatch(line)

        if match is not None:
            groups = tuple(
                filter(
                    lambda group: group != "",
                    map(lambda group: group.strip(), match.groups()),
                )
            )

            if len(groups) == 1:
                lines.insert(0, f".. image:: {FL_BADGE.format(groups[0])}")
                lines.insert(1, "")
            elif len(groups) == 2:
                grid = f"""
                .. figure:: {FL_BADGE.format(groups[0])}
                    :alt: New in FL Studio v{groups[0]}

                    {groups[1].strip()}

                """
                lines[:0] = grid.splitlines()  # https://stackoverflow.com/a/25855473
            lines.remove(line)


def add_annotations(app, what, name, obj, options, signature, return_annotation):
    if what == "class" and issubclass(obj, ModelBase):
        annotations = {}
        for name_, type in vars(obj).items():
            if isinstance(obj, NestedProp):
                annotations[name_] = type._type
            elif hasattr(type, "__orig_class__"):
                annotations[name_] = type.__orig_class__.__args__[0]

            if isinstance(type, (EventProp, StructProp)):
                annotations[name_] |= None

        if hasattr(obj, "__annotations__"):
            obj.__annotations__.update(annotations)
        else:
            obj.__annotations__ = annotations


def autodoc_markdown(app, what, name, obj, options, lines):
    newlines = m2r2.convert("\n".join(lines)).splitlines()
    lines.clear()
    lines.extend(newlines)


def remove_model_signature(app, what, name, obj, options, signature, return_annotation):
    """Removes the :func:`ModelBase.__init__` args from the docstrings.

    It's an implementation detail, and only clutters the docs.
    """
    if what == "class" and issubclass(obj, ModelBase):
        return ("", return_annotation)


def remove_enum_signature(app, what, name, obj, options, signature, return_annotation):
    """Removes erroneous :attr:`signature` = '(value)' for `enum.Enum` subclasses."""
    if inspect.isclass(obj) and issubclass(obj, enum.Enum):  # Event ID class
        return ("", return_annotation)


def include_obsolete_ids(app, what, name, obj, skip, options):
    """Includes obsolete / undocumented (prefixed with a `_`) event IDs."""
    if isinstance(obj, EventEnum):  # EventID member
        return False


def show_model_dunders(app, what, name, obj, skip, options):
    """ModelBase subclasses show these dunders regardless of any settings."""
    if name in ("__getitem__", "__setitem__", "__iter__", "__len__", "__index__"):
        return False


def setup(app):
    app.connect("autodoc-process-docstring", badge_flstudio)
    app.connect("autodoc-process-docstring", autodoc_markdown)
    app.connect("autodoc-process-signature", add_annotations)
    app.connect("autodoc-process-signature", remove_model_signature)
    app.connect("autodoc-process-signature", remove_enum_signature)
    app.connect("autodoc-skip-member", include_obsolete_ids)
    app.connect("autodoc-skip-member", show_model_dunders)
