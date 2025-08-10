from __future__ import annotations
from typing import Callable, Any, TypeGuard, TypeVar
from dataclasses import dataclass, field
from struct import calcsize, unpack_from
from enum import Enum
from scssdk_dataclasses import TYPE_SIZE_BY_ID


class SCSValueType(Enum):
    SCS_VALUE_TYPE_INVALID = 0
    SCS_VALUE_TYPE_bool = 1
    SCS_VALUE_TYPE_s32 = 2
    SCS_VALUE_TYPE_u32 = 3
    SCS_VALUE_TYPE_u64 = 4
    SCS_VALUE_TYPE_float = 5
    SCS_VALUE_TYPE_double = 6
    SCS_VALUE_TYPE_fvector = 7
    SCS_VALUE_TYPE_dvector = 8
    SCS_VALUE_TYPE_euler = 9
    SCS_VALUE_TYPE_fplacement = 10
    SCS_VALUE_TYPE_dplacement = 11
    SCS_VALUE_TYPE_string = 12
    SCS_VALUE_TYPE_s64 = 13


VALUE_STORAGE_INITIALIZED: int = 0
VALUE_STORAGE_VALUE: int = 1
VALUE_STORAGE_VALUES: int = 1


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
    PADDING = 4
    position: SCSValueDVector = field(default_factory=SCSValueDVector)
    orientation: SCSValueEuler = field(default_factory=SCSValueEuler)

    @staticmethod
    def from_bytes(buffer, offset: int = 0) -> tuple[SCSValueDPlacement, int]:
        position, position_read = SCSValueDVector.from_bytes(buffer, offset)
        orientation, orientation_read = SCSValueEuler.from_bytes(buffer, offset + position_read)
        return SCSValueDPlacement(position, orientation), position_read + orientation_read + SCSValueDPlacement.PADDING


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


def dynamic_bool_vector_from_bytes(buffer, offset: int = 0) -> tuple[list[bool], int]:
    array_size: int = unpack_from("=I", buffer, offset)[0]
    offset += 4

    if array_size == 0:
        return [], 4

    bools: list[bool] = []
    byte: int = 0
    bit: int = 0
    for _ in range(array_size):
        if bit == 8:
            bit = 0
            byte += 1
        bools.append((buffer[offset + byte] & (1 << bit)) > 0)
        bit += 1
    return bools, byte + 1 + 4


type ValueTypes = (
    bool |
    int |
    float |
    SCSValueFVector |
    SCSValueDVector |
    SCSValueEuler |
    SCSValueFPlacement |
    SCSValueDPlacement |
    str |
    list
)


type ValueStorageTypes = (
    tuple[bool, ValueTypes] |
    tuple[bool, ValueTypes, int] |
    list[ValueTypes]
)


DESERIALIZER_BY_ID: list[Callable[[Any, int], tuple[ValueTypes, int]] | None] = [
    None,
    (lambda buffer, offset: (unpack_from("=?", buffer, offset)[0], TYPE_SIZE_BY_ID[1])),
    (lambda buffer, offset: (unpack_from("=i", buffer, offset)[0], TYPE_SIZE_BY_ID[2])),
    (lambda buffer, offset: (unpack_from("=I", buffer, offset)[0], TYPE_SIZE_BY_ID[3])),
    (lambda buffer, offset: (unpack_from("=Q", buffer, offset)[0], TYPE_SIZE_BY_ID[4])),
    (lambda buffer, offset: (unpack_from("=f", buffer, offset)[0], TYPE_SIZE_BY_ID[5])),
    (lambda buffer, offset: (unpack_from("=d", buffer, offset)[0], TYPE_SIZE_BY_ID[6])),
    SCSValueFVector.from_bytes,
    SCSValueDVector.from_bytes,
    SCSValueEuler.from_bytes,
    SCSValueFPlacement.from_bytes,
    SCSValueDPlacement.from_bytes,
    szstr_from_bytes,
    (lambda buffer, offset: (unpack_from("=q", buffer, offset)[0], TYPE_SIZE_BY_ID[13])),
]


def value_storage_from_bytes(
    scs_value_type: SCSValueType,
    buffer,
    offset: int = 0,
    array_size: int | None = None,
    dynamic_size: bool = False
) -> tuple[ValueStorageTypes, int]:
    if not (deserializer := DESERIALIZER_BY_ID[scs_value_type.value]):
        raise ValueError("Invalid scs value value type")

    if array_size is not None and dynamic_size:
        raise ValueError("'array_size' and 'dynamic_size' are mutually exclusive")
    if array_size is not None:
        if array_size <= 0:
            raise ValueError("'array_size' must be greater than 0")
        initialized: bool = unpack_from("=?", buffer, offset)[0]
        total_read = 1

        count: int = unpack_from("=I", buffer, offset + total_read)[0]
        total_read += 4

        array: list = []
        for _ in range(array_size):
            deserialized, read = deserializer(buffer, offset + total_read)
            array.append(deserialized)
            total_read += read
        return (initialized, array, count), total_read
    elif dynamic_size:
        if scs_value_type == SCSValueType.SCS_VALUE_TYPE_bool:
            array, read = dynamic_bool_vector_from_bytes(buffer, offset)
            return array, read

        array_size = unpack_from("=I", buffer, offset)[0]
        assert array_size is not None
        total_read: int = 4
        array: list = []
        for _ in range(array_size):
            value, read = deserializer(buffer, offset + total_read)
            array.append(value)
            total_read += read
        return array, total_read

    initialized: bool = unpack_from("=?", buffer, offset)[0]
    value, read = deserializer(buffer, offset + 1)
    return (initialized, value), 1 + read


T = TypeVar("T")


def value_storage_guard(storage: ValueStorageTypes, storage_type_instance: T) -> TypeGuard[tuple[bool, T]]:
    return (
        len(storage) == 2 and isinstance(storage[0], bool) and isinstance(storage[1], type(storage_type_instance))
    )


def value_array_storage_guard(storage: ValueStorageTypes, storage_type_instance: T) -> TypeGuard[tuple[bool, list[T], int]]:
    return (
        len(storage) == 3 and
        isinstance(storage[0], bool) and
        isinstance(storage[1], list) and
        all(isinstance(x, type(storage_type_instance)) for x in storage[1]) and
        isinstance(storage[2], int)
    )


def value_vector_storage_guard(storage: ValueStorageTypes, storage_type_instance: T) -> TypeGuard[list[T]]:
    return (
        isinstance(storage, list) and
        all(isinstance(x, type(storage_type_instance)) for x in storage)
    )
