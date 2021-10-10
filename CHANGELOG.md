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
