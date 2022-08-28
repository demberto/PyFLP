import datetime
import pathlib

from pyflp.project import FileFormat, FLVersion, PanLaw, Project


def test_project(project: Project):
    assert len(project.arrangements) == 2
    assert project.artists == "demberto"
    assert project.channel_count == 6
    assert project.comments == "A test FLP created for PyFLP."
    assert project.created_on == datetime.datetime(2021, 10, 4, 14, 24, 40, 190000)
    assert project.data_path == pathlib.Path("")
    assert project.channels.fit_to_steps is None
    assert project.format == FileFormat.Project
    assert project.genre == "Christian Gangsta Rap"
    assert [group.name for group in project.channels.groups] == [
        "Audio",
        "Automation",
        "Instrument",
        "Layer",
        "Sampler",
        "Unsorted",
    ]
    assert len(list(project.mixer.inserts)) == 127
    assert project.looped
    assert project.main_pitch == 0
    assert project.main_volume is None
    assert project.pan_law == PanLaw.Circular
    assert len(project.patterns) == 4
    assert project.patterns.play_cut_notes
    assert project.ppq == 96
    assert project.licensed
    assert project.licensee == "zhoupengfei36732654"
    assert project.patterns.current == list(project.patterns)[3]
    assert project.arrangements.loop_pos is None
    assert not project.show_info
    assert project.channels.swing == 64
    assert project.tempo == 69.420
    assert project.arrangements.time_signature.num == 2
    assert project.arrangements.time_signature.beat == 8
    assert project.title == "Test"
    assert project.url == "https://github.com/demberto/PyFLP"
    assert project.version == FLVersion(20, 8, 3, 2304)
