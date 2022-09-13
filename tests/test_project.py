import datetime
import pathlib

from pyflp.project import FileFormat, FLVersion, PanLaw, Project


def test_project(project: Project):
    assert project.artists == "demberto"
    assert project.channel_count == 6
    assert project.comments == "A test FLP created for PyFLP."
    assert project.created_on == datetime.datetime(2021, 10, 4, 14, 24, 40, 190000)
    assert project.data_path == pathlib.Path("")
    assert project.format == FileFormat.Project
    assert project.genre == "Christian Gangsta Rap"
    assert project.licensed
    assert project.licensee == "zhoupengfei36732654"
    assert project.looped
    assert project.main_pitch == 0
    assert project.main_volume is None
    assert project.pan_law == PanLaw.Circular
    assert project.ppq == 96
    assert not project.show_info
    assert project.tempo == 69.420
    # ! assert project.time_spent == datetime.timedelta(hours=2, minutes=35, seconds=53)
    assert project.title == "Test"
    assert project.url == "https://github.com/demberto/PyFLP"
    assert project.version == FLVersion(20, 8, 3, 2304)
