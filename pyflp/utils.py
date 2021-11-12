from dataclasses import dataclass, field


def isascii(s: str) -> bool:
    """str.isascii() for Python 3.6

    Attribution: https://stackoverflow.com/a/18403812
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
    string: str = field(repr=False)
    major: int = field(init=False)
    minor: int = field(init=False)
    revision: int = field(init=False)
    build: int = field(init=False)

    def __post_init__(self):
        split = self.string.split(".")
        self.major = int(split[0])
        self.minor = int(split[1])
        self.revision = int(split[2])
        try:
            self.build = int(split[3])
        except IndexError:  # pragma: no cover
            pass

    def as_float(self) -> float:
        return float(f"{self.major}.{self.minor}")
