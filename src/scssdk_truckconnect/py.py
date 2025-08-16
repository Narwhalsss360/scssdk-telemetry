from pathlib import Path
from types import TracebackType
from scssdk_telemetry.scssdk_dataclasses import TYPE_MACROS_BY_ID, Event, EventAttribute, SCS_TELEMETRY_trailers_count
from scssdk_truckconnect.truckconnect import Telemetry, master_telemetry, name, telemetries, INVALID_TELEMETRY_ID, trailer_structure_telemetry, configuration_trailer_structure_telemetry
from scssdk_truckconnect.csharp import pascalify_snake


OUTPUT_FOLDER: Path = Path("generated.gitignore/")
TAB_CHARS: str = " " * 4


PY_TYPE_BY_ID: list[str] = [
    "",
    "bool",
    "int",
    "int",
    "int",
    "float",
    "float",
    "SCSValueFVector",
    "SCSValueDVector",
    "SCSValueEuler",
    "SCSValueFPlacement",
    "SCSValueDPlacement",
    "str",
    "int"
]


def annotation(telemetry_or_attr: Telemetry | EventAttribute) -> str:
    if isinstance(telemetry_or_attr, Telemetry):
        if not telemetry_or_attr.is_channel:
            return pascalify_snake(name(telemetry_or_attr))
        if telemetry_or_attr.as_channel.indexed:
            return f"tuple[bool, list[{PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]}], int]"
        return f"tuple[bool, {PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]}]"

    if telemetry_or_attr.indexed:
        return f"list[{PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]}]"
    return f"tuple[bool, {PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]}]"


def default_factory(telemetry_or_attr: Telemetry | EventAttribute) -> str:
    if isinstance(telemetry_or_attr, Telemetry):
        if not telemetry_or_attr.is_channel:
            return pascalify_snake(name(telemetry_or_attr))
        if telemetry_or_attr.as_channel.indexed:
            return f"lambda: (False, [{PY_TYPE_BY_ID[telemetry_or_attr.as_channel.scs_type_id]}() for _ in range({telemetry_or_attr.as_channel.max_count})], 0)"
        return f"lambda: (False, {PY_TYPE_BY_ID[telemetry_or_attr.as_channel.scs_type_id]}())"

    if telemetry_or_attr.indexed:
        return "lambda: []"
    return f"lambda: (False, {PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]}())"


def deserializer_for(telemetry_or_attr: Telemetry | EventAttribute, buffer: str = "buffer", offset: str = "offset") -> str:
    if isinstance(telemetry_or_attr, EventAttribute):
        if telemetry_or_attr.indexed:
            return f"value_vector_storage_from_bytes(SCSValueType.{TYPE_MACROS_BY_ID[telemetry_or_attr.scs_type_id]}, {buffer}, {offset})"
        else:
            return f"value_storage_from_bytes(SCSValueType.{TYPE_MACROS_BY_ID[telemetry_or_attr.scs_type_id]}, {buffer}, {offset})"

    if telemetry_or_attr.is_channel:
        if telemetry_or_attr.indexed:
            return f"value_array_storage_from_bytes(SCSValueType.{TYPE_MACROS_BY_ID[telemetry_or_attr.scs_type_id]}, {telemetry_or_attr.max_count}, {buffer}, {offset})"
        return f"value_storage_from_bytes(SCSValueType.{TYPE_MACROS_BY_ID[telemetry_or_attr.scs_type_id]}, {buffer}, {offset})"

    return f"{pascalify_snake(name(telemetry_or_attr))}.from_bytes({buffer}, {offset})"


def is_storage_type_guard(telemetry_or_attr: Telemetry | EventAttribute, identifier: str) -> str:
    if isinstance(telemetry_or_attr, EventAttribute):
        if telemetry_or_attr.indexed:
            return f"is_value_vector_storage({identifier}, {PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]})"
        else:
            return f"is_value_storage({identifier}, {PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]})"

    if telemetry_or_attr.is_channel:
        if telemetry_or_attr.indexed:
            return f"is_value_array_storage({identifier}, {PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]})"
        return f"is_value_storage({identifier}, {PY_TYPE_BY_ID[telemetry_or_attr.scs_type_id]})"

    return f"isinstance({identifier}, {pascalify_snake(name(telemetry_or_attr))})"


def telemetry_id() -> str:
    out: str = (
        "import enum\n"
        "\n\n"
        "class TelemetryID(enum.Enum):\n"
    )
    for i, telemetry in enumerate(telemetries()):
        out += f"{TAB_CHARS}{pascalify_snake(name(telemetry))} = {i}\n"
    out += f"{TAB_CHARS}Invalid = {INVALID_TELEMETRY_ID}\n"
    return out


def master_structure() -> str:
    out: str = (
        "from __future__ import annotations\n"
        "from dataclasses import dataclass, field\n"
        "from scssdk_telemetry.scssdk_dataclasses import SCS_TELEMETRY_trailers_count\n"
        "from truckconnect.value_storage import (\n"
        f"{TAB_CHARS}SCSValueType,\n"
        f"{TAB_CHARS}BufferType,\n"
        f"{TAB_CHARS}value_storage_from_bytes,\n"
        f"{TAB_CHARS}value_array_storage_from_bytes,\n"
        f"{TAB_CHARS}value_vector_storage_from_bytes,\n"
        f"{TAB_CHARS}is_value_storage,\n"
        f"{TAB_CHARS}is_value_array_storage,\n"
        f"{TAB_CHARS}is_value_vector_storage,\n"
        f"{TAB_CHARS}SCSValueFVector,\n"
        f"{TAB_CHARS}SCSValueFPlacement,\n"
        f"{TAB_CHARS}SCSValueDPlacement\n"
        ")\n"
        "\n\n"
    )

    dependency_sorted: list[Telemetry] = list(filter(
        lambda telemetry: telemetry.is_structure or telemetry.is_event_info,
        telemetries()[::-1]
    ))
    dependency_sorted.sort(key=lambda telemetry: 3 if telemetry == master_telemetry() else -telemetry.rank)
    for i, telemetry in enumerate(dependency_sorted):
        out += (
            "@dataclass\n"
            f"class {pascalify_snake(name(telemetry))}:\n"
        )

        if telemetry.is_structure:
            for child in telemetry.as_structure.children:
                if child in (trailer_structure_telemetry(), configuration_trailer_structure_telemetry()):
                    out += f"{TAB_CHARS}{name(child)}: list[{annotation(child)}] = field(default_factory=lambda: [{pascalify_snake(name(child))}() for _ in range(SCS_TELEMETRY_trailers_count)])\n"
                else:
                    out += f"{TAB_CHARS}{name(child)}: {annotation(child)} = field(default_factory={default_factory(child)})\n"

            out += (
                "\n"
                f"{TAB_CHARS}@staticmethod\n"
                f"{TAB_CHARS}def from_bytes(buffer: BufferType, offset: int = 0) -> tuple[{pascalify_snake(name(telemetry))}, int]:\n"
                f"{TAB_CHARS * 2}{name(telemetry)}: {pascalify_snake(name(telemetry))} = {pascalify_snake(name(telemetry))}()\n"
                f"{TAB_CHARS * 2}total_read: int = 0\n"
            )

            for child in telemetry.as_structure.children:
                if child in (trailer_structure_telemetry(), configuration_trailer_structure_telemetry()):
                    out += (
                        f"{TAB_CHARS * 2}for _ in range(SCS_TELEMETRY_trailers_count):\n"
                        f"{TAB_CHARS * 3}deserialized, read = {deserializer_for(child, offset="offset + total_read")}\n"
                        f"{TAB_CHARS * 3}{name(telemetry)}.{name(child)}.append(deserialized)\n"
                        f"{TAB_CHARS * 3}total_read += read\n\n"
                    )
                else:
                    out += (
                        f"{TAB_CHARS * 2}deserialized, read = {deserializer_for(child, offset="offset + total_read")}\n"
                        f"{TAB_CHARS * 2}assert {is_storage_type_guard(child, "deserialized")}\n"
                        f"{TAB_CHARS * 2}{name(telemetry)}.{name(child)} = deserialized\n"
                        f"{TAB_CHARS * 2}total_read += read\n\n"
                    )
            out += f"{TAB_CHARS * 2}return {name(telemetry)}, total_read"
        else: # telemetry.is_event_info
            for attribute in telemetry.as_event_info.attributes:
                out += f"{TAB_CHARS}{name(attribute)}: {annotation(attribute)} = field(default_factory={default_factory(attribute)})\n"

            out += (
                "\n"
                f"{TAB_CHARS}@staticmethod\n"
                f"{TAB_CHARS}def from_bytes(buffer: BufferType, offset: int = 0) -> tuple[{pascalify_snake(name(telemetry))}, int]:\n"
                f"{TAB_CHARS * 2}{name(telemetry)}: {pascalify_snake(name(telemetry))} = {pascalify_snake(name(telemetry))}()\n"
                f"{TAB_CHARS * 2}total_read: int = 0\n"
            )

            for attribute in telemetry.as_event_info.attributes:
                out += (
                    f"{TAB_CHARS * 2}deserialized, read = {deserializer_for(attribute, offset="offset + total_read")}\n"
                    f"{TAB_CHARS * 2}assert {is_storage_type_guard(attribute, "deserialized")}\n"
                    f"{TAB_CHARS * 2}{name(telemetry)}.{name(attribute)} = deserialized\n"
                    f"{TAB_CHARS * 2}total_read += read\n\n"
                )
            out += f"{TAB_CHARS * 2}return {name(telemetry)}, total_read"
        if i != len(dependency_sorted) - 1:
            out += "\n\n"
    return out


def generate() -> dict[str, str]:
    return {
        "telemetry_id.py": telemetry_id(),
        "master_structure.py": master_structure()
    }


def main() -> None:
    print(f"Loaded {len(telemetries())} telemetries.")
    if not OUTPUT_FOLDER.exists():
        OUTPUT_FOLDER.mkdir()
    files: dict[str, str] = generate()
    for file_name, text in files.items():
        with open(OUTPUT_FOLDER.joinpath(file_name), "w", encoding="utf-8") as f:
            f.write(text)
            print(f"Generated {text.count('\n')} lines {file_name}.")


if __name__ == "__main__":
    main()
