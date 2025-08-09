from __future__ import annotations
from typing import Callable, Any
from dataclasses import dataclass, field
from scssdk_dataclasses import TYPE_SIZE_BY_ID
from struct import calcsize, unpack_from


@dataclass
class SCSValueFVector:
    x: float = field(default=0)
    y: float = field(default=0)
    z: float = field(default=0)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> tuple[SCSValueFVector, int]:
        return SCSValueFVector(*unpack_from("=fff", buffer, offset)), TYPE_SIZE_BY_ID[7]

    @staticmethod
    def size() -> int:
        return calcsize("=fff")


@dataclass
class SCSValueDVector:
    x: float = field(default=0)
    y: float = field(default=0)
    z: float = field(default=0)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> tuple[SCSValueDVector, int]:
        return SCSValueDVector(*unpack_from("=ddd", buffer, offset)), TYPE_SIZE_BY_ID[8]

    @staticmethod
    def size() -> int:
        return calcsize("=ddd")

@dataclass
class SCSValueEuler:
    heading: float = field(default=0)
    pitch: float = field(default=0)
    roll: float = field(default=0)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> tuple[SCSValueEuler, int]:
        return SCSValueEuler(*unpack_from("=fff", buffer, offset)), TYPE_SIZE_BY_ID[9]

    @staticmethod
    def size() -> int:
        return calcsize("=fff")

@dataclass
class SCSValueFPlacement:
    position: SCSValueFVector = field(default_factory=SCSValueFVector)
    orientation: SCSValueEuler = field(default_factory=SCSValueEuler)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> tuple[SCSValueFPlacement, int]:
        position, position_read = SCSValueFVector.from_bytes(buffer, offset)
        orientation, orientation_read = SCSValueEuler.from_bytes(buffer, offset + position_read)
        return SCSValueFPlacement(position, orientation), position_read + orientation_read

@dataclass
class SCSValueDPlacement:
    position: SCSValueDVector = field(default_factory=SCSValueDVector)
    orientation: SCSValueEuler = field(default_factory=SCSValueEuler)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> tuple[SCSValueDPlacement, int]:
        position, position_read = SCSValueDVector.from_bytes(buffer, offset)
        orientation, orientation_read = SCSValueEuler.from_bytes(buffer, offset + position_read)
        return SCSValueDPlacement(position, orientation), position_read + orientation_read


def szstr_from_bytes(buffer, offset: int = 0) -> tuple[str, int]:
    if len(buffer) == offset:
        raise ValueError("Offset out of bounds")

    if buffer[offset] == 0:
        return "", 1

    end: int = offset
    for i, c in enumerate(buffer[offset:]):
        if c == 0:
            end = offset + i
            break

    if end == offset:
        raise ValueError("Non-null terminated string")

    return bytes(buffer[offset:end]).decode(), end - offset + 1


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


FROM_BYTES_BY_ID: list[None | Callable[[Any, int], tuple[ValueTypes, int]]] = [
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


def value_from_bytes(scs_value_type: int, buffer, offset: int = 0) -> tuple[ValueTypes, int]:
    if unpack_spec := UNPACK_SPEC_BY_ID[scs_value_type]:
        return unpack_from(f"={unpack_spec}", buffer, offset)[0], TYPE_SIZE_BY_ID[scs_value_type]
    if (deserializer := FROM_BYTES_BY_ID[scs_value_type]) is not None:
        return deserializer(buffer, offset)
    raise ValueError("invalid scs value type")


def value_storage_from_bytes(scs_value_type: int, buffer, offset: int = 0) -> tuple[tuple[bool, ValueTypes], int]:
    if offset == len(buffer):
        raise ValueError("offset out of bounds.")
    value, read = value_from_bytes(scs_value_type, buffer, offset + 1)
    return (buffer[offset] > 0, value), read + 1
