### PyFLP

- `Misc.start_date` parse logic raises **OverflowError**
- **repr()** for `FLObject` subclasses
- Use the same event system used in other FLObjects for `Plugin` but make the `save()` method recombine it into a single event (Events inside event)
- Instead of creating objects in a single go, create them in multiple layers of parsing. I think this is what FL also does
- Test for verifying that the data chunk length == size of events
- Pattern controller events
- `_count` variables being static become useless when `Parser` is reinitalised
- Switch over to [`BytesIOEx`](https://github.com/demberto/bytesioex)
- First pattern doesn't get a name after saving
- Saving an FLP back into a ZIP
- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, why this is caused is not known

### FLPInspect

- Progress bar
- Fix high CPU usage
- Support event editing
- Warnings and errors are ignored by `GUIHandler` if verbose mode is not enabled
- Tooltips are a mess
- Tests

### FLPInfo

- Long comments cause incorrect formatting
- Tests
