from __future__ import annotations

import datetime
import pathlib
import textwrap

import pytest

import pyflp
from pyflp.project import VALID_PPQS, FileFormat, FLVersion, PanLaw, Project


def test_project(project: Project):
    assert project.artists == "demberto"
    assert project.channel_count == 19
    assert (
        project.comments
        == textwrap.dedent(
            """\
    This is a testing FLP used by PyFLP - An FL Studio project file parser.

    Notes for contributors:
    1. Make a separate item for every testable property (and its inverse if its a boolean).
    2. Give item names related to the property they will be tested for.

    Terms:
    "item(s)": Refers to a channel, inert, slot, clip, track, pattern, time marker, controller.
    """
        ).replace("\n", "\r")
    )  # Who the hell uses \r?
    assert project.created_on == datetime.datetime(2022, 9, 16, 20, 47, 12, 746000)
    assert project.data_path == pathlib.Path("")
    assert project.format == FileFormat.Project
    assert project.genre == "Testing..."
    assert project.licensed
    assert project.licensee == "VIKTORKHLEBNIKOV38394416"
    assert project.looped
    assert project.main_pitch == 0
    assert project.main_volume is None
    assert project.pan_law == PanLaw.Circular
    assert project.ppq == 96
    assert project.show_info
    assert project.tempo == 69.420
    # ! assert project.time_spent == datetime.timedelta(hours=2, minutes=35, seconds=53)
    assert project.title == "PyFLP Test FLP"
    assert project.url == "https://github.com/demberto/PyFLP"
    assert project.version == FLVersion(20, 8, 4, 2576)

    with pytest.raises(ValueError, match="cannot be less than zero"):
        project.channel_count = -1

    with pytest.raises(ValueError, match=f"{VALID_PPQS}"):
        project.ppq = 0

    with pytest.raises(ValueError, match="10.0-522.0"):
        project.tempo = 999.0

    with pytest.raises(ValueError, match="major.minor.build.patch?"):
        project.version = "2.2"  # type: ignore


def test_null_check(project: Project, tmp_path: pathlib.Path):
    pyflp.save(project, tmp_path / "null_check.flp")
    b1 = open(pathlib.Path(__file__).parent / "assets" / "FL 20.8.4.flp", "rb").read()
    b2 = open(tmp_path / "null_check.flp", "rb").read()
    result = b1 == b2  # ! Don't compare 2 big bytes objects in pytest EVER
    assert result
