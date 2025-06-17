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
    TYPE_MACROS_BY_ID,
    Channel
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
        f"{tabstr}public enum TelemetryID\n"
        f"{tabstr}{{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += (
            f"{tabstr}{TAB_CHARS}{pascalify_snake(name(telemetry))},\n"
        )

    out += (
        f"{tabstr}{TAB_CHARS}Invalid = 255\n"
        f"{tabstr}}}\n"
    )
    return out


def telemetry_type_enum(tabcount: int = 1) -> str:
    tabstr: str = TAB_CHARS * tabcount
    return (
        f"{tabstr}public enum TelemetryType\n"
        f"{tabstr}{{\n"
        f"{tabstr}{TAB_CHARS}Structure,\n"
        f"{tabstr}{TAB_CHARS}EventInfo,\n"
        f"{tabstr}{TAB_CHARS}Channel\n"
        f"{tabstr}}}\n"
    )


def cs_value(value: TelemetryType | bool) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, TelemetryType):
        match value:
            case TelemetryType.Structure:
                return "TelemetryType.Structure"
            case TelemetryType.EventInfo:
                return "TelemetryType.EventInfo"
            case TelemetryType.Channel:
                return "TelemetryType.Channel"

    assert False, "Unknown type."


def cs_scs_value_type(channel: Channel) -> str:
    return f"TruckConnect.SCSValueType.{TYPE_MACROS_BY_ID[channel.scs_type_id]}"


def metadata_class(telemetries: list[Telemetry], tabcount: int = 1) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}public class Metadata\n"
        f"{tabstr}{{\n"
    )

    tabstr = TAB_CHARS * (tabcount + 1)
    out += (
        f"{tabstr}public TelemetryID ID {{ get; init; }}\n\n"
        f"{tabstr}public TelemetryType TelemetryType {{ get; init; }}\n\n"
        f"{tabstr}public bool ConstantSize {{ get; init; }}\n\n"
        f"{tabstr}public UInt32 MasterOffset {{ get; init; }}\n\n"
        f"{tabstr}public UInt32 StructureOffset {{ get; init; }}\n\n"
        f"{tabstr}public string? Macro {{ get; init; }}\n\n"
        f"{tabstr}public bool? Indexed {{ get; init; }}\n\n"
        f"{tabstr}public UInt32? MaxCount {{ get; init; }}\n\n"
        f"{tabstr}public bool? TrailerChannel {{ get; init; }}\n\n"
        f"{tabstr}public SCSValueType? SCSValueType {{ get; init; }}\n\n"
        f"{tabstr}public bool? CustomChannel {{ get; init; }}\n\n"
        f"{tabstr}public static Metadata? ByID(TelemetryID id) => Array.Find(METADATA, metadata => metadata.id == id);\n\n"
    )

    out += (
        f"{tabstr}public static readonly Metadata[] METADATA =\n"
        f"{tabstr}[\n"
    )
    for i, telemetry in enumerate(telemetries):
        out += (
            f"{tabstr}{TAB_CHARS}new() {{ "
        )

        out += (
            f"ID = TelemetryID.{pascalify_snake(name(telemetry))}, "
            f"TelemetryType = {cs_value(telemetry.telemetry_type)}, "
            f"ConstantSize = {cs_value(telemetry.constant_size)}, "
        )

        if telemetry.is_structure:
            if telemetry == master_telemetry():
                out += (
                    f"MasterOffset = 0, "
                    f"StructureOffset = 0 "
                )
            else:
                out += (
                    f"MasterOffset = 0, /*?*/ "
                    f"StructureOffset = 0 /*?*/ "
                )
        elif telemetry.is_event_info:
            out += (
                f"MasterOffset = 0, /*?*/ "
                f"StructureOffset = 0, /*?*/ "
                f"Macro = \"{telemetry.as_event_info.expansion}\" "
            )
        else: #=> telemetry.is_channel
            out += (
                f"MasterOffset = 0, /*?*/ "
                f"StructureOffset = 0, /*?*/ "
                f"Macro = \"{telemetry.as_channel.expansion}\", "
                f"Indexed = {cs_value(telemetry.as_channel.indexed)}, "
                f"MaxCount = {telemetry.as_channel.max_count} ,"
                f"TrailerChannel = {cs_value(telemetry.as_channel.is_trailer_channel)}, "
                f"SCSValueType = {cs_scs_value_type(telemetry.as_channel)}, "
                f"CustomChannel = {cs_value(is_custom_channel(telemetry))}"
            )

        out += "}"
        if i != len(telemetries) - 1:
            out += ","
        out += "\n"
    out += (
        f"{tabstr}];\n"
    )


    out += (
        f"{TAB_CHARS * tabcount}}}\n"
    )
    return out


def generate(telemetries: list[Telemetry]) -> dict[str, str]:
    return {
        "TelemetryID.cs": telemetry_id_enum(telemetries),
        "TelemetryType.cs": telemetry_type_enum(),
        "Metadata.cs": metadata_class(telemetries)
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

