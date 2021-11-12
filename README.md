![GitHub Workflow Status](https://img.shields.io/github/workflow/status/demberto/pyflp/Build%20&%20Publish?style=flat-square)
[![Documentation Status](https://readthedocs.org/projects/pyflp/badge/?version=latest)](https://pyflp.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/demberto/PyFLP/branch/master/graph/badge.svg?token=RGSRMMF8PF)](https://codecov.io/gh/demberto/PyFLP)
[![CodeFactor](https://www.codefactor.io/repository/github/demberto/pyflp/badge)](https://www.codefactor.io/repository/github/demberto/pyflp)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/PyFLP/community)
![PyPI - License](https://img.shields.io/pypi/l/pyflp?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/pyflp?color=blue&style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyflp?style=flat-square)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)

# PyFLP

> An FL Studio project file (.flp) parser

PyFLP is a parser (written in pure-Python, cross-platform) for FL Studio project (.flp) files.

You should also check some of my other projects based on PyFLP:

- A CLI utility [**FLPInfo**](https://github.com/demberto/FLPInfo) to see basic information about an FLP.
- A GUI tool [**FLPInspect**](https://github.com/demberto/FLPInspect) for a further, detailed view into the internal structure of an FLP.

## Installation

PyFLP requires Python 3.6+

```
pip install --upgrade pyflp
```

## Usage

### Initialisation

```Python
from pyflp import Parser
project = Parser().parse("/path/to/efelpee.flp")
```

More examples [here](https://pyflp.rtfd.io/handbook.md)

# Documentation

Docs are available on [ReadTheDocs](https://pyflp.rtfd.io)

## Thanks

[**Monad.FLParser**](https://github.com/monadgroup/FLParser)

**FLPEdit** [(author)](https://github.com/roadcrewworker)

## [Contributing](https://github.com/demberto/PyFLP/blob/master/CONTRIBUTING.md)

## [Changelog](https://github.com/demberto/PyFLP/blob/master/CHANGELOG.md)

## License

**PyFLP** has been licensed under the [GNU Public License v3](https://www.gnu.org/licenses/gpl-3.0.en.html).
