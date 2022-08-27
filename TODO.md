Here I keep my TODOs and goals. I remove them once they are solved/no
longer a problem. This is not a complete list, you can find many `# TODO`
comments all over the codebase.

## General goals

- There are many unknown properties in discovered events, discover their purpose.
- Figure out remaining event IDs.
- Instead of creating objects in a single go, create them in multiple layers
  of parsing. I think this is what FL also does.
- Automation! Although controllers have been implemented, a huge number of
  properties are yet to be discovered.

## Current TODOs

- Discover enums for `Channel.layer_flags` and `Channel.sampler_flags` and
  merge them both into `Channel.flags`.
- Group pattern notes by `Note.rack_channel` i.e. `Pattern.notes`
  should be of type `Dict[Channel, Note]`.
- Tests.
