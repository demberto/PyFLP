[![Documentation Status](https://readthedocs.org/projects/pyflp/badge/?version=latest)](https://pyflp.readthedocs.io/en/latest/?badge=latest)
![PyPI - License](https://img.shields.io/pypi/l/pyflp)
![PyPI](https://img.shields.io/pypi/v/pyflp?color=blue)

# PyFLP
PyFLP creates an object from an FLP. You can edit it and save it back also. *Please don't use this for serious stuffs, I have done minimal testing myself and much of the features are yet to be implemented.*

It also has useful utilities like:
* Creating a ZIP looped package from an FLP

## Usage
```Python
from pyflp.parser import ProjectParser
project = ProjectParser().parse("/path/to/efelpee.flp")

# Use ProjectParser(verbose=True) if you want to see logs
```

## Installation

```
pip install pyflp
```

## Testing
I have created a [null test](test_parser.py). More tests need to be added.

## Thanks

[**Monad.FLParser**](https://github.com/monadgroup/FLParser) for providing up-to-date parsing logic and the idea of creating an object model

[**FLPEdit**](https://github.com/roadcrewworker) I swear, this library would have remained a dream without this tool. A very helpful program for examining the event structure as it is present in an FLP and value of events. It is very unfortunate that the author has removed it.

## Contributions

If you can spare some time for testing and/or contributing, I would be very grateful. Please check the [TODO](../TODO) as well for current goals/issues. You can reach me at **demberto**[at]**protonmail**[dot]**com** as well :)