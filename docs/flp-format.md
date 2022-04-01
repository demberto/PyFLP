# FLP Format

FLP uses a [TLV](https://en.wikipedia.org/wiki/Type%E2%80%93length%E2%80%93value)
encoding scheme to store its data. Unlike JSON and XML where data is already
stored like an object, converting this bulk of data into a proper object model
gets quite tricky.

Structure of an FLP event

| Field    |        Size         | Notes                                    |
| :------- | :-----------------: | :--------------------------------------- |
| event_id |          1          | For classification of the type of event. |
| length   |       varint        | Used only by `TextEvent` and `DataEvent` |
| data     | 1, 2, 4 or `length` | Size decided by `event_id` (see below)   |

_where size of `data` is decided by_

| `event_id` |   Size   | Notes        |
| :--------: | :------: | ------------ |
|    0-63    |    1     | `ByteEvent`  |
|   63-127   |    2     | `WordEvent`  |
|  128-191   |    4     | `DWordEvent` |
|  192-207   | `length` | `TextEvent`  |
|  208-255   | `length` | `DataEvent`  |

Variable-sized events (`TextEvent` and `DataEvent`) are used for storing
strings or a blob of a collection of various simple types like `int`, `bool`,
`float` etc. Since `event_id` can hold only 256 different values, it is easier
to use just a single `event_id` > 192 and store all sorts of data in it without
worrying a lot about size and event ID space.

!!! note "DataEvents"
    As newer features get introduced, many times IL just adds more data at the
    end of an existing `DataEvent`, making for e.g. a 62 byte event in FL 20
    to a 66 byte event in a later version.
