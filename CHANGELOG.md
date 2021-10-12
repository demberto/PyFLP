# 0.2.0 Inital release

## **Highlights**

- **PyFLP has passed the null test for a full project of mine (FL 20.7.2) 🥳**
- This library uses code from [FLParser](https://github.com/monadgroup/FLParser), a GPL license project, PyFLP is now under GPL
- API reference documentation is complete now
- Few new events implemented for `Channel`
- Refactored `FLObject` and `Plugin`

## `FLObject` refactoring

- `parseprop` is now `_parseprop`
- All `_parseprop` delegates are now "protected" as well
- `setprop` is now `_setprop`

## Additions

- `ChannelEvent.Delay` is implemented by `ChannelDelay` and `Channel.delay`
- `Event.to_raw` and `Event.dump` now log when they are called
- [Exceptions](https://github.com/demberto/PyFLP/tree/master/exceptions.py) `DataCorruptionDetected` and `OperationNotPermitted`

## Bug Fixes

- Can definitely say, all naming inconsistencies have been fixed
- Fixed `TimeMarker` assign to `Arrangement` logic in `Parser`
- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, caused due to double dumping of same events
- Empty pattern events, `PatternEvent.Name` and `PatternEvent.Color` don't get saved

---

**❗ These versions below don't work due to naming inconsistencies 😅, you will not find them 👇**

# 0.1.2

## Additions

- More docs
- Add some new properties/events to `Channel`
- A sample [empty FLP]("tests/assets/FL 20.8.3/Empty.flp") has been provided to allow running tests
- All `FLObject` subclasses now have a basic `__repr__` method

## Bug fixes

- Improve the GitHub workflow action, uploads to PyPI will not happen unless the test is passed
- ~~Fix all naming inconsistencies caused due to migration to [`BytesIOEx`](https://github.com/demberto/BytesIOEx)~~ Not all

## Known issues

Same as in 0.1.1

# 0.1.1

~~The first version of PyFLP that works correctly 🥳~~ No, unfortunately

## **Highlights**

- Changed documentation from Sphinx to MkDocs
- [FLPInfo](https://github.com/demberto/FLPInfo) is now a separate package
- [FLPInspect](https://github.com/demberto/FLPInspect) is now a separate package
- PyFLP now uses [BytesIOEx](https://github.com/demberto/BytesIOEx/) as an external dependency

## Bug Fixes

- `ByteEvent`, `WordEvent` and `DWordEvent` now raise a `TypeError`
  when they are initialised with the wrong size of data
- Fix setup.cfg, project structure is now as expected, imports will work
- [Docs](https://pyflp.rtfd.io/) are now up and running

## Known issues

- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, why this is caused is not known

---

**❗ These versions below don't work because I didn't know how to configure `setup.cfg` properly 😅**

# 0.1.0

## **Highlights**

- `flpinspect` - An FLP Event Viewer made using Tkinter.
- `flpinfo` - A CLI utility to get basic information about an FLP.
- Switched to MIT License

## Additions

- Lots of changes, refactoring and code cleanup of `pyflp`
- New docs
- Changes to `README`
- Adopted [`black`](https://github.com/psf/black) coding style
- Added a `log_level` argument to `Parser`
- `Project.create_zip` copies stock samples as well now
- `Project.get_events` for getting just the events; they are not parsed
  Read [docs](https://pyflp.rtfd.io) for more info about this
- `Event` classes now have an `__eq__` and `__repr__` method

## Bug fixes

- Tests don't give module import errors
- `Pattern` event parsing
- Initialise `_count` to 0, everytime `Parser` is initialised
- `Project.create_zip` now works as intended
- Overhauled logging
- A lot of potential bugs in `FLObject` subclasses

## Known issues

- `flpinfo` doesn't output correctly sometimes due to long strings
- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, why this is caused is not known

---
