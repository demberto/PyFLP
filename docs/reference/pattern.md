# Pattern

::: pyflp.pattern.pattern.Pattern
    selection:
      members:
        - EventID
        - color
        - index
        - name
        - notes
        - is_empty

# PatternNote

::: pyflp.pattern.note.PatternNote
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

# PatternController

::: pyflp.pattern.controller.PatternController
    selection:
      members:
        - position
        - target_channel
        - target_flags
        - value
