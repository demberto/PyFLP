# PyFLP

PyFLP creates an object from an FLP. You can edit it and save it back also. *Please don't use this for serious stuffs, I have done minimal testing myself and much of the features are yet to be implemented.*

## Usage
```Python
from pyflp.parser import ProjectParser
project = ProjectParser().parse("/path/to/efelpee.flp")

# Use ProjectParser(verbose=True) if you want to see logs
```

## More about FLP format
FLP uses events to store its data. Unlike JSON and XML where data is already stored like an object, converting this bulk of data into a proper object model gets quite tricky. FLP events are chunks of data which are of the structure:

```Python
event_id    # [1 byte unsigned integer] For classification of the type of event
length      # [varint - size >= 1] Used by variable sized events to store length of data
data        # [size, type depends on id] Either a fixed size event or a variable sized event 
```

*where type of `data` is decided by*

```Python
if event_id in range(0, 64):
    data.size = 1       # Hence event size = 2 ("ByteEvent" from here on)
elif event_id in range(64, 128):
    data.size = 2       # Hence event size = 3 ("WordEvent" from here on)
elif event_id in range(128, 192):
    data.size = 2       # Hence event size = 5 ("DWordEvent" from here on)
else:
    # data.size is stored next to event_id as a a varint, so the parser
    # knows how much bytes to read: ("TextEvent" for strings and
    # "DataEvent" for the rest from here on).
```

Variable-sized events are used for storing strings or a blob of a collection of various simple types like `int`, `bool`, `float` etc. Since `event_id` can hold only 256 different values, it is easier to use just a single `event_id` > 192 and store all sorts of data in it without worrying a lot about size and event ID space.

As newer features get introduced, many times IL just adds more data at the end of an existing `DataEvent`, making for e.g. a 62 byte event in FL 20 to a 66 byte event in a later version.

## `Project`
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

## `Misc`
Stores many one-time events like project Artists, Title, Tempo, Save timestamp etc. Most of the work here is done.

## `Pattern`
Represents a pattern. Only `index`, `name` and `color` properties are implemented.

## `Channel`
Represents a channel. This includes everything visible in Channel Rack. Automation, Samplers, plain audio clips, instruments are treated as a channel by FL. At this point many essential properties of a channel are implemented and a lot more are yet to be done. 

## `Insert`
Represents a mixer track ("Insert" from here on). Only `name`, `color`, `routing` and `flags` (properties like whether an `Insert` is docked to the middle, left or right, whether it is locked or not) are implemented yet. Implementing the rest in this kind of parser is kinda difficult (explained below). `InsertSlot`s are also stored in an `Insert`.

## `InsertSlot`
Represents a mixer track channel ("insert slot" from here on). Like `Insert` only few basic properties like `name`, `color` and `index` are implemented (explained below).

## FAQ
### Why are some `Insert` and `InsertSlot` properties hard to implement?
A majority of the properties of `Insert` and `InsertSlot`, for e.g. send volumes, post-EQ settings, insert/insert slot enabled state and volume is stored in a single event at the *almost* end of an FLP after the entire mixer is dumped. This is quite a different approach used by IL, and parsing these properties is not as difficult as making them editable *which is my goal, as other libraries exist for reading the object structure or editing the event structure*.

## Thanks

Monad.FLParser: https://github.com/monadgroup/FLParser for providing up-to-date parsing logic and the idea of creating an object model

FLPEdit: https://github.com/roadcrewworker I swear, this library would have remained a dream without this tool. A very helpful program for examining the event structure as it is present in an FLP and value of events. It is very unfortunate that the author has removed it.

## Contributions

If you can spare some time for testing and/or contributing, I would be very grateful . You can reach me at **demberto**[at]**protonmail**[dot]**com** as well :)