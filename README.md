![GitHub Workflow Status](https://img.shields.io/github/workflow/status/demberto/pyflp/Build%20&%20Publish?style=flat-square)
[![Documentation Status](https://readthedocs.org/projects/pyflp/badge/?version=latest)](https://pyflp.readthedocs.io/en/latest/?badge=latest)
![PyPI - License](https://img.shields.io/pypi/l/pyflp?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/pyflp?color=blue&style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyflp?style=flat-square)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)

# PyFLP

PyFLP allows an object oriented access to an FLP. This provides an abstraction from its TLV implementation.

You should also check these:
- A CLI utility [**FLPInfo**](https://github.com/demberto/FLPInfo) to see basic information about an FLP.
- A GUI tool [**FLPInspect**](https://github.com/demberto/FLPInspect) for a further, detailed view into the internal structure of an FLP.

# Documentation

Docs are available on [ReadTheDocs](https://pyflp.rtfd.io)

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

## Note

PyFLP or me, demberto the author of this library am in no way affiliated to Image-Line. This library is only tested with FL 20 and later projects. Projects made with older versions of FL have vast differences in the internal event structuring. But if your project can't be parsed, I have some good news for you, you can still read/edit the event structure (TLV implementation) it in [FLPInspect](https://github.com/demberto/FLPInspect).

## Thanks

[**Monad.FLParser**](https://github.com/monadgroup/FLParser) for providing up-to-date parsing logic and the idea of creating an object model.

**FLPEdit** [(author)](https://github.com/roadcrewworker) I swear, this library would have remained a dream without this tool. A very helpful program for examining the event structure as it is present in an FLP and value of events. It is very unfortunate that the author has removed it. [FLPInspect](https://github.com/demberto/FLPInspect) is a _WIP_ recreation of this legendary tool.

## Contributions

If you can spare some time for testing and/or contributing, I would be very grateful. Please check the [TODO](TODO.md) as well for current goals/issues. Its kind of getting difficult for me as this project becomes bigger. You can reach me at **demberto**[at]**protonmail**[dot]**com** as well :)

## License

PyFLP has been licensed under the [GNU Public License v3](https://www.gnu.org/licenses/gpl-3.0.en.html). The reason for this is some of the code has been taken from [FLParser](https://github.com/monadgroup/FLParser), a library also under the same license.
