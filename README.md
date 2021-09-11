# PyFLP
PyFLP creates an object from an FLP. You can edit it and save it back also. *Please don't use this for serious stuffs, I have done minimal testing myself and much of the features are yet to be implemented.*

It also has useful utilities like:
* Creating a ZIP looped package from an FLP

## Usage
```Python
from pyflp.parser import ProjectParser
project = ProjectParser().parse("/path/to/efelpee.flp")

# Use ProjectParser(verbose=True) if you want to see logs
```

## [More about FLP Format](doc/flp-format.md)

## [How does it work?](doc/how-does-it-work.md)

# Classes

## `Project`
The main entry point. Created by `ProjectParser().parse()`

```Python
misc: Misc
playlist: Playlist
patterns: List[Pattern]
filterchannels: List[FilterChannel]
channels: List[Channel]
arrangements: List[Arrangement]
timemarkers: List[TimeMarker]
tracks: List[Track]
inserts: List[Insert]
_unparsed_events: List[Event]
```

Below are brief descriptions of the classes used above

### `Misc`
Stores many one-time events like project Artists, Title, Tempo, Save timestamp etc. Most of the work here is done.

### `Pattern`
Represents a pattern. Only `index`, `name` and `color` properties are implemented.

### `Channel`
Represents a channel. This includes everything visible in Channel Rack. Automation, Samplers, plain audio clips, instruments are treated as a channel by FL. At this point many essential properties of a channel are implemented and a lot more are yet to be done. 

### `Insert`
Represents a mixer track ("Insert" from here on). Only `name`, `color`, `routing` and `flags` (properties like whether an `Insert` is docked to the middle, left or right, whether it is locked or not) are implemented yet. `InsertSlot`s are also stored in an `Insert`.

### `InsertSlot`
Represents a mixer track channel ("insert slot" from here on). Like `Insert` only few basic properties like `name`, `color` and `index` are implemented.

### Unparsed events
There are still many events which are not implemented. You can find them commented in one of the `*EventID` enums spread across the `FLObject` subclasses.

## Testing
I have created a [null test](tests/test_parser.py) and provided an empty FLP as well. However due to module import errors, I cannot get that test running :(

## Thanks

**Monad.FLParser**: https://github.com/monadgroup/FLParser for providing up-to-date parsing logic and the idea of creating an object model

**FLPEdit**: https://github.com/roadcrewworker I swear, this library would have remained a dream without this tool. A very helpful program for examining the event structure as it is present in an FLP and value of events. It is very unfortunate that the author has removed it.

## Contributions

If you can spare some time for testing and/or contributing, I would be very grateful. Please check the [TODO](../TODO) as well for current goals/issues. You can reach me at **demberto**[at]**protonmail**[dot]**com** as well :)