from __future__ import annotations

from typing import Callable

import colour
import pytest

from pyflp.arrangement import (
    Arrangement,
    Arrangements,
    ChannelPLItem,
    PatternPLItem,
    Track,
    TrackMotion,
    TrackPress,
    TrackSync,
)


def test_arrangements(arrangements: Arrangements):
    assert len(arrangements) == 2
    assert arrangements.current == arrangements[0]
    assert arrangements.loop_pos is None
    assert arrangements.max_tracks == 500
    assert arrangements.time_signature.num == 4
    assert arrangements.time_signature.beat == 4


@pytest.fixture(scope="session")
def arrangement(arrangements: Arrangements):
    def wrapper(index: int):
        return arrangements[index]

    return wrapper


@pytest.fixture(scope="session")
def tracks(arrangement: Callable[[int], Arrangement]):
    return tuple(arrangement(0).tracks)[:22]


def test_track_color(tracks: tuple[Track, ...]):
    for track in tracks:
        assert (
            track.color == colour.Color("red")
            if track.name == "Red"
            else track.color == colour.Color("#485156")
        )


def test_track_content_locked(tracks: tuple[Track, ...]):
    for track in tracks:
        assert (
            track.content_locked
            if track.name == "Locked to content"
            else not track.content_locked
        )


def test_track_enabled(tracks: tuple[Track, ...]):
    for track in tracks:
        assert not track.enabled if track.name == "Disabled" else track.enabled


def test_track_grouped(tracks: tuple[Track, ...]):
    for track in tracks:
        assert track.grouped if track.name == "Grouped" else not track.grouped


# TODO #35
# def test_track_height(tracks: tuple[Track, ...]):
#     for track in tracks:
#         if track.name == "Min Size":
#             assert track.height == 0.0
#         elif track.name == "Max Size":
#             assert track.height == 18.4
#         else:
#             assert track.height == 1.0


def test_track_icon(tracks: tuple[Track, ...]):
    for track in tracks:
        assert track.icon == 70 if track.name == "Iconified" else not track.icon


def test_track_items(tracks: tuple[Track, ...]):
    for track in tracks:
        num_items = 0
        if track.name == "Audio track":
            num_items = 16
            assert set(type(i) for i in track) == set((ChannelPLItem,))
            assert set(i.channel.iid for i in track) == set((11,))  # type: ignore
        elif track.name == "MIDI":
            num_items = 4
            assert set(type(i) for i in track) == set((PatternPLItem,))
            assert set(i.pattern.index for i in track) == set((3,))  # type: ignore
            assert [i.position for i in track] == [p * 384 for p in range(num_items)]
        elif track.name in ("Cut pattern", "Automation"):
            num_items = 1

        assert len(track) == num_items
        assert [i.group for i in track] == [0] * num_items


def test_track_locked(tracks: tuple[Track, ...]):
    for track in tracks:
        assert track.locked if track.name == "Locked" else not track.locked


def test_track_motion(tracks: tuple[Track, ...]):
    for track in tracks:
        assert (
            track.motion == TrackMotion.Random
            if track.name == "Random Motion"
            else track.motion == TrackMotion.Stay
        )


def test_track_name(tracks: tuple[Track, ...]):
    assert [track.name for track in tracks] == [
        None,
        "Enabled",
        "Disabled",
        "Locked",
        "Red",
        "Iconified",
        "Grouped",
        "Audio track",
        "Instrument track",
        "MIDI",
        "Cut pattern",
        "Automation",
        "Locked to content",
        "Locked to size",
        "Min Size",
        "Max Size",
        "Latched",
        "Random Motion",
        "Trigger Sync OFF",
        "Position Sync AUTO",
        "Queued",
        "Intolerant",
    ]


def test_track_position_sync(tracks: tuple[Track, ...]):
    for track in tracks:
        assert (
            track.position_sync == TrackSync.Auto
            if track.name == "Position Sync AUTO"
            else track.position_sync == TrackSync.Off
        )


def test_track_press(tracks: tuple[Track, ...]):
    for track in tracks:
        assert (
            track.press == TrackPress.Latch
            if track.name == "Latched"
            else track.press == TrackPress.Retrigger
        )


def test_track_tolerant(tracks: tuple[Track, ...]):
    for track in tracks:
        assert not track.tolerant if track.name == "Intolerant" else track.tolerant


def test_track_queued(tracks: tuple[Track, ...]):
    for track in tracks:
        assert track.queued if track.name == "Queued" else not track.queued


def test_first_arrangement(arrangement: Callable[[int], Arrangement]):
    arr = arrangement(0)
    assert arr.name == "Just tracks"
    assert not tuple(arr.timemarkers)
    assert len(tuple(arr.tracks)) == 500


def test_second_arrangement(arrangement: Callable[[int], Arrangement]):
    arr = arrangement(1)
    assert arr.name == "Just timemarkers"
    assert len(tuple(arr.timemarkers)) == 11
    assert len(tuple(arr.tracks)) == 500
