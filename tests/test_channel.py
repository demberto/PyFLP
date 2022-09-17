from __future__ import annotations

from pyflp.channel import ChannelRack


def test_channels(rack: ChannelRack):
    assert len(rack) == 12
    assert rack.fit_to_steps is None
    assert [group.name for group in rack.groups] == ["Audio", "Generators", "Unsorted"]
    assert not rack.swing
