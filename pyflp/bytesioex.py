import io
import struct
from typing import Optional

Bool = struct.Struct("?")
SByte = struct.Struct("b")
Byte = struct.Struct("B")
Short = struct.Struct("h")
UShort = struct.Struct("H")
Int = struct.Struct("i")
UInt = struct.Struct("I")
Long = struct.Struct("q")
ULong = struct.Struct("Q")
Float = struct.Struct("f")
Double = struct.Struct("d")


class BytesIOEx(io.BytesIO):
    """C# BinaryReader + BinaryWriter equivalent."""

    def read_bool(self) -> Optional[bool]:
        """Reads a C99 _Bool."""
        buf = self.read(1)
        return Bool.unpack(buf)[0] if buf else None

    def read_int8(self) -> Optional[int]:
        """Reads a 1-byte signed integer."""
        buf = self.read(1)
        return SByte.unpack(buf)[0] if buf else None

    def read_uint8(self) -> Optional[int]:
        """Reads a 1-byte unsigned integer."""
        buf = self.read(1)
        return Byte.unpack(buf)[0] if buf else None

    def read_int16(self) -> Optional[int]:
        """Reads a 2-byte signed integer."""
        buf = self.read(2)
        return Short.unpack(buf)[0] if buf else None

    def read_uint16(self) -> Optional[int]:
        """Reads a 2-byte unsigned integer."""
        buf = self.read(2)
        return UShort.unpack(buf)[0] if buf else None

    def read_int32(self) -> Optional[int]:
        """Reads a 4-byte signed integer."""
        buf = self.read(4)
        return Int.unpack(buf)[0] if buf else None

    def read_uint32(self) -> Optional[int]:
        """Reads a 4-byte unsigned integer."""
        buf = self.read(4)
        return UInt.unpack(buf)[0] if buf else None

    def read_int64(self) -> Optional[int]:
        """Reads an 8-byte signed integer."""
        buf = self.read(8)
        return Long.unpack(buf)[0] if buf else None

    def read_uint64(self) -> Optional[int]:
        """Reads an 8-byte unsigned integer."""
        buf = self.read(8)
        return ULong.unpack(buf)[0] if buf else None

    def read_float(self) -> Optional[float]:
        """Reads a 4-byte floating-point number."""
        buf = self.read(4)
        return Float.unpack(buf)[0] if buf else None

    def read_double(self) -> Optional[float]:
        """Reads an 8-byte floating-point number."""
        buf = self.read(8)
        return Double.unpack(buf)[0] if buf else None

    def read_varint(self) -> Optional[int]:
        """Reads a 7bit variable sized encoded integer."""
        b = self.read_uint8()
        if b is not None:
            data_len = b & 0x7F
            shift = 7
            while (b & 0x80) != 0:
                b = self.read_uint8()
                if b is None:
                    break
                data_len |= (b & 0x7F) << shift
                shift += 7
            return data_len
        return None

    def write_bool(self, value: bool) -> int:
        return self.write(Bool.pack(value))

    def write_int8(self, value: int) -> int:
        return self.write(SByte.pack(value))

    def write_uint8(self, value: int) -> int:
        return self.write(Byte.pack(value))

    def write_int16(self, value: int) -> int:
        return self.write(Short.pack(value))

    def write_uint16(self, value: int) -> int:
        return self.write(UShort.pack(value))

    def write_int32(self, value: int) -> int:
        return self.write(Int.pack(value))

    def write_uint32(self, value: int) -> int:
        return self.write(UInt.pack(value))

    def write_int64(self, value: int) -> int:
        return self.write(Long.pack(value))

    def write_uint64(self, value: int) -> int:
        return self.write(ULong.pack(value))

    def write_float(self, value: float) -> int:
        return self.write(Float.pack(value))

    def write_double(self, value: float) -> int:
        return self.write(Double.pack(value))

    def write_varint(self, buflen: int) -> int:
        """Converts an unsigned integer to a 7-bit encoded integer (varint) and writes it.

        Args:
            buflen (int): The length of the buffer to be converted.
        """
        ret = bytearray()
        while True:
            towrite = buflen & 0x7F
            buflen >>= 7
            if buflen > 0:
                towrite |= 0x80
            ret.append(towrite)
            if buflen <= 0:
                break
        return self.write(bytes(ret))
