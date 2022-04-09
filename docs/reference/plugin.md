# Plugin

::: pyflp.plugin._plugin._Plugin

## VSTPlugin

!!! info
    A `VSTPlugin` event has events inside it. Their structure is as follows:

    | Name | Type | Offset |
    | ---- | ---- | ------ |
    | id   | B    | 0      |
    | size | Q    | 1      |
    | data | N.A  | 9      |

    This event is implemented by `_QWordVariableEvent`.


::: pyflp.plugin.vst.VSTPlugin
    selection:
      members:
        - flags
        - fourcc
        - guid
        - midi_in_port
        - midi_out_port
        - name
        - pitch_bend_range
        - plugin_path
        - state
        - vendor
        - vst_number

## Native effects

### Fruity Balance

::: pyflp.plugin.effects.balance.FBalance
    selection:
      members:
        - pan
        - volume

### Fruity Soft Clipper

::: pyflp.plugin.effects.soft_clipper.FSoftClipper
    selection:
      members:
        - post_gain
        - threshold

### Fruity Stereo Enhancer

::: pyflp.plugin.effects.stereo_enhancer.FStereoEnhancer
    selection:
      members:
        - pan
        - volume
        - stereo_separation
        - phase_offset
        - phase_inversion
        - effect_position

### Soundgoodizer

::: pyflp.plugin.effects.soundgoodizer.Soundgoodizer
    selection:
      members:
        - amount
        - Mode
        - mode

### Fruity Notebook 2

::: pyflp.plugin.effects.notebook2.FNoteBook2
    selection:
      members:
        - active_page
        - editable
        - pages

### Fruity Send

::: pyflp.plugin.effects.send.FSend
    selection:
      members:
        - dry
        - pan
        - volume
        - send_to

### Fruity Fast Dist

::: pyflp.plugin.effects.fast_dist.FFastDist
    selection:
      members:
        - pre
        - threshold
        - kind
        - Kind
        - mix
        - post

## Native synths

### BooBass

::: pyflp.plugin.synths.boobass.BooBass
    selection:
      members:
        - bass
        - mid
        - high
