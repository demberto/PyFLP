<!-- markdownlint-disable no-duplicate-heading -->
<!-- markdownlint-disable link-image-reference-definitions -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2023-05-24

### Changed

- Refactored `VSTPluginEvent` sub-event handling into `_VSTPluginProp`.
- All `VSTPluginEvent` string sub-events decoded as UTF8.

### Fixed

- `VSTPlugin.name` encoded in UTF8 [#150].

[#150]: https://github.com/demberto/PyFLP/issues/150

## [2.1.0] - 2023-04-18

### Added

- Plugin data parsers: `FruitKick` and `Plucked`.
- `ArrangementsID.PLSelection` [#132].

### Changed

- Unbound descriptors return `self` - more `property`*esque* behaviour.
  This is primarily done to allow `flpinspect` to inspect descriptor types.
- Moved `Sampler.pitch_shift` upto its base class `_SamplerInstrument`.

### Deprecated

- `ArrangementID.LoopPos` [#132].

[#132]: https://github.com/demberto/PyFLP/issues/132

## [2.0.0] - 2023-03-18

Welcome PyFLP 2.0 🎉
Read the previous changelogs to get the complete list of changes.

### Added

- `FruityBloodOverdrive` - thanks to @@ttaschke [#120].

### Changed

- Docs are way more easier to navigate now.

### Fixed

- `VSTPluginEvent.__setitem__` and `_VSTPluginProp._set` [#113].

### Removed

- Support for PyPy 3.7 (unable to run tox, cannot find a download).

[#113]: https://github.com/demberto/PyFLP/issues/113
[#120]: https://github.com/demberto/PyFLP/pull/120

## [2.0.0a7] - 2022-12-19

### Added

- `Pattern` timemarkers [#27].
- Low-level API support for FL Studio 21's `PlaylistEvent` [#108].

### Changed

- Renamed `PlaylistEvent.track_index` to `PlaylistEvent.track_rvidx`.
- Optimized `Arrangement.tracks` iteration logic - 50% lesser time to run tests.
- `StructEventBase.value` raises `NotImplementedError`.
- Ambiguous `Pattern.__iter__` refactored into a property `Pattern.notes`.
- `Pattern.index` renamed to `Pattern.iid`.
- Improved `__repr__` strings; replaced with `ModelReprMixin` at some places
  use `__str__` for a more human readable representation.

### Fixed

- `Patterns.__getitem__` didn't work with pattern names as documented.

### Removed

- Ambiguous `__index__` methods from a bunch of model classes.
- Unimplemented `Slot.controllers`.

[#27]: https://github.com/demberto/PyFLP/issues/27
[#108]: https://github.com/demberto/PyFLP/issues/108

## [2.0.0a6] - 2022-11-19

### Added

- `Keyboard.main_pitch`, `Keyboard.add_root`, `Keyboard.key_region` [#92].
- `Sampler.filter` and `Filter` [#99].

### Changed

- `Channel.group` becomes a read-only property (modify event to change channel group).
- `PLItemBase.offsets` and its fields in `PlaylistEvent` are [float32](https://stackoverflow.com/a/74247360/)
  Thanks to `chrslg` from Stackoverflow and @jubabrut.
- `Track.height` returns an `str` of its percentage e.g. `100%`.
- `Instrument.plugin` and `Slot.plugin` return `_PluginBase` for unimplemented
  native plugins [#102].
- Reimplemented `EventTree` to use a list and got a 10+% perf boost in unit tests.

### Fixed

- `Channel.group` remained unitialised [#100].
- `Chanel.plugin` failed due to base class type parameter check [#101].

### Removed

- `Track.locked_height` as what this quantity stores is unknown to me yet.
- Use of fixture factories in unittests [#74].

[#74]: https://github.com/demberto/PyFLP/issues/74
[#92]: https://github.com/demberto/PyFLP/issues/92
[#99]: https://github.com/demberto/PyFLP/issues/99
[#100]: https://github.com/demberto/PyFLP/issues/100
[#101]: https://github.com/demberto/PyFLP/issues/101
[#102]: https://github.com/demberto/PyFLP/issues/102

## [2.0.0a5.post] - 2022-10-31

### Changed

- Upgrade `construct-typing` to 0.5.3.

## [2.0.0a5] - 2022-10-28

### Added

- Implementation for `Channel` and `Pattern` playlist items [#84].
- `FX.remove_dc`, `FX.trim`, `FX.fix_trim`, `FX.crossfade`,
  `FX.length`, `FX.normalize`, `FX.inverted`, `FX.start` [#55].
- Normalized linear values for certain properties, more user friendly to deal with.
  The required encode / decode is done at event level itself.
- `TimeStretching.time`, `TimeStretching.pitch`, `TimeStretching.multiplier` [#87].
- (Undiscovered) `MIDIControllerEvent`.
- `Delay.mod_x`, `Delay.mod_y`, `Delay.fat_mode` and `Delay.ping_pong` [#88].
- Improve enum performance by using `f-enum` library (`pyflp.parse` is 50% faster).
- `Time.gate`, `Time.shift` and `Time.full_porta` [#89].
- *Experimental* Python 3.11 support is back.
- A shit ton of flags in `VSTPlugin` and refactoring [#95].
- `WrapperEvent.page`, `WrapperEvent.height`, `WrapperEvent.width` [#93].
- `ItemModel.__setitem__` propagates back changes to owner event [#97].

### Changed

- `PlaylistItemBase.offsets` now returns start and end offsets.
- Use git commit for `construct-typing` which has fixed certain bugs.
- Rename `PlaylistItemBase` to `PLItemBase` and `PatternPlaylistItem` to `PatternPLItem`.
- Rename `Polyphony` members `is_mono` to `mono` and `is_porta` to `porta`.
- `NoModelsFound` also bases `LookupError` now.
- Compiled `VSTPluginEvent.STRUCT`.

### Fixed

- `EventTree.divide` fails to yield the only element [#90].
- `TrackID.Name` events were grouped instead of getting divided [#96].
- `PropBase.__set__` always raises `PropertyCannotBeSet` [#97].

### Removed

- `PlaylistItemBase.start_offset` and `PlaylistItemBase.end_offset`.
- Redundant exceptions `ExpectedValue`, `UnexpectedType`.
- Undiscovered `num_inputs`, `num_outputs` and `vst_number` from `VSTPlugin`.

[#55]: https://github.com/demberto/PyFLP/issues/55
[#84]: https://github.com/demberto/PyFLP/issues/84
[#87]: https://github.com/demberto/PyFLP/issues/87
[#88]: https://github.com/demberto/PyFLP/issues/88
[#89]: https://github.com/demberto/PyFLP/issues/89
[#90]: https://github.com/demberto/PyFLP/issues/90
[#93]: https://github.com/demberto/PyFLP/issues/93
[#95]: https://github.com/demberto/PyFLP/issues/95
[#96]: https://github.com/demberto/PyFLP/issues/96
[#97]: https://github.com/demberto/PyFLP/issues/97

## [2.0.0a4] - 2022-10-22

The way models were passed events has changed. I designed a new data structure
called `EventTree` (check `pyflp._events`) to allow the insertion and
deletion of events like a list while preserving the speed of a dict lookups.

Sounds *awfully* like `multidict` except that it doesn't allow mutable views.
`EventTree` knows its parents and any attempt to insert or delete an event
from it will also affect its parents *and vice-versa*. Took quite some to do.

`EventTree` will allow for insertion / removal of events when corresponding
descriptor setters / deleters (yet to implement) are invoked. This can allow
for wonderful things like creating new channels, moving inserts etc.

### Added

- A multidict with mutable dict view `EventTree`.
- PyPy 3.7+ support [#77].
- Slicing for ModelBase collections [#31].
- Fruity Center parser [#42].
- Dependency on `sortedcontainers` library for `EventTree`.
- Remaining and some new images for docstrings [#47].
- GUI locations of descriptors (w.r.t. FL 20.8.4) [#80].

### Changed

- Simplified some `__repr__` strings.
- Event IDs are all `EventEnum` members (better repr-strings).
- PyFLP is guaranteed to be not thread-safe.
- Moved up `Sampler.cut_group` to `_SamplerInstrument`.

### Fixed

- `ModelReprMixin`.

### Removed

- `Track.index` in favour of the redundant `Track.__index__`.
- `Track.items`. Iterate over a track, to get them now.
- Subclassing of protocol classes keeping [PEP544] in mind [#50].
- Models are no longer hashable as events were made unhashable previously.
- Commented out currently unimplemented `Channel.controllers`.

[#31]: https://github.com/demberto/PyFLP/issues/31
[#42]: https://github.com/demberto/PyFLP/discussions/42
[#47]: https://github.com/demberto/PyFLP/issues/47
[#50]: https://github.com/demberto/PyFLP/issues/50
[#77]: https://github.com/demberto/PyFLP/issues/77
[#80]: https://github.com/demberto/PyFLP/issues/80
[PEP544]: https://peps.python.org/pep-0544

## [2.0.0a3] - 2022-10-08

### Added

- 100% mypy tested *for all you mypy geeks*. It makes me play cat-and-mouse.
- `Automation` points and LFO, via [#29].

### Changed

- All `StructBaseEvent` classes overhauled to use the `construct` library.
- `EventBase.__len__` is now `EventBase.size`, a property.
- Shift all subclass event parsing to `PODEventBase`.
- Replace all uses of `bytesioex` with equivalents from `construct`.
- Struct definitions moved to `StructEventBase` itself.
- Enums used in structs directly now inherit from `construct_typed.EnumBase`.
- `LFO` renamed to `SamplerLFO` to be distinguishable from `AutomationLFO`.

### Fixed

- `InsertEQ` was't working [#46].
- Negative `FileFormat` weren't being read.
- Incorrect event size calculation in `StructEventBase` [#72].
- `Pattern.__repr__` failed for empty patterns.

### Removed

- `_StructMeta` (voodoo magic) and `StructBase` from `pyflp._events`.
- `SoundgoodizerMode`, `FruityFastDistKind`, `StereoEnhancerInvertPosition`,
  `StereoEnhancerEffectPosition` from `pyflp.plugin` in favour of equivalent
  string literals.
- Protocol subclassing of `EventBase` hierarchy.
- Faulty `EventBase.__hash__`.
- Python 3.11 support due to <https://github.com/timrid/construct-typing/issues/15>
- Incomplete support for `Sequence` in model collections.

[#29]: https://github.com/demberto/PyFLP/issues/29
[#46]: https://github.com/demberto/PyFLP/issues/46
[#72]: https://github.com/demberto/PyFLP/issues/72

## [2.0.0a2] - 2022-10-01

### Added

- `FX.clip`, `FX.fade_stereo`, `FX.freq_tilt`, `FX.pogo`, `FX.ringmod`,
  `FX.swap_stereo` & `FX.reverse` [#55].
- `TimeStretching.mode` and `StretchMode` [#56].
- `Playback.start_offset` [#57].
- `Content.declick_mode` and `DeclickMode` [#58].
- User guide and contibutor's guide.
- Official support for Python 3.11.
- Super basic `__repr__` for `StructBase` to ease debugging.
- `Envelope.amount`, `Envelope.synced`, `LFO.amount`,
  `LFO.attack`, `LFO.predelay` & `LFO.speed` [#69].

### Changed

- Moved `stretching` to `Sampler`, instruments don't have it.
- `Note.key` now returns a note name with octave [#66].
- A cleaner implementation of `MixerParamsEvent`.
- `Layer.__repr__` now shows the number of children also.
- Separated test assets into presets for better isolation of results [#6].
- Renamed `LFO.is_synced` to `LFO.synced` and `LFO.is_retrig` to `LFO.retring`.
- `StructBase` and `ListEventBase` are lazily evaluated now.
- Model collections are indexable by item names as well [#45].

### Fixed

- String are decoded as UTF16 when version is 11.5+ now [#65].
- `Insert.stereo_separation` docstring for maximum, minimum value.
- `U16TupleEvent.value` [#68].
- Minimum and maximum value docstrings for certain `FX` properties.
- `Sampler.pitch_shift` internal representation.

### Removed

- Images for individual FX properties as they were redundant.
- Redundant member `_SamplerInstrument.flags`.

[#6]: https://github.com/demberto/PyFLP/issues/6
[#45]: https://github.com/demberto/PyFLP/issues/45
[#55]: https://github.com/demberto/PyFLP/issues/55
[#56]: https://github.com/demberto/PyFLP/issues/56
[#57]: https://github.com/demberto/PyFLP/issues/57
[#58]: https://github.com/demberto/PyFLP/issues/58
[#65]: https://github.com/demberto/PyFLP/issues/65
[#66]: https://github.com/demberto/PyFLP/issues/66
[#68]: https://github.com/demberto/PyFLP/issues/68
[#69]: https://github.com/demberto/PyFLP/issues/69

## [2.0.0a1] - 2022-09-21

### Added

- `PlaylistItemBase.group` for `ChannelPlaylistItem` and `PatternPlaylistItem` [#36].
- More info in contributor's guide.
- VSCode Python extension configuration, recommended extensions and tasks.
- `ChannelRack.height` which tells the height of the channel rack in pixels.
- `Track[x]` returns `Track.items[x]`.
- `Patterns` warns when tried to be accessed with an index of 0.
- `Note.group`, a number which notes of the same group share [#28].
- `Note.slide` which indicates whether a note is a sliding note.
- Plugin wrapper properties to docs.
- A user guide section in docs.
- `Sampler.content`, `Layer.random` & `Layer.crossfade` [#24].
- `Playback.ping_pong_loop`.

### Changed

- `Pattern.notes` refactored into `Pattern.__iter__`.
- `Sampler.sample_path` returns `pathlib.Path` instead of `str` now [#41].
- `PluginID.Data` events get parsed during event collection itself.
- All models are now equatable and hashable.

### Fixed

- `Arrangement` parsing logic is incorrect [#32].
- `Track.color` returns `int` instead of `colour.Color` [#33].
- `_PlaylistItemStruct.track_index` should be 2 bytes [#36].
- Tracks don't get assigned playlist items [#37].
- KeyError when accessing `Track.content_locked` [#38].
- Channel type wasn't correctly detected at times [#40].
- `Arrangements.height` was actually `ChannelRack.height` [#43].
- TypeError when accessing `Insert.dock` [#44].
- `Pattern.note` and `Pattern.controllers` [#48].
- `Track.items` [#49]
- Certain properties of `Note` were interpreted incorrectly.
- `Slot.plugin` wasn't working at all (events, properties, repr) [#53].
- `FruitySend.send_to` was interepreted incorrectly.
- `Instrument.plugin` and `Slot.plugin` setter.
- `Playback.use_loop_points`.

### Removed

- `Arrangements.height`.

[#24]: https://github.com/demberto/PyFLP/issues/24
[#28]: https://github.com/demberto/PyFLP/issues/28
[#32]: https://github.com/demberto/PyFLP/issues/32
[#33]: https://github.com/demberto/PyFLP/issues/33
[#36]: https://github.com/demberto/PyFLP/issues/36
[#37]: https://github.com/demberto/PyFLP/issues/37
[#38]: https://github.com/demberto/PyFLP/issues/38
[#40]: https://github.com/demberto/PyFLP/issues/40
[#41]: https://github.com/demberto/PyFLP/issues/41
[#43]: https://github.com/demberto/PyFLP/issues/43
[#44]: https://github.com/demberto/PyFLP/issues/44
[#48]: https://github.com/demberto/PyFLP/issues/48
[#49]: https://github.com/demberto/PyFLP/issues/49
[#53]: https://github.com/demberto/PyFLP/issues/53

## [2.0.0a0] - 2022-09-14

PyFLP has been rewritten ✨

Highlights:

1. Richer events: Variable data events now parse their structure themselves.
   Fixed size events are categorized closely to the data they represent.
2. Lazy evaluation: Properties are evaluated as lazily as possible to prevent
   the use of private variables and keep them synced with event data.
3. Neatly organised models: Appropriate use of composition and subclassing.
4. Zero pre-parse field validation: Makes sense for an undocumented format.
5. Fully type hinted: Ensures strict adherence with pyright.
6. Simplified single-level module hierarchy to ease imports.
7. Docs now contain images for corresponding model types.

*The major version number bump indicates a breaking change, however I would highly
encourage you to upgrade to this version. **I WILL NOT BE MAINTAINING OLDER VERSIONS.***

## 1.1.2 - Unreleased

### Fixed

- [#9](https://github.com/demberto/PyFLP/pull/9), thanks to @zacanger.

## [1.1.1] - 2022-07-10

### Added

- Avoid mkdocs warnings in tox.

### Changed

- `_FLObject._save` always returns a list now.
- CI: Merge `dev` and `publish` workflows into one.

### Fixed

- [#8](https://github.com/demberto/PyFLP/issues/8).
- Type hints and type variables are much better.
- `FSoftClipper` property setter typo caused it to be set to zero.
- `ChannelParameters._save()` didn't return an event.

### Removed

- Wait action in CI workflow.
- `setup-cfg-fmt` pre-commit hook, [why?](https://github.com/asottile/setup-cfg-fmt/issues/147)

## [1.1.0] - 2022-05-29

### Added

- Support for Fruity Stereo Enhancer @@nickberry17
- Instructions for alternate methods to install PyFLP.

### Changed

- Improvements to CI

### Fixed

- Incorrect encoding used to dump UTF-16 strings in `_TextEvent`.
- [#4](https://github.com/demberto/PyFLP/issues/4).

### Removed

- `_FLObject.max_count`, `MaxInstancesError`, `test_flobject.py` and
  `_MaxInstancedFLObject`.
- Gitter links from README and room itself, due to inactivity.

## [1.0.1] - 2022-04-02

This update is more about QOL improvements, testing and refactoring. Few bugs
have been fixed as well, while Python 3.6 support has been deprecated.

### Added

- Adopted `bandit`.
- `_MaxInstancedFLObject`: `FLObject` with a limit on number of instances.
- GPL3 short license headers.
- Missing docs about `PatternNote` and `PatternController` events.
- Exceptions: `InvalidHeaderSizeError`, `InvalidMagicError` and `MaxInstancesError`.
- Import statements in submodules to simplify import process externally.
- Test validators and properties and project version setter.
- OTT plugin to test project to test VST plugins.

### Changed

- All use of `assert` has been replaced by exceptions (bandit: assert-used).
- Version links in changelog now show changes.
- LF line endings used and enforced everywhere.
- `ppq` field moved to `_FLObject` from `Playlist`.
- Much improved `tox.ini` and pre-commit configuration.
- Modules which aren't meant for external use are prefixed with a _.
- Simplified property declaration.

### Deprecated

- Python 3.6 support will be dropped in a future major release.

### Fixed

- All this time, `VSTPluginEvent` was never getting created/saved.
- Lint errors reported by flake8, pylint and bandit.
- Just realised `__setattr__` works only on instances 😅, came up with
  `_FLObjectMeta` which is the metaclass used by `_FLObject`.

### Removed

- Redundant `__repr__` from `PatternNote`.

## [1.0.0] - 2021-11-12

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

### Added

- `__repr__()` for all `_FLObject` subclasses.
- `Channel.color`, `Insert.color` and `Pattern.color` now return `colour.Color`.
  This is implemented by `ColorEvent` (*which subclasses `DWordEvent`*).
- New event implementations for `ChannelFX.EventID` (`Cutoff`, `Fadein`, `Fadeout` and more).
- New event implementations for `Channel.EventID` (`ChannelTracking`,
  `ChannelLevels`, `ChannelLevelOffsets`, `ChannelPolyphony` and more).
- `Channel.cut_group` implementing `Channel.EventID.CutSelfCutBy`.
- Remote controllers (`RemoteController`). Accessible from `Project.controllers`.
- Saving for `VSTPlugin`.
- All enum members used by `FLObject` subclasses now have a docstring.
- Added links in docstrings to official FL Studio Manual wherever possible.
- `Parser.__build_event_store()` uses inner methods now to parse different kind of events; very helpful for the new `DataEvents`.
- Added support for pattern controller events (`PatternController`, `PatternControllerEvent` who implement `PatternEventID.Controllers`).
- Many attribute docstrings now include minimum, maximum and default values. **These limits are enforced by setters**.
- Added `.editorconfig`, *using CRLF line endings btw*.
- Added `test_parser.py` and `test_events.py`.
- `Parser.parse_zip` now accepts a `bytes` object for `zip_file` parameter.
- `Misc.registered` for `Misc.EventID.Registered`.

### Changed

- All `_FLObject` subclasses have been moved to parent `pyflp/` from `pyflp/flobject/` to ease import names.
- All `Event` subclasses have been moved in a single `event.py` and `event/` folder is removed.
- All event ID enum names are now inner classes of `_FLObject` subclasses.
- Constructor of `Project` has been simplified.
- `VSTPlugin`'s underlying event now supports saving, it has been refactored out of `_parse_data_event` also.
- `InsertParametersEvent` to replace the equivalent parsing in `Insert._parse_data_event`.
- The `TODO` *(deleted now)* has been changed to reflect the type of goals.
- `_FLObject.save` is now `_FLObject._save`.
- Some constants present in `utils.py` have been moved to `constants.py`.
- Docs include a brief summary of the underlying data event wherever applicable.
- Minor property name changes; made them more concise.
- Absolute imports are used everywhere now.

### Fixed

- `ChannelFXReverb` was not getting initialised.
- `InsertParamsEvent` was not getting initialised.
- Syntax is highlighted in the [docs](https://pyflp.rtfd.io/) as expected now.
- `FNotebook2` text parsing.
- `Insert.routing` returned `True` for all tracks.
- `Misc.start_date` and `Misc.work_time` parsing.

### Removed

- Any and all sort of logging, not useful anymore. Haven't seen any 3rd party
  Python library ever using it. Used `warnings` wherever necessary.
- `mypy`. Its useless tbh, I will use types as I see fit.
- Setters for all properties containing `_FLObject` (or any sort of a collection of them), *e.g. Arrangement.tracks*.

## [0.2.0]

### **Highlights**

- **PyFLP has passed the null test for a full project of mine (FL 20.7.2) 🥳**.
- This library uses code from [FLParser](https://github.com/monadgroup/FLParser),
  a GPL license project, PyFLP is now under GPL.
- API reference documentation is complete now.
- Few new events implemented for `Channel`.
- Refactored `FLObject` and `Plugin`.

#### `FLObject` refactoring

- `parseprop` is now `_parseprop`.
- All `_parseprop` delegates are now "protected" as well.
- `setprop` is now `_setprop`.

### Added

- `ChannelEvent.Delay` is implemented by `ChannelDelay` and `Channel.delay`.
- `Event.to_raw` and `Event.dump` now log when they are called.
- Exceptions `DataCorruptionDetected` and `OperationNotPermitted`.

### Fixed

- Can definitely say, all naming inconsistencies have been fixed.
- Fixed `TimeMarker` assign to `Arrangement` logic in `Parser`.
- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, caused due to
  double dumping of same events.
- Empty pattern events, `PatternEvent.Name` and `PatternEvent.Color` don't get saved.

---

❗ These versions below don't work due to naming inconsistencies 😅, you will not find them 👇

## [0.1.2]

### Added

- More docs.
- Add some new properties/events to `Channel`.
- A sample empty FLP has been provided to allow running tests.
- All `FLObject` subclasses now have a basic `__repr__` method.

### Fixed

- Improve the GitHub workflow action, uploads to PyPI will not happen unless the test is passed.
- ~~Fix all naming inconsistencies caused due to migration to [`BytesIOEx`](https://github.com/demberto/BytesIOEx)~~ Not all.

### Known issues

Same as in 0.1.1

## [0.1.1]

~~The first version of PyFLP that works correctly 🥳~~ No, unfortunately

### **Highlights**

- Changed documentation from Sphinx to MkDocs.
- [FLPInfo](https://github.com/demberto/FLPInfo) is now a separate package.
- FLPInspect is now a separate package.
- PyFLP now uses [BytesIOEx](https://github.com/demberto/BytesIOEx/) as an external dependency.

### Fixed

- `ByteEvent`, `WordEvent` and `DWordEvent` now raise a `TypeError`.
  when they are initialised with the wrong size of data.
- Fix setup.cfg, project structure is now as expected, imports will work.
- [Docs](https://pyflp.rtfd.io/) are now up and running.

### Known issues

- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, why this is caused is not known.

---

**❗ These versions below don't work because I didn't know how to configure `setup.cfg` properly 😅**

## 0.1.0

- `flpinspect` - An FLP Event Viewer made using Tkinter.
- `flpinfo` - A CLI utility to get basic information about an FLP.
- Switched to MIT License.

### Added

- Lots of changes, refactoring and code cleanup of `pyflp`.
- New docs.
- Changes to `README`.
- Adopted [`black`](https://github.com/psf/black) coding style.
- Added a `log_level` argument to `Parser`.
- `Project.create_zip` copies stock samples as well now.
- `Project.get_events` for getting just the events; they are not parsed.
  Read [docs](https://pyflp.rtfd.io) for more info about this.
- `Event` classes now have an `__eq__` and `__repr__` method.

### Fixed

- Tests don't give module import errors.
- `Pattern` event parsing.
- Initialise `_count` to 0, everytime `Parser` is initialised.
- `Project.create_zip` now works as intended.
- Overhauled logging.
- A lot of potential bugs in `FLObject` subclasses.

### Known issues

- `flpinfo` doesn't output correctly sometimes due to long strings.
- Extraneous data dumped sometimes by `InsertSlotEvent.Plugin`, why this is caused is not known.

[2.1.1]: https://github.com/demberto/PyFLP/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/demberto/PyFLP/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/demberto/PyFLP/compare/v2.0.0a7.post0...v2.0.0
[2.0.0a7]: https://github.com/demberto/PyFLP/compare/v2.0.0a6...v2.0.0a7
[2.0.0a6]: https://github.com/demberto/PyFLP/compare/v2.0.0a5.post...v2.0.0a6
[2.0.0a5.post]: https://github.com/demberto/PyFLP/compare/v2.0.0a5...v2.0.0a5.post
[2.0.0a5]: https://github.com/demberto/PyFLP/compare/v2.0.0a4...v2.0.0a5
[2.0.0a4]: https://github.com/demberto/PyFLP/compare/v2.0.0a3...v2.0.0a4
[2.0.0a3]: https://github.com/demberto/PyFLP/compare/v2.0.0a2...v2.0.0a3
[2.0.0a2]: https://github.com/demberto/PyFLP/compare/v2.0.0a1...v2.0.0a2
[2.0.0a1]: https://github.com/demberto/PyFLP/compare/v2.0.0a0...v2.0.0a1
[2.0.0a0]: https://github.com/demberto/PyFLP/compare/v1.1.1...v2.0.0a0
[1.1.1]: https://github.com/demberto/PyFLP/compare/1.1.0...v1.1.1
[1.1.0]: https://github.com/demberto/PyFLP/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/demberto/PyFLP/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/demberto/PyFLP/compare/0.2.0...1.0.0
[0.2.0]: https://github.com/demberto/PyFLP/compare/0.1.2...0.2.0
[0.1.2]: https://github.com/demberto/PyFLP/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/demberto/PyFLP/releases/tag/0.1.1
