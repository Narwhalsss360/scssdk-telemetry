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
        as_pascal += "_"
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


def fullprop(tabcount: int, field_type: str, field_name: str, field_default: str, propertry_type: str, property_name: str, getter: str, setter: str) -> str:
    tabstr: str = TAB_CHARS * tabcount
    return (
        f"{tabstr}private {field_type} {field_name} = {field_default};\n"
        f"{tabstr}public {propertry_type} {property_name}\n"
        f"{tabstr}{{\n"
        f"{tabstr}{TAB_CHARS}get {getter}\n"
        f"{tabstr}{TAB_CHARS}init {setter}\n"
        f"{tabstr}}}\n\n"
    )


def metadata_class(telemetries: list[Telemetry], tabcount: int = 1) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}public class Metadata\n"
        f"{tabstr}{{\n"
    )

    tabstr = TAB_CHARS * (tabcount + 1)

    not_a_channel_exception: str = "throw new InvalidOperationException(\"This property is only available for channels.\")"
    channel_getter = lambda field: f"=> TelemetryType == TelemetryType.Channel ? {field} : {not_a_channel_exception};"
    channel_setter = lambda field: f"=> {field} = TelemetryType == TelemetryType.Channel ? value : {not_a_channel_exception};"

    non_structure_exception: str = "throw new InvalidOperationException(\"This property is not available on structures.\")"
    non_structure_getter = lambda field: f"=> TelemetryType != TelemetryType.Structure ? {field} : {non_structure_exception};"
    non_structure_setter = lambda field: f"=> {field} = TelemetryType != TelemetryType.Structure ? value : {non_structure_exception};"

    out += (
        f"{tabstr}public TelemetryType TelemetryType {{ get; init; }}\n\n" +
        f"{tabstr}public TelemetryID ID {{ get; init; }}\n\n" +
        f"{tabstr}public bool ConstantSize {{ get; init; }}\n\n" +
        f"{tabstr}public UInt32 MasterOffset {{ get; init; }}\n\n" +
        f"{tabstr}public UInt32 StructureOffset {{ get; init; }}\n\n" +
        fullprop(tabcount + 1, "string", "_macro", "\"\"", "string", "Macro", non_structure_getter("_macro"), non_structure_setter("_macro")) +
        fullprop(tabcount + 1, "bool", "_indexed", "false", "bool", "Indexed", non_structure_getter("_indexed"), non_structure_setter("_indexed")) +
        fullprop(tabcount + 1, "UInt32", "_maxCount", "0", "UInt32", "MaxCount", channel_getter("_maxCount"), channel_setter("_maxCount")) +
        fullprop(tabcount + 1, "bool", "_trailerChannel", "false", "bool", "TrailerChannel", channel_getter("_trailerChannel"), channel_setter("_trailerChannel")) +
        fullprop(tabcount + 1, "SCSValueType", "_valueType", "SCSValueType.SCS_VALUE_TYPE_INVALID", "SCSValueType", "SCSValueType", channel_getter("_valueType"), channel_setter("_valueType")) +
        fullprop(tabcount + 1, "bool", "_customChannel", "false", "bool", "CustomChannel", channel_getter("_customChannel"), channel_setter("_customChannel")) +
        f"{tabstr}public static Metadata ByID(TelemetryID id) => Array.Find(METADATA, metadata => metadata.ID == id) ?? throw new ArgumentException(\"Metadata not found\", nameof(id));\n\n"
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

