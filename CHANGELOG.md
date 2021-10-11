# 0.1.1

The first version of PyFLP that works correctly 🥳

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

Same as in 0.1.0

******************************************************************************************************************************
**❗ These versions below don't work because I didn't know how to configure `setup.cfg` properly 😅, you will not find them 👇**


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
- `Project.get_events` for getting just the events; they are not parsed.
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
******************************************************************************************************************************
