Here I keep my TODOs, goals and issues. I remove them once they are solved/no
longer a problem. This is not a complete list, you can find many `# TODO`
comments all over the codebase.

## General goals

- There are many unknown properties in discovered events, discover their purpose.
- Figure out remaining event IDs.
- Instead of creating objects in a single go, create them in multiple layers
  of parsing. I think this is what FL also does.
- How about a separate parser class for `FLObject` subclasses? For e.g, `Misc`
  will just hold the properties and saving logic, parsing will be handled by
  `MiscParser` which can also hold some of the parsing logic from `Parser`.
- Automation! Although controllers have been implemented, a huge number of
  properties are yet to be discovered.

## Current TODOs

- Saving an FLP back into a ZIP.
- Use the same event system used in other FLObjects for `Plugin` but make the
  `save()` method recombine it into a single event (Events inside event).
- Discover enums for `Channel.layer_flags` and `Channel.sampler_flags`.
- Merge `Channel.layer_flags` and `Channel.sampler_flags` into `Channel.flags`.
  Needs a custom getter and parsing logic.
- Group pattern notes by `Note.rack_channel` i.e. `Pattern.notes` should be of
  type `Dict[int, Note]`.
- `VSTPluginEvent` is a mess, clean it up.
