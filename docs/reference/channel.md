## Channel

### ::: pyflp.channel.channel.Channel
    selection:
      members:
        - EventID
        - arp
        - au_sample_rate
        - children
        - color
        - cut_group
        - default_name
        - delay
        - enabled
        - env_lfos
        - filter_channel
        - fx
        - icon
        - index
        - kind
        - layer_flags
        - locked
        - level_offsets
        - levels
        - name
        - pan
        - plugin
        - polyphony
        - root_note
        - sample_path
        - sampler_flags
        - stretch_time
        - swing
        - target_insert
        - tracking_vol
        - tracking_key
        - use_loop_points
        - volume
        - zipped

## ChannelArp

!!! caution "Saving"
    This object doesn't implement property setters yet!

### ::: pyflp.channel.arp.ChannelArp
    selection:
      members:
        - direction
        - range
        - chord
        - repeat
        - time
        - gate
        - slide

## ChannelDelay

### Event information

Size: 20 (all 32 bit unsigned integers)

Structure:

| Parameter   | Offset |
| ----------- | ------ |
| feedback    | 0      |
| pan         | 4      |
| pitch_shift | 8      |
| echo        | 12     |
| time        | 16     |

### ::: pyflp.channel.delay.ChannelDelay
    selection:
      members:
        - echo
        - feedback
        - pan
        - pitch_shift
        - time

## ChannelEnvelopeLFO

### Event information

Size: 68 (per parameter; occurs 5x per channel)

Structure:

| Parameter    | Offset |
| ------------ | ------ |
| `__flags`    | 0      |
| enabled      | 4      |
| env_predelay | 8      |
| env_attack   | 12     |
| env_hold     | 16     |
| env_decay    | 20     |
| env_sustain  | 24     |
| env_release  | 28     |
| lfo_shape    | 52     |
| env_att_tns  | 56     |
| env_sus_tns  | 60     |
| env_rel_tns  | 64     |

!!! note
    `__flags` holds flags for `lfo_synced` and `lfo_retrig` properties.

!!! todo
    Some properties are yet to be discovered.

### ::: pyflp.channel.envlfo.ChannelEnvelopeLFO
    selection:
      members:
        - LFOShape
        - lfo_synced
        - lfo_retrig
        - enabled
        - env_predelay
        - env_attack
        - env_hold
        - env_decay
        - env_sustain
        - env_release
        - lfo_shape
        - env_att_tns
        - env_sus_tns
        - env_rel_tns


## ChannelLevelOffsets

### Event information

Size: 20 (all 32 bit signed integers)

Structure:

| Parameter    | Offset |
| ------------ | ------ |
| pan          | 0      |
| volume       | 8      |
| mod_x        | 12     |
| mod_y        | 16     |

::: pyflp.channel.level_offsets.ChannelLevelOffsets
    selection:
      members:
        - mod_x
        - mod_y
        - pan
        - volume

## ChannelLevels

### Event information

Size: 24 (all 32 bit signed integers)

Structure:

| Parameter    | Offset |
| ------------ | ------ |
| pan          | 0      |
| volume       | 4      |
| pitch_shift  | 8      |

!!! todo
    Some properties are yet to be discovered.

### ::: pyflp.channel.levels.ChannelLevels
    selectiom:
      members:
        - pan
        - pitch_shift
        - volume

## ChannelPolyphony

### Event information

Size: 9

Structure:

| Parameter | Offset | Type |
| --------- | ------ | ---- |
| max       | 0      | I    |
| slide     | 4      | I    |
| flags     | 8      | B    |

### ::: pyflp.channel.polyphony.ChannelPolyphony
    selection:
      members:
        - Flags
        - flags
        - max
        - slide

## ChannelTracking

### Event information

Size: 16 (all 32 bit signed integers)

Structure:

| Parameter    | Offset |
| ------------ | ------ |
| middle_value | 0      |
| pan          | 4      |
| mod_x        | 8      |
| mod_y        | 12     |

::: pyflp.channel.tracking.ChannelTracking
    selection:
      members:
       - middle_value
       - mod_x
       - mod_y
       - pan

## ChannelFX

### ::: pyflp.channel.fx.ChannelFX
    selection:
      members:
        - EventID
        - cutoff
        - fade_in
        - fade_out
        - pre_amp
        - reverb
        - resonance
        - stereo_delay

## ChannelFXReverb

### ::: pyflp.channel.fx.ChannelFXReverb
    selection:
      members:
        - kind
        - mix

## Filter

### ::: pyflp.channel.filter.Filter
    selection:
      members:
        - EventID
        - name
