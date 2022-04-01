# Handbook

PyFLP can be used for automation purposes e.g. finding/setting project titles,
artists names, genre etc. and also by people who are interested more about the
FLP format. You can even repair a broken FLP, *ofcourse by yourself*.

## Initialisation

```Python
from pyflp import Parser
project = Parser(verbose=True).parse("/path/to/efelpee.flp")
```

## Saving

```Python
project.save(save_path="/path/to/save.flp")
```

### Get some channel information

```Python
for channel in project.channels:
    print(channel.name)     # Channel name
    print(channel.kind)     # Sampler, Audio, Instrument, Layer, ...
    # The location of a sample used in a sampler or plain audio
    print(channel.sample_path)
```

There's a lot more information you can get (almost every type of information
stored about a channel).

!!! tip "For more information"
    See [Channel](reference/channel.md).

### What about patterns?

```Python
for pattern in project.patterns:
    print(pattern.name)
    print(len(pattern.notes))   # The total amount of notes a pattern holds
```

#### You can even get information about a particular note

```Python
...
for note in pattern.notes:
    print(note.key)
```

!!! tip "For more information"
    See [Pattern](reference/pattern.md) and [PatternNote](reference/pattern.md#PatternNote)

!!! hint "Docstrings"
    Almost all properties have a meaningful docstring, and many classes have a
    direct link to the FL Studio manual page to point out what they implement.

!!! note
    There is much more, check the [Reference](reference.md)

### Export it as a ZIP looped package

```Python
project.create_zip(path="/path/to/flp.zip")
```
