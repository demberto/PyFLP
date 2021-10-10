## FLPInfo

> A CLI utility to print basic information about an FLP.

## Usage

```
>>> flpinfo /path/to/flp.flp

Title:            My FLP, My Song
Artist(s):        Who else than me?
Genre:            Unique
Project URL:      https://google.com
FL Version:       20.8.3.2304
Channel(s):       10 [Piano, Lead, Chord, ...]
Arrangement(s):   1 [Arrangement]
Pattern(s):       2 [Clap, Hats]
Note(s):          69
```

## Command-line options

```
flpinfo [-h] [-v] [--full-lists] [--no-color] flp_or_zip

positional arguments:
  flp_or_zip     The location of FLP/zipped FLP to show information about.

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Display verbose logging output and full lists
  --full-lists   Lists will not appear truncated.
  --no-color     Disables colored output
```
