# FLP Format

FLP uses a [TLV](https://en.wikipedia.org/wiki/Type%E2%80%93length%E2%80%93value)
encoding scheme to store its data. Unlike JSON and XML where data is already
stored like an object, converting this bulk of data into a proper object model
gets quite tricky.

Structure of an FLP event

| Field    |        Size         | Notes                                        |
| :------- | :-----------------: | :------------------------------------------- |
| event_id |          1          | For classification of the type of event.     |
| length   |       varint        | Used only by string and custom data events.  |
| data     | 1, 2, 4 or `length` | Size decided by `event_id` (see below)       |

_where size of `data` is decided by_

| `event_id` |   Size   | Implemented by                                        |
| :--------: | :------: | ----------------------------------------------------- |
|    0-63    |    1     | `U8Event`, `I8Event`, `BoolEvent`                     |
|   63-127   |    2     | `U16Event`, `I16Event`                                |
|  128-191   |    4     | `U32Event`, `I32Event`, `U16TupleEvent`, `ColorEvent` |
|  192-255   | `length` | `AsciiEvent`, `UnicodeEvent`, `DataArrayEvent`, etc.  |
