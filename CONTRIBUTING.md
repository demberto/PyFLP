# Contributor's Guide

PyFLP adheres to the [Contributor Covenant Code of Conduct][code-of-conduct].
Please make sure you have read it and accept it before proceeding further.

*This document is still a WIP*.

## Testing

- Check the comments inside [test FLP][test-flp].
- Create a virtual environment before setting up.

## Docs

Don't forget to update the [docs](https://pyflp.rtfd.io/) after you are done
with a feature or a bug fix that affects the documentation.

## Use `black`

PyFLP use the black code style, format your code with it.

## VSCode

I use VSCode for development. I have made certain changes to the workspace to
suit my workflows and make life easier.

<!-- TODO Inspect whether venv creation can be automated through VSCode. -->

### Python extension configuration

To ease linting, enforce strict type checking and improve code quality, I have
modified certain settings for the official Python / Pylance extension, so that
you don't need to manually configure it or encounter issues while committing.
Check [settings.json].

### Recommended extensions

When you open the repo directory in VSCode, you will get recommendations for
extensions. I use these extensions myself. You can check [extensions.json] to
know why and where they are used.

### Tasks

If you use Windows, I have made some shortcuts for common tasks. Check [tasks.json].

[code-of-conduct]: https://github.com/demberto/PyFLP/blob/master/CODE_OF_CONDUCT.md
[extensions.json]: https://github.com/demberto/PyFLP/blob/master/.vscode/extensions.json
[settings.json]: https://github.com/demberto/PyFLP/blob/master/.vscode/settings.json
[tasks.json]: https://github.com/demberto/PyFLP/blob/master/.vscode/tasks.json
[test-flp]: https://github.com/demberto/PyFLP/blob/master/tests/assets/FL%2020.8.4.flp
