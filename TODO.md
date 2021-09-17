* `Misc.start_date` parse logic raises **OverflowError**
* **repr()** for `FLObject` subclasses
* `max_count` - required or not?
* Use the same event system used in other FLObjects for `Plugin` but make the `save()` method recombine it into a single event
* Instead of creating objects in a single go, create them in multiple layers of parsing. I think this is what FL also does
* `TimeMarker` events not getting dumped
* `PatternEventID.New` event occurs twice, doesn't get dumped twice as parsing logic replaces previous instance when it occurs 2nd time
* Test for verifying that the data chunk length == size of events