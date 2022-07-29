import dataclasses
import os
import warnings
from typing import Any, Dict

from bytesioex import BytesIOEx

from .events import *
from .models import *

__all__ = ["save"]


def save(project: Project, file: os.PathLike) -> None:
    """Save a project back into a file.

    Args:
        project (Project): The project to be saved.
        file (os.PathLike): Path of the file to save the `project` into.
    """
    insert_iter = iter(project.inserts)
    cur_insert = next(insert_iter)
    cur_slot = project.inserts[0].slots[0]
    groups_iter = iter(project.groups)
    parse_channel = True

    for event_idx, event in enumerate(project._events):
        id = event.id
        if isinstance(event, StructEventBase):
            props: Dict[str, Any] = event.props
        elif isinstance(event, DataEventBase):
            stream = event.stream
            stream.seek(0)

        if id == EventID.ArrName:
            event.value = cur_arrangement.name

        elif id == EventID.ArrNew:
            cur_arrangement = project.arrangements[event.value]
            timemarker_iter = iter(cur_arrangement.timemarkers)
            track_iter = iter(cur_arrangement.tracks)

        elif id == EventID.ChAUSampleRate:
            event.value = cur_channel.au_sample_rate

        # elif id == EventID.ChChildren:
        #     event.value = cur_channel.children[layer_child_idx].iid
        #     layer_child_idx += 1

        elif id == EventID.ChCutGroup:
            event.value = cur_channel.cut_group

        elif id == EventID.ChCutoff:
            event.value = cur_channel.fx.cutoff

        elif id == EventID.ChDelay:
            props.update(dataclasses.asdict(cur_channel.delay))

        elif id == EventID.ChEnvelopeLFO:
            _name = next(envlfo_iter)

            _envelope = cur_channel.envelopes[_name]
            for attr in props.keys():
                if attr.startswith("envelope"):
                    props[attr] = getattr(_envelope, attr.split(".")[1])

            _lfo = cur_channel.lfos[_name]
            _flags = ChannelEnvelopeFlags(props["flags"])
            for param, _flag in {
                _lfo.is_synced: ChannelEnvelopeFlags.LFOTempoSync,
                _lfo.is_retrig: ChannelEnvelopeFlags.LFORetrig,
            }.items():
                _flags = _flags | _flag if param else _flags & ~_flag
            props["lfo.shape"] = int(_lfo.shape)

        elif id == EventID.ChFadeIn:
            event.value = cur_channel.fx.fade_in

        elif id == EventID.ChFadeOut:
            event.value = cur_channel.fx.fade_out

        elif id == EventID.ChFineTune:
            event.value = cur_channel.keyboard.fine_tune

        elif id == EventID.ChGroupNum:
            event.value = project.groups.index(cur_channel.group)

        elif id == EventID.ChIsEnabled:
            event.value = cur_channel.enabled

        elif id == EventID.ChIsLocked:
            event.value = cur_channel.locked

        elif id == EventID.ChLayerFlags:
            event.value = cur_channel.layer_flags

        elif id == EventID.ChLevelAdjusts:
            props.update(dataclasses.asdict(cur_channel.level_adjusts))

        elif id == EventID.ChLevels:
            props["pan"] = cur_channel.pan
            props["pitch_shift"] = cur_channel.pitch_shift
            props["volume"] = cur_channel.volume

        elif id == EventID.ChNew:
            for iid, channel in project.channels.items():
                if iid == event.value:
                    cur_channel = channel
                    envlfo_iter = iter(ENVELOPE_NAMES)  # noqa: F841
                    tracking_iter = iter(TRACKING_TYPES)

        elif id in (EventID._ChPanByte, EventID._ChPanWord):
            event.value = cur_channel.pan

        elif id == EventID.ChParameters:
            _arp = cur_channel.arp
            props["arp.direction"] = int(_arp.direction)
            props["arp.range"] = _arp.range
            props["arp.chord"] = _arp.chord
            props["arp.time"] = _arp.time
            props["arp.gate"] = _arp.gate
            props["arp.slide"] = _arp.slide
            props["arp.repeat"] = _arp.repeat

        elif id == EventID.ChPolyphony:
            _polyphony = cur_channel.polyphony
            props["max"] = _polyphony.max
            props["slide"] = _polyphony.slide
            for _flag, _cond in {
                ChannelPolyphonyFlags.Mono: _polyphony.is_mono,
                ChannelPolyphonyFlags.Porta: _polyphony.is_porta,
            }.items():
                if _cond:
                    props["flags"] |= _flag
                else:
                    props["flags"] &= ~_flag

        elif id == EventID.ChPreamp:
            event.value = cur_channel.fx.boost

        elif id == EventID.ChResonance:
            event.value = cur_channel.fx.resonance

        elif id == EventID.ChReverb:
            _reverb = cur_channel.fx.reverb
            if _reverb.type == ChannelReverbType.B:
                event.value = ChannelReverbType.B + _reverb.mix
            else:
                event.value = _reverb.mix

        elif id == EventID.ChRootNote:
            event.value = cur_channel.keyboard.root_note

        elif id == EventID.ChRoutedTo:
            event.value = cur_channel.target_insert

        elif id == EventID.ChSamplePath:
            event.value = cur_channel.sample_path

        elif id == EventID.ChSamplerFlags:
            event.value = cur_channel.sampler_flags

        elif id == EventID.ChStereoDelay:
            event.value = cur_channel.fx.stereo_delay

        elif id == EventID.ChStretchTime:
            event.value = cur_channel.stretching.time

        elif id == EventID.ChSwing:
            event.value = cur_channel.time.swing

        elif id == EventID.ChTracking:
            tracking = cur_channel.tracking[next(tracking_iter)]
            props.update(dataclasses.asdict(tracking))

        elif id == EventID.ChUsesLoopPoints:
            event.value = cur_channel.playback.use_loop_points

        elif id in (EventID._ChVolByte, EventID._ChVolWord):
            event.value = cur_channel.volume

        elif id == EventID.ChZipped:
            event.value = cur_channel.zipped

        elif id == EventID.GroupName:
            event.value = next(groups_iter).name

        elif id == EventID.InsColor:
            event.value = cur_insert.color

        elif id == EventID.InsFlags:
            parse_channel = False
            for _flag, _cond in {
                InsertFlags.DockMiddle: cur_insert.docked_to == InsertDock.Middle,
                InsertFlags.DockRight: cur_insert.docked_to == InsertDock.Right,
                InsertFlags.Enabled: cur_insert.enabled,
                InsertFlags.EnableEffects: not cur_insert.bypassed,
                InsertFlags.Locked: cur_insert.locked,
                InsertFlags.PolarityReversed: cur_insert.polarity_reversed,
                InsertFlags.SeparatorShown: cur_insert.separator_shown,
                InsertFlags.Solo: cur_insert.is_solo,
                InsertFlags.SwapLeftRight: cur_insert.channels_swapped,
            }.items():
                if _cond:
                    props["flags"] |= _flag
                else:
                    props["flags"] &= ~_flag

        elif id == EventID.InsIcon:
            event.value = cur_insert.icon

        elif id == EventID.InsInput:
            event.value = cur_insert.input

        elif id == EventID.InsOutput:
            try:
                cur_insert = next(insert_iter)
            except StopIteration:
                pass

        elif id == EventID.InsParameters:
            if event.stream_len % 12 != 0:
                warnings.warn("Insert parameters event size not divisible by 12")
                continue

            while stream.tell() < event.stream_len:
                stream.seek(4, 1)  # 4
                _id = stream.read_B()  # 5
                stream.seek(1, 1)  # 6
                _channel_data = stream.read_H()  # 8

                _insert = project.inserts[(_channel_data >> 6) & 0x7F]
                _slot = _insert.slots[_channel_data & 0x3F]
                # TODO _insert_type = channel_data >> 13

                if _id == InsParamsEventID.SlotEnabled:
                    _msg = int(_slot.enabled)
                elif _id == InsParamsEventID.SlotMix:
                    _msg = _slot.mix
                elif _id == InsParamsEventID.Volume:
                    _msg = _insert.volume
                elif _id == InsParamsEventID.Pan:
                    _msg = _insert.pan
                elif _id == InsParamsEventID.StereoSeparation:
                    _msg = _insert.stereo_separation
                elif _id == InsParamsEventID.LowGain:
                    _msg = _insert.eq.low.gain
                elif _id == InsParamsEventID.BandGain:
                    _msg = _insert.eq.band.gain
                elif _id == InsParamsEventID.HighGain:
                    _msg = _insert.eq.high.gain
                elif _id == InsParamsEventID.LowFreq:
                    _msg = _insert.eq.low.frequency
                elif _id == InsParamsEventID.BandFreq:
                    _msg = _insert.eq.band.frequency
                elif _id == InsParamsEventID.HighFreq:
                    _msg = _insert.eq.high.frequency
                elif _id == InsParamsEventID.LowQ:
                    _msg = _insert.eq.low.resonance
                elif _id == InsParamsEventID.BandQ:
                    _msg = _insert.eq.band.resonance
                elif _id == InsParamsEventID.HighQ:
                    _msg = _insert.eq.high.resonance
                elif _id in range(
                    InsParamsEventID.RouteVolStart, len(project.inserts) + 1
                ):
                    _route_id = _id - InsParamsEventID.RouteVolStart
                    _msg = _insert.routes[_route_id].volume

                stream.write_I(_msg)

        elif id == EventID.InsRouting:
            _routing = bytearray()
            for route in cur_insert.routes:
                _routing.append(route.is_routed)
            stream.write(_routing)

        elif id == EventID.SlotIndex:
            event.value = cur_slot.index
            cur_insert.slots.append(cur_slot)
            cur_slot = InsertSlot()

        elif id == EventID.PatColor:
            event.value = cur_pattern.color

        elif id == EventID.PatControllers:
            ...

        elif id == EventID.PatName:
            event.value = cur_pattern.name

        elif id == EventID.PatNew:
            cur_pattern = project.patterns[event.value]

        elif id == EventID.PatNotes:
            if event.stream_len % 24 != 0:
                warnings.warn("Pattern note size not divisible by 24.")
                continue

            for note in cur_pattern.notes:
                stream.write_I(note.position)
                stream.write_H(note.flags)
                stream.write_H(note.rack_channel)
                stream.write_I(note.length)
                stream.write_I(note.key)
                stream.write_b(note.fine_pitch)
                stream.seek(1, 1)
                stream.write_B(note.release)
                stream.write_B(note.midi_channel)
                stream.write_b(note.pan)
                stream.write_B(note.velocity)
                stream.write_B(note.mod_x)
                stream.write_B(note.mod_y)

        elif id == EventID.PlaylistData:
            if event.stream_len % 32 != 0:
                warnings.warn("Playlist data size not divisible by 32.")
                continue
            ...

        elif id == EventID.PlugColor:
            if parse_channel:
                event.value = cur_channel.color
            else:
                event.value = cur_slot.color

        elif id == EventID.PlugData:
            if parse_channel:
                _plugin = cur_channel.plugin
            else:
                _plugin = cur_slot.plugin

            if getattr(_plugin, "DEFAULT_NAME", None) == cur_channel.default_name:
                props.update(dataclasses.asdict(_plugin))

        elif id == EventID.PlugDefaultName:
            _cur_obj = cur_channel if parse_channel else cur_slot

            _plugin = _cur_obj.plugin
            if dataclasses.is_dataclass(_plugin):
                _cur_obj.default_name = _plugin.DEFAULT_NAME
            event.value = _cur_obj.default_name

        elif id == EventID.PlugIcon:
            if parse_channel:
                event.value = cur_channel.icon
            else:
                event.value = cur_slot.icon

        elif id == EventID.PlugName:
            if parse_channel:
                event.value = cur_channel.name
            else:
                event.value = cur_slot.name

        elif id == EventID.ProjArtists:
            event.value = project.artists

        elif id in (EventID.ProjComments, EventID._ProjRTFComments):
            event.value = project.comments

        elif id == EventID.ProjCurGroupId:
            try:
                event.value = project.groups.index(project.selection.group)
            except ValueError:
                pass

        # elif id == EventID.ProjCurPatIdx:
        #     event.value = project.selection.pattern

        elif id == EventID.ProjDataPath:
            _path_str = str(project.data_path)
            event.value = _path_str if _path_str != "." else ""

        elif id == EventID._ProjFitToSteps:
            event.value = project.fit_to_steps

        elif id == EventID.ProjFLVersion:
            _v = project.version
            event.value = f"{_v.major}.{_v.minor}.{_v.build}.{_v.patch}"

        elif id == EventID.ProjGenre:
            event.value = project.genre

        elif id == EventID.ProjLoopActive:
            event.value = project.loop_active

        elif id == EventID.ProjLoopPos:
            event.value = project.selection.song_loop

        elif id == EventID.ProjPanLaw:
            event.value = int(project.pan_law)

        elif id == EventID.ProjPitch:
            event.value = project.main_pitch

        elif id == EventID.ProjPlayTruncatedNotes:
            event.value = project.play_truncated_notes

        elif id == EventID.ProjRegistered:
            event.value = project.registered

        elif id == EventID.ProjRegisteredTo:
            event.value = project.registered_to

        elif id == EventID.ProjShowInfo:
            event.value = project.show_info

        elif id == EventID.ProjSwing:
            event.value = project.swing

        elif id == EventID.ProjTempo:
            event.value = int(project.tempo * 1000)

        elif id == EventID.ProjTimeSigBeat:
            event.value = project.time_signature.beat

        elif id == EventID.ProjTimeSigNum:
            event.value = project.time_signature.num

        elif id == EventID.ProjTimestamp:
            props["created_on"] = (project.created_on - DELPHI_EPOCH).total_seconds()
            props["work_time"] = project.work_time.total_seconds()

        elif id == EventID.ProjUrl:
            event.value = project.url

        elif id == EventID.ProjVerBuild:
            event.value = project.version_build

        elif id == EventID._ProjVolume:
            event.value = project.main_volume

        elif id == EventID.TMDenominator:
            event.value = cur_timemarker.denominator

        elif id == EventID.TMName:
            event.value = cur_timemarker.name

        elif id == EventID.TMNumerator:
            event.value = cur_timemarker.numerator

        elif id == EventID.TMPosition:
            cur_timemarker = next(timemarker_iter)
            if cur_timemarker.type == TimeMarkerType.Signature:
                event.value = TimeMarkerType.Signature + cur_timemarker.position
            else:
                event.value = cur_timemarker.position

        elif id == EventID.TrackData:
            cur_track = next(track_iter)
            props.update(dataclasses.asdict(cur_track))

        elif id == EventID.TrackName:
            event.value = cur_track.name

    event_chunklen = 0
    for event in project._events:
        event_chunklen += len(event)

    stream = BytesIOEx()
    stream.write(b"FLhd")
    stream.write_I(6)
    stream.write_h(project.format)
    stream.write_H(project.channel_count)
    stream.write_H(project.ppq)
    stream.write(b"FLdt")
    stream.write_I(event_chunklen)
    for event in project._events:
        stream.write(bytes(event))

    with open(file, "wb+") as flp:
        flp.write(stream.getvalue())
