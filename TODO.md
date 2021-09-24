* `Misc.start_date` parse logic raises **OverflowError**
* **repr()** for `FLObject` subclasses
* `max_count` - required or not?
* Use the same event system used in other FLObjects for `Plugin` but make the `save()` method recombine it into a single event (Events inside event)
* Instead of creating objects in a single go, create them in multiple layers of parsing. I think this is what FL also does
* `PatternEventID.New` event occurs twice, doesn't get dumped twice as parsing logic replaces previous instance when it occurs 2nd time
* Test for verifying that the data chunk length == size of events
* `Project.save()` must check for changed to certain `Misc` properties, which cannot be set by `Misc` itself as they are not events.
* Pattern controller events