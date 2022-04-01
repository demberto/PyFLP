# Contributing

PyFLP adheres to the [Contributor Covenant Code of Conduct][covenant].
Please make sure you have read it and accept it before proceeding further.

## Code Style: Black

PyFLP follows the [black](https://github.com/psf/black) code style. It has a
formatter. Make sure to use it.

## Code comments

At places in the code, you will see comments like this

```
# * Important
# ? Doubt
# ! Urgent
```

I recommend you to install [Better Comments][better-comments] and use the
appropriate formatting.

## Docstrings

The object model created by PyFLP is its core, ensure property docstrings are
given wherever possible; however avoid redundant ones, along with other
information like minimum, maximum limits and default. Also mention whether the
default event linked to a property is stored or not. Currently PEP-257 attribute
docstrings are used heavily and VS Code luckily supports them.

Don't add a full-stop/period after an exception docstring. It is used by
`__repr__` to format the exception string.

### When to document?

```Python
prop: int = IntProperty()
"""Doc doc doc. Min: min, Max: max, Default: default."""
```

Document properties when you satisfy either of the conditions:

- When you have some basic information other than the property name itself.
- When you have minimum, maximum and/or default values.

### When NOT to document?

```Python
color: colour.Color = ColorProperty()
"""Color."""
```

Don't document properties like name, color, index etc. if the property name
itself is the only useful information available. These properties occur
throughout the object model that their meaning is pretty self-explanatory.

## Imports

Submodule `__init__.py` files have `import` statements in them. They are only
to simplify the import process externally (make it look less messier) and not
to be used internally.

## Issues

You should begin with the [TODO](https://github.com/demberto/PyFLP/blob/master/TODO.md).

## Testing

Testing is a difficult thing. A proprietary closed sourced program and a closed
format add to the woes. If any genius soul has a solution, please help me!

### Running tests

Run tests with [`coverage.py`](https://github.com/nedbat/coveragepy)

```
coverage run -m pytest
```

!!! tip "Check coverage reports"
    `coverage html`

## Documentation

PyFLP uses MkDocs, the process to update it is fairly simple. Documentation is
not versioned yet and I don't see the need to do it in the near future either.
I used Sphinx earlier, but its love for reStructuredText makes it difficult to
use.

## Changelog update

I am not using any tools to generate automated changelogs.
[Keep A Changelog](https://keepachangelog.com/) format is used.

## Pre-commit hooks

[Pre-commit](https://pre-commit.com/) is used. Its configuration can be found
[here](https://github.com/demberto/PyFLP/blob/master/.pre-commit-config.yaml)

<!-- LINKS -->

[better-comments]: https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments
[covenant]: https://github.com/demberto/PyFLP/blob/master/CODE_OF_CONDUCT.md
