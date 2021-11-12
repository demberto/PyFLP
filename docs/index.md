![GitHub Workflow Status](https://img.shields.io/github/workflow/status/demberto/pyflp/Build%20&%20Publish?style=flat-square)
[![Documentation Status](https://readthedocs.org/projects/pyflp/badge/?version=latest)](https://pyflp.readthedocs.io/en/latest/?badge=latest)
[![CodeFactor](https://www.codefactor.io/repository/github/demberto/pyflp/badge)](https://www.codefactor.io/repository/github/demberto/pyflp)
[![codecov](https://codecov.io/gh/demberto/PyFLP/branch/master/graph/badge.svg?token=RGSRMMF8PF)](https://codecov.io/gh/demberto/PyFLP)
![PyPI - License](https://img.shields.io/pypi/l/pyflp?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/pyflp?color=blue&style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyflp?style=flat-square)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)

# PyFLP

> An FL Studio project file (.flp) parser

PyFLP is a parser (written in pure-Python, hence cross-platform) for FL Studio project (.flp) files.

You should also check some of my other projects based on PyFLP:

- A CLI utility [**FLPInfo**](https://github.com/demberto/FLPInfo) to see basic information about an FLP.
- A GUI tool [**FLPInspect**](https://github.com/demberto/FLPInspect) for a further, detailed view into the internal structure of an FLP.


### Installation

PyFLP requires Python 3.6+.

```
pip install --upgrade pyflp
```

### Usage

```Python
from pyflp import Parser
project = Parser().parse("/path/to/efelpee.flp")
```

More examples [here](handbook.md)

### Note

PyFLP or me, demberto the author of this library am in no way affiliated to Image-Line. This library is only tested with FL 20 and later projects. Projects made with older versions of FL have vast differences in the internal event structuring. But if your project can't be parsed, I have some good news for you, you can still read/edit the event structure (TLV implementation) in [FLPInspect](https://github.com/demberto/FLPInspect).

### Thanks

[**Monad.FLParser**](https://github.com/monadgroup/FLParser) for providing up-to-date parsing logic and the idea of creating an object model.

**FLPEdit** [(author)](https://github.com/roadcrewworker) I swear, this library would have remained a dream without this tool. A very helpful program for examining the event structure as it is present in an FLP and value of events. It is very unfortunate that the author has taken it down. [FLPInspect](https://github.com/demberto/FLPInspect) is a _WIP_ recreation of this legendary tool.

### [Changelog](https://github.com/demberto/PyFLP/blob/master/CHANGELOG.md)

The **Changelog** is where you will see a detailed list of end-user and implementation level additions, changes, improvements, bug fixes, refactorings and more. You should check this if you are interested in the history of PyFLP.

### [TODO](https://github.com/demberto/PyFLP/blob/master/TODO.md)

I keep a list of current goals, issues and more general (i.e. longtime) goals in the **TODO**. Contributors should check this.

### [Contributing](contributing.md)

If you are interested in the development of PyFLP, please check the contributing section. All contributions in whatever methods you see fit (issues, PRs, etc.) are welcome.

### License

PyFLP has been licensed under the [GNU Public License v3](https://www.gnu.org/licenses/gpl-3.0.en.html). The reason for this is some of the code has been taken from [FLParser](https://github.com/monadgroup/FLParser), a library also under the same license.
