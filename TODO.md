Here I keep my TODOs and issues. I remove them once they are solved/no longer a problem.

- Improve `FLObject.save()` method
- `Misc.start_date` parse logic raises **OverflowError**
- A more detailed **repr()** for `FLObject` subclasses
- Use the same event system used in other FLObjects for `Plugin` but make the `save()` method recombine it into a single event (Events inside event)
- Instead of creating objects in a single go, create them in multiple layers of parsing. I think this is what FL also does
- Test for verifying that the data chunk length == size of events
- Pattern controller events
- Saving an FLP back into a ZIP
- Using a color object for storing color properties
- Figure out remaining event IDs
- Use `_setprop()` override for `Track`
- Reduce the use of `# type: ignore`
- Fruity Notebook2 parsing code doesn't work, it caused infinite loops, however the latter has been fixed.
