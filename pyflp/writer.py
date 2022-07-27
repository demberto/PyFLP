import dataclasses
import os
import warnings
from typing import Any, Dict

from bytesioex import BytesIOEx

from .events import *
from .models import *

__all__ = ["save"]


def save(project: Project, file: os.PathLike) -> None:
    insert_iter = iter(project.inserts)
    cur_insert = next(insert_iter)
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

        elif id == EventID.ChColor and parse_channel:
            event.value = cur_channel.color

        elif id == EventID.ChCutGroup:
            event.value = cur_channel.cut_group

        elif id == EventID.ChCutoff:
            event.value = cur_channel.fx.cutoff

        elif id == EventID.ChDefaultName and parse_channel:
            event.value = cur_channel.default_name

        elif id == EventID.ChDelay:
            props.update(dataclasses.asdict(cur_channel.delay, {}))

        elif id == EventID.ChEnvelopeLFO:
            name = next(envlfo_iter)

            envelope = cur_channel.envelopes[name]
            for attr in props:
                if attr.startswith("envelope"):
                    props[attr] = getattr(envelope, attr.split(".")[1])

            lfo = cur_channel.lfos[name]
            flags = ChannelEnvelopeFlags(props["flags"])
            for param, flag in {
                lfo.is_synced: ChannelEnvelopeFlags.LFOTempoSync,
                lfo.is_retrig: ChannelEnvelopeFlags.LFORetrig,
            }.items():
                flags = flags | flag if param else flags & ~flag
            props["lfo.shape"] = int(lfo.shape)

        elif id == EventID.ChFadeIn:
            event.value = cur_channel.fx.fade_in

        elif id == EventID.ChFadeOut:
            event.value = cur_channel.fx.fade_out

        elif id == EventID.ChFineTune:
            event.value = cur_channel.keyboard.fine_tune

        elif id == EventID.ChGroupNum:
            event.value = project.groups.index(cur_channel.group)

        elif id == EventID.ChIcon and parse_channel:
            event.value = cur_channel.icon

        elif id == EventID.ChIsEnabled:
            event.value = cur_channel.enabled

        elif id == EventID.ChIsLocked:
            event.value = cur_channel.locked

        elif id == EventID.ChLayerFlags:
            event.value = cur_channel.layer_flags

        elif id == EventID.ChLevelAdjusts:
            props.update(dataclasses.asdict(cur_channel.level_adjusts, {}))

        elif id == EventID.ChLevels:
            props["pan"] = cur_channel.pan
            props["pitch_shift"] = cur_channel.pitch_shift
            props["volume"] = cur_channel.volume

        elif id == EventID.ChName and parse_channel:
            event.value = cur_channel.name

        elif id == EventID.ChNew:
            for iid, channel in project.channels.items():
                if iid == event.value:
                    cur_channel = channel
                    envlfo_iter = iter(ENVELOPE_NAMES)  # noqa: F841
                    tracking_iter = iter(TRACKING_TYPES)

        elif id in (EventID._ChPanByte, EventID._ChPanWord):
            event.value = cur_channel.pan

        elif id == EventID.ChParameters:
            arp = cur_channel.arp
            props["arp.direction"] = int(arp.direction)
            props["arp.range"] = arp.range
            props["arp.chord"] = arp.chord
            props["arp.time"] = arp.time
            props["arp.gate"] = arp.gate
            props["arp.slide"] = arp.slide
            props["arp.repeat"] = arp.repeat

        elif id == EventID.ChPlugin and parse_channel:
            pass

        elif id == EventID.ChPlugWrapper and parse_channel:
            pass

        elif id == EventID.ChPolyphony:
            polyphony = cur_channel.polyphony
            props["max"] = polyphony.max
            props["slide"] = polyphony.slide
            for flag, cond in {
                ChannelPolyphonyFlags.Mono: polyphony.is_mono,
                ChannelPolyphonyFlags.Porta: polyphony.is_porta,
            }.items():
                if cond:
                    props["flags"] |= flag
                else:
                    props["flags"] &= ~flag

        elif id == EventID.ChPreamp:
            event.value = cur_channel.fx.boost

        elif id == EventID.ChResonance:
            event.value = cur_channel.fx.resonance

        elif id == EventID.ChReverb:
            reverb = cur_channel.fx.reverb
            if reverb.kind == ChannelReverbType.B:
                return (ChannelReverbType.B, reverb.mix - ChannelReverbType.B)
            return (ChannelReverbType.A, reverb.mix)

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
            props.update(dataclasses.asdict(tracking, {}))

        elif id == EventID.ChUsesLoopPoints:
            event.value = cur_channel.playback.use_loop_points

        elif id in (EventID._ChVolByte, EventID._ChVolWord):
            event.value = cur_channel.volume

        elif id == EventID.ChZipped:
            event.value = cur_channel.zipped

        elif id == EventID.GroupName:
            event.value = next(groups_iter)

        elif id == EventID.InsColor:
            event.value = cur_insert.color

        elif id == EventID.InsFlags:
            parse_channel = False
            for flag, cond in {
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
                if cond:
                    props["flags"] |= flag
                else:
                    props["flags"] &= ~flag

        elif id == EventID.InsIcon:
            event.value = cur_insert.icon

        elif id == EventID.InsInput:
            event.value = cur_insert.input

        elif id == EventID.InsOutput:
            cur_insert = next(insert_iter)

        elif id == EventID.InsParameters:
            if event.stream_len % 12 != 0:
                warnings.warn("Insert parameters event size not divisible by 12")
                continue

            while stream.tell() < event.stream_len:
                stream.seek(4, 1)  # 4
                id = stream.read_B()  # 5
                stream.seek(1, 1)  # 6
                channel_data = stream.read_H()  # 8

                insert = project.inserts[(channel_data >> 6) & 0x7F]
                slot = insert.slots[channel_data & 0x3F]
                # TODO _insert_type = channel_data >> 13

                if id == InsParamsEventID.SlotEnabled:
                    msg = int(slot.enabled)
                elif id == InsParamsEventID.SlotMix:
                    msg = slot.mix
                elif id == InsParamsEventID.Volume:
                    msg = insert.volume
                elif id == InsParamsEventID.Pan:
                    msg = insert.pan
                elif id == InsParamsEventID.StereoSeparation:
                    msg = insert.stereo_separation
                elif id == InsParamsEventID.LowGain:
                    msg = insert.eq.low.gain
                elif id == InsParamsEventID.BandGain:
                    msg = insert.eq.band.gain
                elif id == InsParamsEventID.HighGain:
                    msg = insert.eq.high.gain
                elif id == InsParamsEventID.LowFreq:
                    msg = insert.eq.low.frequency
                elif id == InsParamsEventID.BandFreq:
                    msg = insert.eq.band.frequency
                elif id == InsParamsEventID.HighFreq:
                    msg = insert.eq.high.frequency
                elif id == InsParamsEventID.LowQ:
                    msg = insert.eq.low.resonance
                elif id == InsParamsEventID.BandQ:
                    msg = insert.eq.band.resonance
                elif id == InsParamsEventID.HighQ:
                    msg = insert.eq.high.resonance
                elif id in range(
                    InsParamsEventID.RouteVolStart, len(project.inserts) + 1
                ):
                    route_id = id - InsParamsEventID.RouteVolStart
                    msg = insert.routes[route_id].volume

                stream.write_I(msg)

        elif id == EventID.InsRouting:
            routing = bytearray()
            for route in cur_insert.routes:
                routing.append(route.is_routed)
            stream.write(routing)

        elif id == EventID.SlotColor:
            event.value = cur_slot.color

        elif id == EventID.SlotDefaultName:
            event.value = cur_slot.default_name

        elif id == EventID.SlotIcon:
            event.value = cur_slot.icon

        elif id == EventID.SlotIndex:
            event.value = cur_slot.index
            cur_insert.slots.append(cur_slot)
            cur_slot = InsertSlot()

        elif id == EventID.SlotName:
            event.value = cur_slot.name

        elif id == EventID.SlotPlugin:
            ...

        elif id == EventID.PatColor:
            event.value = cur_pattern.color

        elif id == EventID.PatControllers:
            ...

        elif id == EventID.PatName:
            event.value = cur_insert.name

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
            path_str = str(project.data_path)
            event.value = path_str if path_str != "." else ""

        elif id == EventID._ProjFitToSteps:
            event.value = project.fit_to_steps

        elif id == EventID.ProjFLVersion:
            v = project.version
            event.value = ".".join((v.major, v.minor, v.build, v.patch))

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

    stream = BytesIOEx(b"FLhd")
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
