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


def generate() -> dict[str, str]:
    return {
        "telemetry_id.py": telemetry_id()
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
