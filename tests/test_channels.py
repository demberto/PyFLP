from pyflp import Project


def test_channels(project: Project):
    assert len(project.channels) == 6
    assert project.channels.fit_to_steps is None
    assert [group.name for group in project.channels.groups] == [
        "Audio",
        "Automation",
        "Instrument",
        "Layer",
        "Sampler",
        "Unsorted",
    ]
