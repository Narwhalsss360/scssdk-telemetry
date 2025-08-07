from pathlib import Path
from truckconnect import name, telemetries
from csharp import pascalify_snake


OUTPUT_FOLDER: Path = Path("generated.gitignore/")
TAB_CHARS: str = "\t"

def telemetry_id() -> str:
    out: str = (
        "import enum\n"
        "\n\n"
        "class TelemetryID(enum.Enum):\n"
    )
    for i, telemetry in enumerate(telemetries()):
        out += f"{TAB_CHARS}{pascalify_snake(name(telemetry))} = {i}\n"
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