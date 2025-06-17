from pathlib import Path
from truckconnect import (
    Telemetry,
    name,
    is_custom_channel,
    is_attribute,
    TelemetryType,
    build_telemetries,
    master_telemetry,
    trailer_structure_telemetry,
    configuration_trailer_structure_telemetry,
)


OUTPUT_FOLDER: Path = Path("generated.gitignore/")
TAB_CHARS: str = "\t"


def pascalify_snake(identifier: str) -> str:
    if not identifier:
        return identifier

    as_pascal: str = identifier[0].upper()

    snaked: bool = False
    for c in identifier[1:]:
        if snaked:
            as_pascal += c.upper()
            snaked = False
            continue
        if c == "_":
            snaked = True
            continue
        as_pascal += c

    if snaked: #Add trailing underscore
        c += "_"
    return as_pascal


def telemetry_id_enum(telemetries: list[Telemetry], tabcount: int = 1) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}public enum TelemetryID {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += (
            f"{tabstr}{TAB_CHARS}{pascalify_snake(name(telemetry))}"
        )
        if i != len(telemetries) - 1:
            out += ","
        out += "\n"

    out += (
        f"{tabstr}}}\n"
    )
    return out


def generate(telemetries: list[Telemetry]) -> dict[str, str]:
    return {
        "TelemetryID.cs": telemetry_id_enum(telemetries)
    }


def main() -> None:
    telemetries: list[Telemetry] = build_telemetries()
    print(f"Loaded {len(telemetries)} telemetries.")
    if not OUTPUT_FOLDER.exists():
        OUTPUT_FOLDER.mkdir()
    files: dict[str, str] = generate(telemetries)
    for file_name, text in files.items():
        with open(OUTPUT_FOLDER.joinpath(file_name), "w", encoding="utf-8") as f:
            f.write(text)
            print(f"Generated {text.count('\n')} lines {file_name}.")


if __name__ == "__main__":
    if retval := main():
        print(retval)

