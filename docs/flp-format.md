# FLP Format

FLP uses events to store its data. Unlike JSON and XML where data is already stored like an object, converting this bulk of data into a proper object model gets quite tricky. FLP events are chunks of data which are of the structure:

```Python
event_id    # [1 byte unsigned integer] For classification of the type of event
length      # [varint - size >= 1] Used by variable sized events to store length of data
data        # [size, type depends on id] Either a fixed size event or a variable sized event 
```

*where type of `data` is decided by*

```{code-block} python
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