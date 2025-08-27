from pathlib import Path

from scssdk_telemetry.scssdk_dataclasses import EventAttribute, SCS_TELEMETRY_trailers_count
from scssdk_truckconnect.csharp import pascalify_snake
from . import cpp
from . import csharp
from . import py
from .truckconnect import Telemetry, configuration_trailer_structure_telemetry, name, telemetries, master_telemetry, trailer_structure_telemetry


OUTPUT_FOLDER: Path = Path("generated.gitignore/")
TAB_CHARS: str = " " * 4


def storage(telemetry: Telemetry | EventAttribute) -> str:
    cpp_type: str
    if isinstance(telemetry, EventAttribute):
        cpp_type = cpp.storage(telemetry)[0]
    else:
        cpp_type = cpp.type_name(telemetry) if telemetry.is_structure or telemetry.is_event_info else cpp.storage(telemetry)[0]
    return f"`{cpp_type}` | `{csharp.storage(telemetry)}` | `{py.annotation(telemetry)}`"


def telemetry_types_doc() -> str:
    return (
        "# Telemetry Types\n"
        "\n"
        "- Structure\n"
        "- EventInfo\n"
        "- Channel\n"
        "\n"
    )


def telemetries_doc() -> str:
    out: str = "# Telemetries\n\n"
    for telemetry in telemetries():
        out += f"- {pascalify_snake(name(telemetry))}: {telemetry.telemetry_type.name} = {telemetry.id}\n"
    out += "\n"
    return out


def master_structure_docs() -> str:
    def recurse(tabcount: int, telemetry: Telemetry | EventAttribute) -> str:
        tabstr: str = f"{TAB_CHARS * tabcount}- "
        if isinstance(telemetry, EventAttribute):
            out: str = f"{tabstr}{pascalify_snake(name(telemetry))}: {storage(telemetry)}\n"
        elif telemetry.is_structure:
            if telemetry == trailer_structure_telemetry():
                out: str = f"{tabstr}{pascalify_snake(name(telemetry))} × {SCS_TELEMETRY_trailers_count}: {storage(telemetry)}\n"
            else:
                out: str = f"{tabstr}{pascalify_snake(name(telemetry))}: {storage(telemetry)}\n"

            for child in telemetry.as_structure.children:
                out += recurse(tabcount + 1, child)
        elif telemetry.is_event_info:
            if telemetry == configuration_trailer_structure_telemetry():
                out: str = f"{tabstr}{pascalify_snake(name(telemetry))} × {SCS_TELEMETRY_trailers_count}: {storage(telemetry)}\n"
            else:
                out: str = f"{tabstr}{pascalify_snake(name(telemetry))}: {storage(telemetry)}\n"

            for attribute in telemetry.as_event_info.attributes:
                out += recurse(tabcount + 1, attribute)
        else:  # => is_channel = True
            out = f"{tabstr}{pascalify_snake(name(telemetry))}{f" × {telemetry.as_channel.max_count}" if telemetry.as_channel.indexed else ""}: {storage(telemetry)}\n"

        return out

    out: str = (
        "# Master Structure\n"
        "\n"
        "_Type Language:_ C++ | C# | Python\n"
        "\n"
    )
    out += recurse(0, master_telemetry())
    return out


def generate() -> dict[str, str]:
    return {
        "Telemetry Types.md": telemetry_types_doc(),
        "Telemetries.md": telemetries_doc(),
        "Master Structure.md": master_structure_docs()
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
    if retval := main():
        print(retval)
