from __future__ import annotations
from dataclasses import dataclass, field
from scssdk_dataclasses import TYPE_SIZE_BY_ID
from struct import calcsize, unpack_from


@dataclass
class SCSValueFVector:
    x: float = field(default=0)
    y: float = field(default=0)
    z: float = field(default=0)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> SCSValueFVector:
        return SCSValueFVector(*unpack_from("=fff", buffer, offset))

    @staticmethod
    def size() -> int:
        return calcsize("=fff")


@dataclass
class SCSValueDVector:
    x: float = field(default=0)
    y: float = field(default=0)
    z: float = field(default=0)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> SCSValueDVector:
        return SCSValueDVector(*unpack_from("=ddd", buffer, offset))

    @staticmethod
    def size() -> int:
        return calcsize("=ddd")

@dataclass
class SCSValueEuler:
    heading: float = field(default=0)
    pitch: float = field(default=0)
    roll: float = field(default=0)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> SCSValueEuler:
        return SCSValueEuler(*unpack_from("=fff", buffer, offset))

    @staticmethod
    def size() -> int:
        return calcsize("=fff")

@dataclass
class SCSValueFPlacement:
    position: SCSValueFVector = field(default_factory=SCSValueFVector)
    orientation: SCSValueEuler = field(default_factory=SCSValueEuler)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> SCSValueFPlacement:
        return SCSValueFPlacement(SCSValueFVector.from_bytes(buffer, offset),  SCSValueEuler(buffer, offset + TYPE_SIZE_BY_ID[SCSValueFVector.size()]))

@dataclass
class SCSValueDPlacement:
    position: SCSValueDVector = field(default_factory=SCSValueDVector)
    orientation: SCSValueEuler = field(default_factory=SCSValueEuler)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> SCSValueDPlacement:
        return SCSValueDPlacement(SCSValueDVector.from_bytes(buffer, offset),  SCSValueEuler(buffer, offset + TYPE_SIZE_BY_ID[SCSValueDVector.size()]))


def szstr_from_bytes(buffer, offset: int = 0) -> str:
    end: int = len(buffer)
    for i, c in enumerate(buffer[offset:]):
        if c == 0:
            end = i
            break

    if end == len(buffer):
        raise ValueError("Non-null terminated string")

    return bytes(buffer[offset:end + 1]).decode()


type ValueTypes = bool | int | float | SCSValueFVector | SCSValueDVector | SCSValueEuler | SCSValueFPlacement | SCSValueDPlacement | str


UNPACK_SPEC_BY_ID: list[str] = [
    "",
    "?",
    "i",
    "I",
    "Q",
    "f",
    "d",
    "",
    "",
    "",
    "",
    "",
    "",
    "q"
]


FROM_BYTES_BY_ID: list = [
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    SCSValueFVector.from_bytes,
    SCSValueDVector.from_bytes,
    SCSValueEuler.from_bytes,
    SCSValueFPlacement.from_bytes,
    SCSValueDPlacement.from_bytes,
    szstr_from_bytes,
    None
]


def value_from_bytes(scs_value_type: int, buffer, offset: int = 0) -> ValueTypes:
    if UNPACK_SPEC_BY_ID[scs_value_type]:
        return unpack_from(f"={UNPACK_SPEC_BY_ID[scs_value_type]}", buffer, offset)[0]

    if FROM_BYTES_BY_ID[scs_value_type]:
        return FROM_BYTES_BY_ID[scs_value_type](buffer, offset)

    raise ValueError("invalid scs value type")


def value_storage_from_bytes(scs_value_type: int, buffer, offset: int = 0) -> tuple[bool, ValueTypes]:
    if offset == len(buffer):
        raise ValueError("offset out of bounds.")
    return buffer[offset] > 0, value_from_bytes(scs_value_type, buffer, offset + 1)
