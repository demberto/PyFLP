from dataclasses import dataclass, field

BYTE = 0
WORD = 64
DWORD = 128
TEXT = 192
DATA = 208

DATA_TEXT_EVENTS = (
    TEXT + 49,  # Arrangement.name
    TEXT + 39,  # FilterChannel.name
    TEXT + 47,  # Track.name
)


def isascii(s: str) -> bool:
    """str.isascii() for Python 3.6

    [StackOverflow](https://stackoverflow.com/a/18403812)
    """
    return len(s) == len(s.encode())


def buflen_to_varint(buffer: bytes) -> bytes:
    ret = bytearray()
    buflen = len(buffer)
    while True:
        towrite = buflen & 0x7F
        buflen >>= 7
        if buflen > 0:
            towrite |= 0x80
        ret.append(towrite)
        if buflen <= 0:
            break
    return bytes(ret)


@dataclass
class FLVersion:
    string: str
    major: int = field(init=False, repr=False)
    minor: int = field(init=False, repr=False)
    revision: int = field(init=False, repr=False)
    build: int = field(init=False, repr=False)

    def __post_init__(self):
        split = self.string.split(".")
        self.major = int(split[0])
        self.minor = int(split[1])
        self.revision = int(split[2])
        try:
            self.build = int(split[3])
        except IndexError:
            pass

    def as_float(self) -> float:
        return float(f"{self.major}.{self.minor}")
