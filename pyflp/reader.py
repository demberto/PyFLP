import dataclasses
import os
import pathlib
import warnings
from collections import defaultdict
from datetime import timedelta
from typing import DefaultDict, Dict, List

from bytesioex import BytesIOEx

from .events import *
from .models import *


class ParseError(Error):
    pass


class HeaderParseError(ParseError):
    pass


class EventParseError(ParseError):
    def __init__(self, event: EventType, idx: int) -> None:
        super().__init__(f"Failed to parse event #{idx} {event!r}")


def parse(file: os.PathLike, dont_fail: bool = False) -> Project:
    """Parse an FL Studio project file.

    Args:
        file (os.PathLike): Path to the FLP.
        dont_fail (bool, optional): Dont't raise an exception if a certain event
            fails to get parsed and return as is. Defaults to False.

    Raises:
        HeaderParseError: When parsing the file header fails.
        EventParseError: When parsing a certain event fails and `dont_fail` is False.

    Returns:
        Project: The parsed object, whose properties might be dirty / incorrect,
            if errors occured during parsing. However the underlying event data
            will be completely free from any errors, if the source file event data
            wasn't corrupted.
    """

    with open(file, "rb") as flp:
        stream = BytesIOEx(flp.read())

    events: List[EventType] = []
    project = Project.with_events(events)

    if stream.read(4) != b"FLhd":  # 4
        raise ParseError("Unexpected header chunk magic")

    if stream.read_I() != 6:  # 8
        raise ParseError("Unexpected header chunk size")

    format = stream.read_H()  # 10
    try:
        format = FileFormat(format)
    except ValueError:
        raise ParseError("Unsupported project format")
    else:
        project.format = format

    project.channel_count = stream.read_H()  # 12
    project.ppq = stream.read_H()  # 14

    if stream.read(4) != b"FLdt":  # 18
        raise ParseError("Unexpected data chunk magic")

    event_chunklen = stream.read_I()  # 22
    stream.seek(0, os.SEEK_END)
    file_size = stream.tell()
    if file_size != event_chunklen + 22:
        raise ParseError("Data chunk size corrupted")

    str_type = None
    stream.seek(22)  # Back to start of events
    while stream.tell() < file_size:
        id = stream.read_B()
        event_type = None

        if id < WORD:
            value = stream.read(1)
        elif id < DWORD:
            value = stream.read(2)
        elif id < TEXT:
            value = stream.read(4)
        else:
            value = stream.read(stream.read_v())

        if id in {member.value for member in EventID.__members__.values()}:
            event_type = EventID(id).type

            if id == EventID.ProjFLVersion:
                if int(value.decode("ascii").split(".")[0]) >= 12:
                    str_type = UnicodeEvent
                else:
                    str_type = AsciiEvent

        if event_type is None:
            if id < WORD:
                event_type = U8Event
            elif id < DWORD:
                event_type = U16Event
            elif id < TEXT:
                event_type = U32Event
            elif id < DATA or id in NEW_TEXT_IDS:
                event_type = str_type
            else:
                event_type = UnknownDataEvent

        if event_type == PluginEvent:
            event = event_type(value)
        else:
            event = event_type(id, value)
        events.append(event)

    cur_arrangement = Arrangement()
    project.arrangements[0] = cur_arrangement  # For projects not having one
    cur_slot = InsertSlot()
    cur_insert = Insert()
    cur_timemarker = TimeMarker()
    cur_channel = cur_pattern = cur_track = cur_pattern_idx = None
    channel_ctrls: List[RemoteController] = []  # TODO find target channel
    slot_ctrls: Dict[int, Dict[int, List[RemoteController]]] = {}
    track_items: DefaultDict[int, List[PlaylistItemType]] = defaultdict(list)
    parse_channel = True  # Slot and Channel share event IDs, this is a marker

    try:
        for event_idx, event in enumerate(events):
            id = event.id
            if isinstance(event, (FixedSizeEventBase, StrEventBase)):
                value = event.value
            elif isinstance(event, StructEventBase):
                props = event.props
            elif isinstance(event, DataEventBase):
                stream = event.stream

            if id == EventID.ArrNew and value != 0:  # first one is already added
                project.arrangements[value] = cur_arrangement = Arrangement()

            elif id == EventID.ArrName:
                cur_arrangement.name = value

            elif id == EventID.ChAUSampleRate:
                cur_channel.au_sample_rate = value

            elif id == EventID.ChChildren:
                cur_channel.children.append(value)

            elif id == EventID.ChCutGroup:
                cur_channel.cut_group = value

            elif id == EventID.ChCutoff:
                cur_channel.fx.cutoff = value

            elif id == EventID.ChDelay:
                cur_channel.delay = ChannelDelay(**props)

            elif id == EventID.ChEnvelopeLFO:
                name = next(envlfo_iter)

                envelope = cur_channel.envelopes[name]
                for attr, value in props.items():
                    if attr.startswith("envelope"):
                        setattr(envelope, attr.split(".")[1], value)

                lfo = cur_channel.lfos[name]
                flags = ChannelEnvelopeFlags(props["flags"])
                lfo.is_synced = ChannelEnvelopeFlags.LFOTempoSync in flags
                lfo.is_retrig = ChannelEnvelopeFlags.LFORetrig in flags
                lfo.shape = ChannelLFOShape(props["lfo.shape"])

            elif id == EventID.ChFadeIn:
                cur_channel.fx.fade_in = value

            elif id == EventID.ChFadeOut:
                cur_channel.fx.fade_out = value

            elif id == EventID.ChFineTune:
                cur_channel.keyboard.fine_tune = value

            elif id == EventID.ChGroupNum:
                cur_channel.group = project.groups[value]

            elif id == EventID.ChIsEnabled:
                cur_channel.enabled = value

            elif id == EventID.ChIsLocked:
                cur_channel.locked = value

            elif id == EventID.ChLayerFlags:
                cur_channel.layer_flags = value

            elif id == EventID.ChLevelAdjusts:
                level_adjusts = cur_channel.level_adjusts
                for name in dataclasses.asdict(level_adjusts):
                    setattr(level_adjusts, name, props[name])

            elif id == EventID.ChLevels:
                cur_channel.pan = props["pan"]
                cur_channel.pitch_shift = props["pitch_shift"]
                cur_channel.volume = props["volume"]

            elif id == EventID.ChNew:
                project.channels[value] = cur_channel = Channel()
                envlfo_iter = iter(ENVELOPE_NAMES)  # noqa: F841
                tracking_iter = iter(TRACKING_TYPES)

            elif id in (EventID._ChPanByte, EventID._ChPanWord):
                cur_channel.pan = value

            elif id == EventID.ChParameters:
                arp = cur_channel.arp
                arp.direction = ChannelArpDirection(props["arp.direction"])
                arp.range = props["arp.range"]
                arp.chord = props["arp.chord"]
                arp.time = props["arp.time"]
                arp.gate = props["arp.gate"]
                arp.slide = props["arp.slide"]
                arp.repeat = props["arp.repeat"]

            elif id == EventID.ChPolyphony:
                polyphony = cur_channel.polyphony
                polyphony.max = props["max"]
                polyphony.slide = props["slide"]
                flags = ChannelPolyphonyFlags(props["flags"])
                polyphony.is_mono = ChannelPolyphonyFlags.Mono in flags
                polyphony.is_porta = ChannelPolyphonyFlags.Porta in flags

            elif id == EventID.ChPreamp:
                cur_channel.fx.boost = value

            elif id == EventID.ChResonance:
                cur_channel.fx.resonance = value

            elif id == EventID.ChReverb:
                reverb = cur_channel.fx.reverb
                if value >= ChannelReverbType.B:
                    reverb.type = ChannelReverbType.B
                    reverb.mix = value - ChannelReverbType.B
                else:
                    reverb.type = ChannelReverbType.A
                    reverb.mix = value

            elif id == EventID.ChRootNote:
                cur_channel.keyboard.root_note = value

            elif id == EventID.ChRoutedTo:
                cur_channel.target_insert = value

            elif id == EventID.ChSamplerFlags:
                cur_channel.sampler_flags = value

            elif id == EventID.ChSamplePath:
                cur_channel.sample_path = value

            elif id == EventID.ChStereoDelay:
                cur_channel.fx.stereo_delay = value

            elif id == EventID.ChStretchTime:
                cur_channel.stretching.time = value

            elif id == EventID.ChSwing:
                cur_channel.time.swing = value

            elif id == EventID.ChTracking:
                tracking = cur_channel.tracking[next(tracking_iter)]
                tracking.middle_value = props["middle_value"]
                tracking.pan = props["pan"]
                tracking.mod_x = props["mod_x"]
                tracking.mod_y = props["mod_y"]

            elif id == EventID.ChType:
                cur_channel.type = ChannelType(value)

            elif id == EventID.ChUsesLoopPoints:
                cur_channel.playback.use_loop_points = value

            elif id in (EventID._ChVolByte, EventID._ChVolWord):
                cur_channel.volume = value

            elif id == EventID.ChZipped:
                cur_channel.zipped = value

            elif id == EventID.GroupName:
                project.groups.append(DisplayGroup(name=value))

            elif id == EventID.InsColor:
                cur_insert.color = value

            elif id == EventID.InsFlags:
                parse_channel = False  # ! assumption: no more Channel events after this
                flags = InsertFlags(props["flags"])

                if InsertFlags.DockMiddle in flags:
                    dock = InsertDock.Middle
                elif InsertFlags.DockRight in flags:
                    dock = InsertDock.Right
                else:
                    dock = InsertDock.Left

                cur_insert.bypassed = InsertFlags.EnableEffects not in flags
                cur_insert.channels_swapped = InsertFlags.SwapLeftRight in flags
                cur_insert.docked_to = dock
                cur_insert.enabled = InsertFlags.Enabled in flags
                cur_insert.is_solo = InsertFlags.Solo in flags
                cur_insert.locked = InsertFlags.Locked in flags
                cur_insert.polarity_reversed = InsertFlags.PolarityReversed in flags
                cur_insert.separator_shown = InsertFlags.SeparatorShown in flags

            elif id == EventID.InsIcon:
                cur_insert.icon = value

            elif id == EventID.InsInput:
                cur_insert.input = value

            elif id == EventID.InsName:
                cur_insert.name = value

            elif id == EventID.InsOutput:
                cur_insert.output = value
                project.inserts.append(cur_insert)
                cur_insert = Insert()

            elif id == EventID.InsParameters:
                if event.stream_len % 12 != 0:
                    warnings.warn("Insert parameters event size not divisible by 12")
                    continue

                while stream.tell() < event.stream_len:
                    stream.seek(4, 1)  # 4
                    id = stream.read_B()  # 5
                    stream.seek(1, 1)  # 6
                    channel_data = stream.read_H()  # 8
                    msg = stream.read_I()  # 12

                    insert = project.inserts[(channel_data >> 6) & 0x7F]
                    slot = insert.slots[channel_data & 0x3F]
                    # TODO _insert_type = channel_data >> 13

                    if id == InsParamsEventID.SlotEnabled:
                        slot.enabled = msg != 0
                    elif id == InsParamsEventID.SlotMix:
                        slot.mix = msg
                    elif id == InsParamsEventID.Volume:
                        insert.volume = msg
                    elif id == InsParamsEventID.Pan:
                        insert.pan = msg
                    elif id == InsParamsEventID.StereoSeparation:
                        insert.stereo_separation = msg
                    elif id == InsParamsEventID.LowGain:
                        insert.eq.low.gain = msg
                    elif id == InsParamsEventID.BandGain:
                        insert.eq.band.gain = msg
                    elif id == InsParamsEventID.HighGain:
                        insert.eq.high.gain = msg
                    elif id == InsParamsEventID.LowFreq:
                        insert.eq.low.frequency = msg
                    elif id == InsParamsEventID.BandFreq:
                        insert.eq.band.frequency = msg
                    elif id == InsParamsEventID.HighFreq:
                        insert.eq.high.frequency = msg
                    elif id == InsParamsEventID.LowQ:
                        insert.eq.low.resonance = msg
                    elif id == InsParamsEventID.BandQ:
                        insert.eq.band.resonance = msg
                    elif id == InsParamsEventID.HighQ:
                        insert.eq.high.resonance = msg
                    elif id in range(
                        InsParamsEventID.RouteVolStart, len(project.inserts) + 1
                    ):
                        route_id = id - InsParamsEventID.RouteVolStart
                        insert.routes[route_id].volume = msg

            elif id == EventID.InsRouting:
                for is_routed in stream.getvalue():
                    cur_insert.routes.append(InsertRoute(is_routed == b"\x01"))

            elif id == EventID.SlotIndex:
                cur_slot.index = value
                cur_insert.slots.append(cur_slot)
                cur_slot = InsertSlot()

            elif id == EventID.PatNew:
                try:
                    cur_pattern = project.patterns[value]
                except KeyError:
                    project.patterns[value] = cur_pattern = Pattern()

            elif id == EventID.PatColor:
                cur_pattern.color = value

            elif id == EventID.PatControllers:
                if event.stream_len % 12 != 0:
                    warnings.warn("Pattern controller size not divisble by 12")
                    continue

                while stream.tell() < event.stream_len:
                    ctrl = PatternController()
                    ctrl.position = stream.read_I()  # 4
                    stream.seek(2, 1)  # 6
                    ctrl.channel = stream.read_B()  # 7
                    stream.seek(1, 1)  # 8
                    ctrl.value = stream.read_f()  # 12
                    cur_pattern.controllers.append(ctrl)

            elif id == EventID.PatName:
                cur_pattern.name = value

            elif id == EventID.PatNotes:
                if event.stream_len % 24 != 0:
                    warnings.warn("Pattern note size not divisible by 24.")
                    continue

                while stream.tell() < event.stream_len:
                    note = PatternNote()
                    note.position = stream.read_I()  # 4
                    note.flags = stream.read_H()  # 6
                    note.rack_channel = stream.read_H()  # 8
                    note.length = stream.read_I()  # 12
                    note.key = stream.read_I()  # 16
                    note.fine_pitch = stream.read_b()  # 17
                    stream.seek(1, 1)  # 18
                    note.release = stream.read_B()  # 19
                    note.midi_channel = stream.read_B()  # 20
                    note.pan = stream.read_b()  # 21
                    note.velocity = stream.read_B()  # 22
                    note.mod_x = stream.read_B()  # 23
                    note.mod_y = stream.read_B()  # 24
                    cur_pattern.notes.append(note)

            elif id == EventID.PlaylistData:
                if event.stream_len % 32 != 0:
                    warnings.warn("Playlist data size not divisible by 32.")
                    continue

                while stream.tell() < event.stream_len:
                    position = stream.read_I()  # 4
                    pattern_base = stream.read_H()  # 6
                    item_idx = stream.read_H()  # 8
                    length = stream.read_I()  # 12
                    _track_ridx = stream.read_i()  # 16

                    if project.version.major >= 20:
                        track_idx = 499 - _track_ridx
                    else:
                        track_idx = 198 - _track_ridx

                    stream.seek(2, 1)  # 18
                    item_flags = stream.read_H()  # 20
                    stream.seek(4, 1)  # 24
                    muted = (item_flags & 0x2000) > 0

                    if item_idx <= pattern_base:
                        start_offset = int(stream.read_f() * project.ppq)  # 28
                        end_offset = int(stream.read_f() * project.ppq)  # 32
                        for iid, channel in project.channels.items():
                            if iid == item_idx:
                                track_items[track_idx].append(
                                    ChannelPlaylistItem(
                                        position,
                                        length,
                                        start_offset,
                                        end_offset,
                                        muted,
                                        channel,
                                    )
                                )
                    else:
                        start_offset = stream.read_I()
                        end_offset = stream.read_I()
                        for idx, pattern in project.patterns.items():
                            if idx == item_idx - pattern_base - 1:
                                track_items[track_idx].append(
                                    PatternPlaylistItem(
                                        position,
                                        length,
                                        start_offset,
                                        end_offset,
                                        muted,
                                        pattern,
                                    )
                                )

            elif id == EventID.PlugColor:
                if parse_channel:
                    cur_channel.color = value
                else:
                    cur_slot.color = value

            elif id == EventID.PlugData:
                _plugin = None

                if parse_channel:
                    for _plugin_t, _event_t in {BooBass: BooBassEvent}.items():
                        if cur_channel.default_name == _plugin_t.DEFAULT_NAME:
                            event = _event_t(event._raw)
                            _plugin = cur_channel.plugin = _plugin_t()
                else:
                    for _plugin_t, _event_t in {
                        FruityBalance: FruityBalanceEvent,
                        FruityFastDist: FruityFastDistEvent,
                        FruityNotebook2: FruityNotebook2Event,
                        FruitySend: FruitySendEvent,
                        FruitySoftClipper: FruitySoftClipperEvent,
                        FruityStereoEnhancer: FruityStereoEnhancerEvent,
                    }.items():
                        if cur_slot.default_name == _plugin_t.DEFAULT_NAME:
                            event = _event_t(event._raw)
                            _plugin = cur_slot.plugin = _plugin_t()

                if _plugin is not None:
                    for _field in dataclasses.fields(_plugin):
                        setattr(_plugin, _field.name, event.props[_field.name])

            elif id == EventID.PlugDefaultName:
                if parse_channel:
                    cur_channel.default_name = value
                else:
                    cur_slot.default_name = value

            elif id == EventID.PlugIcon:
                if parse_channel:
                    cur_channel.icon = value
                else:
                    cur_slot.icon = value

            elif id == EventID.PlugName:
                if parse_channel:
                    cur_channel.name = value
                else:
                    cur_slot.name = value

            elif id == EventID.ProjArtists:
                project.artists = value

            elif id in (EventID.ProjComments, EventID._ProjRTFComments):
                project.comments = value

            elif id == EventID.ProjCurGroupId:
                try:
                    group = project.groups[value]
                except IndexError:
                    group = DisplayGroup("All")
                finally:
                    project.selection.group = group

            elif id == EventID.ProjCurPatIdx:
                cur_pattern_idx = value

            elif id == EventID.ProjDataPath:
                project.data_path = pathlib.Path(value)

            elif id == EventID._ProjFitToSteps:
                project.fit_to_steps = value

            elif id == EventID.ProjFLVersion:
                project.version = FLVersion(*list(map(int, value.split("."))))

            elif id == EventID.ProjGenre:
                project.genre = value

            elif id == EventID.ProjLoopActive:
                project.loop_active = value

            elif id == EventID.ProjLoopPos:
                project.selection.song_loop = value

            elif id == EventID.ProjPanLaw:
                project.pan_law = PanLaw(value)

            elif id == EventID.ProjPitch:
                project.main_pitch = value

            elif id == EventID.ProjPlayTruncatedNotes:
                project.play_truncated_notes = value

            elif id == EventID.ProjRegistered:
                project.registered = value

            elif id == EventID.ProjRegisteredTo:
                project.registered_to = value

            elif id == EventID.ProjShowInfo:
                project.show_info = value

            elif id == EventID.ProjSwing:
                project.swing = value

            elif id == EventID.ProjTempo:
                project.tempo = float(value / 1000)

            elif id == EventID.ProjTimeSigBeat:
                project.time_signature.beat = value

            elif id == EventID.ProjTimeSigNum:
                project.time_signature.num = value

            elif id == EventID.ProjTimestamp:
                project.created_on = DELPHI_EPOCH + timedelta(days=props["created_on"])
                project.work_time = timedelta(days=props["work_time"])

            elif id == EventID.ProjUrl:
                project.url = value

            elif id == EventID.ProjVerBuild:
                project.version_build = value

            elif id == EventID._ProjVolume:
                project.main_volume = value

            elif id == EventID.RemoteController:
                ctrl = RemoteController()
                if props["destination_data"] & 2000 == 0:
                    ctrl.parameter = props["parameter_data"] & 0x7FFF
                    ctrl.is_vst_param = props["parameter_data"] & 0x8000 > 0
                    channel_ctrls.append(ctrl)
                else:
                    insert = (props["destination_data"] & 0x0FF0) >> 6
                    slot = props["destination_data"] & 0x003F
                    slot_ctrls[insert][slot] = ctrl

            elif id == EventID.TMDenominator:
                cur_timemarker.denominator = value

            elif id == EventID.TMName:
                cur_timemarker.name = value

            elif id == EventID.TMNumerator:
                cur_timemarker.numerator = value

            elif id == EventID.TMPosition:
                if value > TimeMarkerType.Signature:
                    type = TimeMarkerType.Signature
                    position = value - TimeMarkerType.Signature
                else:
                    type = TimeMarkerType.Marker
                    position = value
                cur_timemarker = TimeMarker(position=position, type=type)
                cur_arrangement.timemarkers.append(cur_timemarker)

            elif id == EventID.TrackData:
                cur_track = Track(**props)
                cur_arrangement.tracks.append(cur_track)

            elif id == EventID.TrackName:
                cur_track.name = value

    except Exception as exc:
        if not dont_fail:
            raise EventParseError(event, event_idx) from exc
        project._is_dirty = True

    else:
        for channel in project.channels.values():
            for idx, child_iid in enumerate(channel.children):
                channel.children[idx] = project.channels[child_iid]

        for idx, pattern in project.patterns.items():
            if idx == cur_pattern_idx:
                project.selection.pattern = pattern

        for ins_idx, slot_dict in slot_ctrls.items():
            insert = project.inserts[ins_idx]
            for slot_idx, controllers in slot_dict.items():
                insert.slots[slot_idx].controllers = controllers

    return project
