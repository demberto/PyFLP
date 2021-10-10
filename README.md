[![Documentation Status](https://readthedocs.org/projects/pyflp/badge/?version=latest)](https://pyflp.readthedocs.io/en/latest/?badge=latest)
![PyPI - License](https://img.shields.io/pypi/l/pyflp)
![PyPI](https://img.shields.io/pypi/v/pyflp?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyflp)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-black)

# PyFLP

PyFLP allows an object oriented access to an FLP. This provides an abstraction from its TLV implementation. _Please don't use this for serious stuffs yet._

You should also check these:
- A CLI utility **FLPInfo** to see basic information about an FLP.
- A GUI tool **FLPInspect** for a further, detailed view into the internal structure of an FLP.

## Usage

PyFLP can be used for automation purposes e.g. finding/setting project titles, artists names, genre etc. and also by people who are interested more about the FLP format. You can even repair a broken FLP, *ofcourse by yourself*.

### Initialisation

```{code-block} python
from pyflp import Parser
project = Parser(verbose=True).parse("/path/to/efelpee.flp")
```

### Saving

```{code-block} python
project.save(save_path="/path/to/save.flp")
```

### Export it as a ZIP looped package

```{code-block} python
project.create_zip(path="/path/to/flp.zip")
```

## Installation

```
pip install pyflp
```

## Testing

I have created a [null test](tests/test_parser.py). More tests need to be added.

## Thanks

[**Monad.FLParser**](https://github.com/monadgroup/FLParser) for providing up-to-date parsing logic and the idea of creating an object model

[**FLPEdit**](https://github.com/roadcrewworker) I swear, this library would have remained a dream without this tool. A very helpful program for examining the event structure as it is present in an FLP and value of events. It is very unfortunate that the author has removed it.

## Contributions

If you can spare some time for testing and/or contributing, I would be very grateful. Please check the [TODO](TODO.md) as well for current goals/issues. Its kind of getting difficult for me as this project becomes bigger. You can reach me at **demberto**[at]**protonmail**[dot]**com** as well :)
