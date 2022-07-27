# Handbook

## Parsing

```py
import pyflp
project = pyflp.parse("/path/to/parse.flp")
```

## Saving

```py
import pyflp
pyflp.save(project, "/path/to/save.flp")
```

### Get some channel information

```py
for channel in project.channels:
    print(channel.name)         # (1)
    print(channel.type)         # (2)
    print(channel.sample_path)  # (3)
```

1. The user set name of a channel as is visible in FL Studio.
2. Sampler, Audio, Instrument, Layer, see `ChannelType`.
3. The location of a sample used in a sampler or plain audio

There's a lot more information you can get (almost every type of information
stored about a channel).

### What about patterns?

```py
for pattern in project.patterns:
    print(pattern.name)
    print(len(pattern.notes))   # (1)
```

1. The total number of notes in a pattern.

You can even get information about a particular note

```py
for note in pattern.notes:
    print(note.key)
```
