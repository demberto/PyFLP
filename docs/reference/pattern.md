## Pattern

::: pyflp.pattern.pattern.Pattern
    selection:
      members:
        - EventID
        - color
        - index
        - name
        - notes
        - is_empty

## PatternNote

### Event information

Size: A divisible of 24.

!!! attention
    This event wasn't always a divisible of 24.
    I found a FL 3.0.0 file where it is a divisible of 20.

Structure:

| Parameter    | Offset | Type |
| ------------ | ------ | ---- |
| position     | 0      | I    |
| flags        | 4      | H    |
| rack_channel | 6      | H    |
| duration     | 8      | I    |
| key          | 12     | I    |
| fine_pitch   | 16     | b    |
| *unknown*    | 17     |      |
| release      | 18     | B    |
| midi_channel | 19     | B    |
| pan          | 20     | b    |
| velocity     | 21     | B    |
| mod_x        | 22     | B    |
| mod_y        | 23     | B    |

### ::: pyflp.pattern.note.PatternNote
    selection:
      members:
        - duration
        - fine_pitch
        - flags
        - midi_channel
        - key
        - mod_x
        - mod_y
        - pan
        - position
        - rack_channel
        - release
        - velocity

## PatternController

### Event information

Size: A divisible of 12.

Structure:

| Parameter      | Offset | Type |
| -------------- | ------ | ---- |
| position       | 0      | I    |
| *unknown*      | 4      |      |
| *unknown*      | 5      |      |
| target_channel | 6      | B    |
| target_flags   | 7      | B    |
| value          | 8      | f    |

### ::: pyflp.pattern.controller.PatternController
    selection:
      members:
        - position
        - target_channel
        - target_flags
        - value
