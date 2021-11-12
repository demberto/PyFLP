# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### **Highlights**

- The entire module hierarchy of PyFLP has been simplified.
- Internal/abstract base classes have bee renamed to start with _.
- `repr` for `_FLObject` subclasses.
- The way properties are handled is now completely changed.
- Data events get parsed by a `DataEvent` subclass.
- Way better testing, with a coverage of whooping 79%.
- `color` properties now return a `colour.Color` object.
- Almost everything has a docstring now, even enum members.
- PyFLP has adopted Contributor Covenant Code of Conduct v2.1.

### Changed

- All `_FLObject` subclasses have been moved to parent `pyflp/` from `pyflp/flobject/` to ease import names.
- All `Event` subclasses have been moved in a single `event.py` and `event/` folder is removed.
- All event ID enum names are now inner classes of `_FLObject` subclasses.
- Constructor of `Project` has been simplified.
- `VSTPlugin`'s underlying event now supports saving, it has been refactored out of `_parse_data_event` also.
- `InsertParametersEvent` to replace the equivalent parsing in `Insert._parse_data_event`.
- The [TODO](https://github.com/demberto/PyFLP/blob/master/TODO.md) has been changed to reflect the type of goals.
- `_FLObject.save` is now `_FLObject._save`.
- Some constants present in `utils.py` have been moved to `constants.py`.
- Docs include a brief summary of the underlying data event wherever applicable.
- Minor property name changes; made them more concise.

### Added

- `__repr__()` for all `_FLObject` subclasses.
- `Channel.color`, `Insert.color` and `Pattern.color` now return `colour.Color`. This is implemented by `ColorEvent` (_which subclasses `DWordEvent`_).
- New event implementations for `ChannelFX.EventID` (`Cutoff`, `Fadein`, `Fadeout` and more).
- New event implementations for `Channel.EventID` (`ChannelTracking`, `ChannelLevels`, `ChannelLevelOffsets`, `ChannelPolyphony` and more).
- `Channel.cut_group` implementing `Channel.EventID.CutSelfCutBy`.
- Remote controllers (`RemoteController`). Accessible from `Project.controllers`.
- Saving for `VSTPlugin`.
- All enum members used by `FLObject` subclasses now have a docstring.
- Added links in docstrings to official FL Studio Manual wherever possible.
- `Parser.__build_event_store()` uses inner methods now to parse different kind of events; very helpful for the new `DataEvents`.
- Added support for pattern controller events (`PatternController`, `PatternControllerEvent` who implement `PatternEventID.Controllers`).
- Many attribute docstrings now include minimum, maximum and default values. **These limits are enforced by setters**.
- Added `.editorconfig`, _using CRLF line endings btw_.
- Added `test_parser.py` and `test_events.py`.
- `Parser.parse_zip` now accepts a `bytes` object for `zip_file` parameter.
- `Misc.registered` for `Misc.EventID.Registered`.

### Fixed

- `ChannelFXReverb` was not getting initialised.
- `InsertParamsEvent` was not getting initialised.
- Syntax is highlighted in the [docs](https://pyflp.rtfd.io/) as expected now.
- `FNotebook2` text parsing.
- `Insert.routing` returned `True` for all tracks.
- `Misc.start_date` and `Misc.work_time` parsing.

### Removed

- Submodule `__init__.py` files, absolute imports are used everywhere.
- Any and all sort of logging, not useful anymore. Haven't seen any 3rd party python library ever using it. Used `warnings` wherever necessary.
- `mypy`. Its useless tbh, I will use types as I see fit.
- Setters for all properties containing `_FLObject` (or any sort of a collection of them), _e.g. Arrangement.tracks_.

## [0.2.0]

### **Highlights**

- **PyFLP has passed the null test for a full project of mine (FL 20.7.2) 🥳**
- This library uses code from [FLParser](https://github.com/monadgroup/FLParser), a GPL license project, PyFLP is now under GPL
- API reference documentation is complete now
- Few new events implemented for `Channel`
- Refactored `FLObject` and `Plugin`

#### `FLObject` refactoring

- `parseprop` is now `_parseprop`
- All `_parseprop` delegates are now "protected" as well
- `setprop` is now `_setprop`

### Added

- `ChannelEvent.Delay` is implemented by `ChannelDelay` and `Channel.delay`
- `Event.to_raw` and `Event.dump` now log when they are called
- [Exceptions](https://github.com/demberto/PyFLP/tree/master/exceptions.py) `DataCorruptionDetected` and `OperationNotPermitted`

### Fixed

- Can definitely say, all naming inconsistencies have been fixed
- Fixed `TimeMarker` assign to `Arrangement` logic in `Parser`
- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, caused due to double dumping of same events
- Empty pattern events, `PatternEvent.Name` and `PatternEvent.Color` don't get saved

---

**❗ These versions below don't work due to naming inconsistencies 😅, you will not find them 👇**

## [0.1.2]

### Added

- More docs
- Add some new properties/events to `Channel`
- A sample [empty FLP]("tests/assets/FL 20.8.3/Empty.flp") has been provided to allow running tests
- All `FLObject` subclasses now have a basic `__repr__` method

### Fixed

- Improve the GitHub workflow action, uploads to PyPI will not happen unless the test is passed
- ~~Fix all naming inconsistencies caused due to migration to [`BytesIOEx`](https://github.com/demberto/BytesIOEx)~~ Not all

### Known issues

Same as in 0.1.1

## [0.1.1]

~~The first version of PyFLP that works correctly 🥳~~ No, unfortunately

### **Highlights**

- Changed documentation from Sphinx to MkDocs
- [FLPInfo](https://github.com/demberto/FLPInfo) is now a separate package
- [FLPInspect](https://github.com/demberto/FLPInspect) is now a separate package
- PyFLP now uses [BytesIOEx](https://github.com/demberto/BytesIOEx/) as an external dependency

### Fixed

- `ByteEvent`, `WordEvent` and `DWordEvent` now raise a `TypeError`
  when they are initialised with the wrong size of data
- Fix setup.cfg, project structure is now as expected, imports will work
- [Docs](https://pyflp.rtfd.io/) are now up and running

### Known issues

- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, why this is caused is not known

---

**❗ These versions below don't work because I didn't know how to configure `setup.cfg` properly 😅**

# 0.1.0

## **Highlights**

- `flpinspect` - An FLP Event Viewer made using Tkinter.
- `flpinfo` - A CLI utility to get basic information about an FLP.
- Switched to MIT License

## Added

- Lots of changes, refactoring and code cleanup of `pyflp`
- New docs
- Changes to `README`
- Adopted [`black`](https://github.com/psf/black) coding style
- Added a `log_level` argument to `Parser`
- `Project.create_zip` copies stock samples as well now
- `Project.get_events` for getting just the events; they are not parsed
  Read [docs](https://pyflp.rtfd.io) for more info about this
- `Event` classes now have an `__eq__` and `__repr__` method

## Fixed

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

[1.0.0]: https://github.com/demberto/PyFLP/releases/tag/0.2.0
[0.2.0]: https://github.com/demberto/PyFLP/releases/tag/0.2.0
[0.1.2]: https://github.com/demberto/PyFLP/releases/tag/0.1.2
[0.1.1]: https://github.com/demberto/PyFLP/releases/tag/0.1.1
