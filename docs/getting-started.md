## Getting Started

PyFLP can be used for automation purposes e.g. finding/setting project titles, artists names, genre etc. and also by people who are interested more about the FLP format. You can even repair a broken FLP, *ofcourse by yourself*.

## Installation

```
pip install --upgrade pyflp
```

### Initialisation

```Python
from pyflp import Parser
project = Parser(verbose=True).parse("/path/to/efelpee.flp")
```

### Saving

```Python
project.save(save_path="/path/to/save.flp")
```

### Export it as a ZIP looped package

```Python
project.create_zip(path="/path/to/flp.zip")
```
