from typing import Iterator
from os.path import join
from scssdk_dataclasses import (
    Telemetry,
    Configuration,
    TelemetryEventAttribute,
    TYPE_MACROS_BY_ID,
    SCS_TELEMETRY_trailers_count,
    load,
    TYPE_SIZE_BY_ID,
    TYPES_BY_ID,
    CPP_INVALID_TYPE,
    SHORT_TYPENAME_TO_TYPE
)


VALUE_STORAGE_STRUCT_NAME: str = "value_storage"
VALUE_ARRAY_STORAGE_STRUCT_NAME: str = "value_array_storage"
TRAILER_DATA_STRUCT_NAME: str = "trailer_data"
TRAILER_DATA_INSTANCE_NAME: str = "trailers"
STORE_STRUCT_NAME: str = "game_data_store"
STORE_INSTANCE_NAME: str = "game_data"
STORE_FUNCTION_NAME: str = "store"
TRAILER_STORE_FUNCTION_NAME: str = "trailer_store"
CONTEXT_STORE_NAME: str = "context_store"
CONTEXTS_VECTOR_NAME: str = "contexts"
TELEMETRY_IDS_ENUM_NAME: str = "telemetry_id"

NON_VALUE_TYPE_BY_ID: list[str] = TYPES_BY_ID


def cpp_containers() -> str:
    return (
        "template <typename T>\n"
        f"struct {VALUE_STORAGE_STRUCT_NAME} {{\n"
        "\tT value = T();\n"
        "\tbool initialized = false;\n"
        "};\n"
        "\n"
        "template <typename T, size_t max_count>\n"
        f"struct {VALUE_ARRAY_STORAGE_STRUCT_NAME} {{\n"
        "\tstd::array<T, max_count> values = std::array<T, max_count>();\n"
        "\tbool initialized = false;\n"
        "\tuint32_t size = 0;\n"
        "};\n"
        "\n"
    )


def cpp_store_struct(telemetries: list[Telemetry]) -> str:
    out: str = f"struct {TRAILER_DATA_STRUCT_NAME} {{\n"
    for trailer_telemetry in filter(lambda t: t.is_trailer_channel, telemetries):
        if trailer_telemetry.indexed:
            container_type: str = VALUE_ARRAY_STORAGE_STRUCT_NAME
            template_args: str = f"{NON_VALUE_TYPE_BY_ID[trailer_telemetry.scs_type_id]}, {trailer_telemetry.max_count}"
        else:
            container_type: str = VALUE_STORAGE_STRUCT_NAME
            template_args: str = NON_VALUE_TYPE_BY_ID[trailer_telemetry.scs_type_id]
        out += f"\t{container_type}<{template_args}> {trailer_telemetry.simple_name};\n"

    out += f"}};\n\nstruct {STORE_STRUCT_NAME} {{\n"

    for telemetry in filter(
        lambda t: not t.is_trailer_channel and not t.is_event, telemetries
    ):
        if telemetry.indexed:
            container_type: str = VALUE_ARRAY_STORAGE_STRUCT_NAME
            template_args: str = (
                f"{NON_VALUE_TYPE_BY_ID[telemetry.scs_type_id]}, {telemetry.max_count}"
            )
        else:
            container_type: str = VALUE_STORAGE_STRUCT_NAME
            template_args: str = NON_VALUE_TYPE_BY_ID[telemetry.scs_type_id]
        out += f"\t{container_type}<{template_args}> {telemetry.simple_name};\n"
    out += f"\tstd::array<{TRAILER_DATA_STRUCT_NAME}, {SCS_TELEMETRY_trailers_count}> {TRAILER_DATA_INSTANCE_NAME};\n"
    out += "};\n\n"
    return out


def context_store() -> str:
    return (
        f"struct {CONTEXT_STORE_NAME} {{\n"
        "\tuint8_t id;\n"
        "\tvoid* pointer;\n"
        "\tuint32_t size;\n"
        "\tuint32_t index;\n"
        "\tint8_t trailer_index;\n"
        "\n"
        f"\t{CONTEXT_STORE_NAME}(uint8_t id, void* pointer, uint32_t size, uint32_t index = SCS_U32_NIL, int8_t trailer_index = -1);\n"
        "};\n"
        "\n"
        f"extern std::vector<{CONTEXT_STORE_NAME}> {CONTEXTS_VECTOR_NAME};\n"
    )


def context_store_definition() -> str:
    return (
        f"{CONTEXT_STORE_NAME}::{CONTEXT_STORE_NAME}(uint8_t id, void* pointer, uint32_t size, uint32_t index, int8_t trailer_index)\n"
        "\t: id(id), pointer(pointer), size(size), index(index), trailer_index(trailer_index) { }\n"
    )


def registrations_for(
    telemetries: list[Telemetry],
    trailer_count: int = SCS_TELEMETRY_trailers_count,
    tabs: int = 1,
) -> Iterator[str]:
    tab_str: str = "\t" * tabs
    out: str
    for telemetry in telemetries:
        if telemetry.is_event:
            continue
        function: str = "register_for_channel"
        expansion: str = telemetry.expansion
        type_macro: str = TYPE_MACROS_BY_ID[telemetry.scs_type_id]
        callback: str = (
            f"{STORE_FUNCTION_NAME}<{NON_VALUE_TYPE_BY_ID[telemetry.scs_type_id]}, {telemetry.max_count}>"
            if telemetry.indexed
            else f"{STORE_FUNCTION_NAME}<{NON_VALUE_TYPE_BY_ID[telemetry.scs_type_id]}>"
        )
        store_pointer: str = f"&{STORE_INSTANCE_NAME}.{telemetry.simple_name}"

        if telemetry.is_trailer_channel:
            if telemetry.indexed:
                store_pointer = f"&{STORE_INSTANCE_NAME}.{TRAILER_DATA_INSTANCE_NAME}[t].{telemetry.simple_name}"
                out = (
                    f'{tab_str}char {telemetry.macro}_expansion[] = "{expansion.replace("trailer", "trailer.0")}";\n'
                    f"{tab_str}char& {telemetry.macro}_trailer_index_char = {telemetry.macro}_expansion[8];\n"
                    f"{tab_str}for (scs_u32_t t = 0; t < {trailer_count}; t++) {{\n"
                    f"{tab_str}\t{telemetry.macro}_trailer_index_char = '0' + t;\n"
                    f"{tab_str}\tfor(scs_u32_t i = 0; i < {telemetry.max_count}; i++) {{\n"
                    f"{tab_str}\t\t{CONTEXTS_VECTOR_NAME}.push_back({{ {telemetry.id}, {store_pointer}, {TYPE_SIZE_BY_ID[telemetry.scs_type_id]}, i, static_cast<int8_t>(t) }});\n"
                    f"{tab_str}\t\t{function}({telemetry.macro}_expansion, i, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, reinterpret_cast<void*>({CONTEXTS_VECTOR_NAME}.size() - 1));\n"
                    f"{tab_str}\t}}\n"
                    f"{tab_str}}}\n"
                )
            else:
                store_pointer = f"&{STORE_INSTANCE_NAME}.{TRAILER_DATA_INSTANCE_NAME}[t].{telemetry.simple_name}"
                out = (
                    f'{tab_str}char {telemetry.macro}_expansion[] = "{expansion.replace("trailer", "trailer.0")}";\n'
                    f"{tab_str}char& {telemetry.macro}_trailer_index_char = {telemetry.macro}_expansion[8];\n"
                    f"{tab_str}for (scs_u32_t t = 0; t < {trailer_count}; t++) {{\n"
                    f"{tab_str}\t{telemetry.macro}_trailer_index_char = '0' + t;\n"
                    f"{tab_str}\t{CONTEXTS_VECTOR_NAME}.push_back({{ {telemetry.id}, {store_pointer}, {TYPE_SIZE_BY_ID[telemetry.scs_type_id]}, SCS_U32_NIL, static_cast<int8_t>(t) }});\n"
                    f"{tab_str}\t{function}({telemetry.macro}_expansion, SCS_U32_NIL, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, reinterpret_cast<void*>({CONTEXTS_VECTOR_NAME}.size() - 1));\n"
                    f"{tab_str}}}\n"
                )
        else:
            if telemetry.indexed:
                out = (
                    f"{tab_str}for (scs_u32_t i = 0; i < {telemetry.max_count}; i++) {{\n"
                    f"{tab_str}\t{CONTEXTS_VECTOR_NAME}.push_back({{ {telemetry.id}, {store_pointer}, {TYPE_SIZE_BY_ID[telemetry.scs_type_id]}, i }});\n"
                    f"{tab_str}\t{function}({telemetry.macro}, i, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, reinterpret_cast<void*>({CONTEXTS_VECTOR_NAME}.size() - 1));\n"
                    f"{tab_str}}}\n"
                )
            else:
                out = (
                    f"{tab_str}{CONTEXTS_VECTOR_NAME}.push_back({{ {telemetry.id}, {store_pointer}, {TYPE_SIZE_BY_ID[telemetry.scs_type_id]}, SCS_U32_NIL }});\n"
                    f"{tab_str}{function}({telemetry.macro}, SCS_U32_NIL, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, reinterpret_cast<void*>({CONTEXTS_VECTOR_NAME}.size() - 1));\n"
                )

        yield out


def value_storage_size(value_type_size: int) -> int:
    return value_type_size + 1


def value_array_storage_size(value_type_size: int, count: int) -> int:
    return value_type_size * count + 1 + 4


def trailer_data_size(telemetries: list[Telemetry]) -> int:
    size: int = 0
    for telemetry in telemetries:
        if not telemetry.is_trailer_channel:
            continue
        if telemetry.indexed:
            size += value_array_storage_size(
                TYPE_SIZE_BY_ID[telemetry.scs_type_id], telemetry.max_count
            )
        else:
            size += value_storage_size(TYPE_SIZE_BY_ID[telemetry.scs_type_id])

    return size


def store_size(telemetries: list[Telemetry]) -> int:
    size: int = 0
    for telemetry in telemetries:
        if telemetry.is_trailer_channel or telemetry.is_event:
            continue
        if telemetry.indexed:
            size += value_array_storage_size(
                TYPE_SIZE_BY_ID[telemetry.scs_type_id], telemetry.max_count
            )
        else:
            size += value_storage_size(TYPE_SIZE_BY_ID[telemetry.scs_type_id])

    return size + SCS_TELEMETRY_trailers_count * trailer_data_size(telemetries)


def trailer_data_offset(telemetries: list[Telemetry]) -> int:
    offset: int = 0
    for telemetry in telemetries:
        if telemetry.is_trailer_channel or telemetry.is_event:
            continue
        if telemetry.indexed:
            offset += value_array_storage_size(
                TYPE_SIZE_BY_ID[telemetry.scs_type_id], telemetry.max_count
            )
        else:
            offset += value_storage_size(TYPE_SIZE_BY_ID[telemetry.scs_type_id])
    return offset


def trailer_data_offset_of(
    telemetries: list[Telemetry], telemetry: Telemetry
) -> tuple[int, int, int]:
    if not telemetry.is_trailer_channel:
        raise ValueError("Telemetry is not a trailer channel")

    offset: int = 0
    for other in telemetries:
        if not other.is_trailer_channel or other.is_event:
            continue
        if other.id == telemetry.id:
            break
        if other.indexed:
            offset += value_array_storage_size(
                TYPE_SIZE_BY_ID[other.scs_type_id], other.max_count
            )
        else:
            offset += value_storage_size(TYPE_SIZE_BY_ID[other.scs_type_id])

    count: int = telemetry.max_count if telemetry.indexed else 1
    initialized_offset: int = offset + (count * TYPE_SIZE_BY_ID[telemetry.scs_type_id])
    size_offset: int = initialized_offset + 1
    return offset, initialized_offset, size_offset


def offsets_of(
    telemetries: list[Telemetry], telemetry: Telemetry, trailer_index: int = -1
) -> tuple[int, int, int]:
    offset: int = 0
    if telemetry.is_trailer_channel or trailer_index != -1:
        if not (0 <= trailer_index <= SCS_TELEMETRY_trailers_count):
            raise IndexError(
                f"trailer_index must be within [0, {SCS_TELEMETRY_trailers_count})"
            )

        origin: int = (
            trailer_data_offset(telemetries)
            + trailer_data_size(telemetries) * trailer_index
        )
        return tuple(
            origin + offset for offset in trailer_data_offset_of(telemetries, telemetry)
        )

    for other in filter(
        lambda t: not (t.is_trailer_channel or t.is_event), telemetries
    ):
        if other.id == telemetry.id:
            break
        if other.indexed:
            offset += value_array_storage_size(
                TYPE_SIZE_BY_ID[other.scs_type_id], other.max_count
            )
        else:
            size: int = value_storage_size(TYPE_SIZE_BY_ID[other.scs_type_id])
            offset += size

    count: int = telemetry.max_count if telemetry.indexed else 1
    initialized_offset: int = offset + (count * TYPE_SIZE_BY_ID[telemetry.scs_type_id])
    size_offset: int = initialized_offset + 1
    return offset, initialized_offset, size_offset


def telemetry_id_by_enum(telemetry: Telemetry) -> str:
    return f"{TELEMETRY_IDS_ENUM_NAME}::{telemetry.simple_name}"


def max_count_function(telemetries: list[Telemetry]) -> str:
    out: str = (
        f"constexpr const uint32_t max_count({TELEMETRY_IDS_ENUM_NAME} id) {{\n"
        "\treturn\n"
    )

    indexed: list[Telemetry] = list(filter(lambda t: t.indexed, telemetries))
    for i, telemetry in enumerate(indexed):
        out += f"\t\tid == {telemetry_id_by_enum(telemetry)} ? {telemetry.max_count} :"
        if i == len(indexed) - 1:
            out += " 0;"

        out += "\n"

    out += "}\n"
    return out


def is_event_function(telemetries: list[Telemetry]) -> str:
    out: str = (
        f"constexpr const bool is_event({TELEMETRY_IDS_ENUM_NAME} id) {{\n\treturn\n"
    )

    events: list[Telemetry] = list(filter(lambda t: t.is_event, telemetries))
    for i, telemetry in enumerate(events):
        out += f"\t\tid == {telemetry_id_by_enum(telemetry)} ? true :"
        if i == len(events) - 1:
            out += " false;"

        out += "\n"

    out += "}\n"
    return out


def is_trailer_channel_function(telemetries: list[Telemetry]) -> str:
    out: str = (
        f"constexpr const bool is_trailer_channel({TELEMETRY_IDS_ENUM_NAME} id) {{\n"
        "\treturn\n"
    )

    trailer_channels: list[Telemetry] = list(
        filter(lambda t: t.is_trailer_channel, telemetries)
    )
    for i, telemetry in enumerate(trailer_channels):
        out += f"\t\tid == {telemetry_id_by_enum(telemetry)} ? true :"
        if i == len(trailer_channels) - 1:
            out += " false;"

        out += "\n"

    out += "}\n"
    return out


def type_id_of_function(telemetries: list[Telemetry]) -> str:
    out: str = (
        f"constexpr const scs_value_type_t type_id_of({TELEMETRY_IDS_ENUM_NAME} id) {{\n"
        "\treturn\n"
    )

    indexed: list[Telemetry] = list(filter(lambda t: not t.is_event, telemetries))
    for i, telemetry in enumerate(indexed):
        out += f"\t\tid == {telemetry_id_by_enum(telemetry)} ? {telemetry.scs_type_id} :"
        if i == len(indexed) - 1:
            out += " 0;"

        out += "\n"

    out += "}\n"
    return out


def offset_of_function(telemetries: list[Telemetry]) -> str:
    INVALID_ID: int = -1
    INVALID_TRAILER_INDEX: int = -2

    out: str = (
        f"constexpr const size_t INVALID_ID = {INVALID_ID};\n\n"
        f"constexpr const size_t INVALID_TRAILER_INDEX = {INVALID_TRAILER_INDEX};\n\n"
        f"constexpr const size_t offset_of({TELEMETRY_IDS_ENUM_NAME} id, int8_t trailer_index = -1) {{\n"
        "\treturn\n"
    )

    channels: list[Telemetry] = list(filter(lambda t: not t.is_event, telemetries))
    for i, telemetry in enumerate(channels):
        if telemetry.is_trailer_channel:
            out += f"\t\tid == {telemetry_id_by_enum(telemetry)} ? (\n"
            for i in range(SCS_TELEMETRY_trailers_count):
                out += f"\t\t\ttrailer_index == {i} ? {offsets_of(telemetries, telemetry, i)[0]} :"
                out += "\n"
                if i == SCS_TELEMETRY_trailers_count - 1:
                    out += "\t\t\tstatic_cast<size_t>(INVALID_TRAILER_INDEX)\n\t\t) :"
        else:
            out += (
                f"\t\tid == {telemetry_id_by_enum(telemetry)} ? {offsets_of(telemetries, telemetry)[0]} :"
            )
        if i == len(channels) - 1:
            out += " static_cast<size_t>(INVALID_ID);"

        out += "\n"

    out += "}\n"
    return out


def telemetry_id_enum(telemetries: list[Telemetry]) -> str:
    out: str = f"enum class {TELEMETRY_IDS_ENUM_NAME} {{\n"

    for i, telemetry in enumerate(telemetries):
        out += f"\t{telemetry.simple_name}"
        if i != len(telemetries) - 1:
            out += ","
        out += "\n"

    out += "};\n"
    return out


def sizeof_scs_type() -> str:
    out: str = (
        "constexpr const size_t sizeof_scs_type(scs_value_type_t type) {\n\treturn\n"
    )

    for i, size in enumerate(TYPE_SIZE_BY_ID):
        out += f"\t\ttype == {i} ? {size} :"
        if i == len(TYPE_SIZE_BY_ID) - 1:
            out += " static_cast<size_t>(-1);"
        out += "\n"

    out += "}\n"
    return out


def sizes_test(telemetries: list[Telemetry]) -> str:
    out: str = "void sizes_test() {\n"

    tested: set[tuple[int, int]] = set()
    for telemetry in telemetries:
        if telemetry.is_event:
            continue
        test: tuple[int, int] = (telemetry.scs_type_id, telemetry.max_count)
        if test in tested:
            continue
        tested.add(test)
        if telemetry.indexed:
            out += f'\tstatic_assert(sizeof(value_array_storage<{telemetry.scs_type}, {telemetry.max_count}>) == {value_array_storage_size(TYPE_SIZE_BY_ID[telemetry.scs_type_id], telemetry.max_count)}, "size of {telemetry.scs_type}[{telemetry.max_count}] failure");\n'
        else:
            out += f'\tstatic_assert(sizeof(value_storage<{telemetry.scs_type}>) == {value_storage_size(TYPE_SIZE_BY_ID[telemetry.scs_type_id])}, "size of {telemetry.scs_type} failure");\n'

    out += "\n"
    out += f'\tstatic_assert(sizeof({TRAILER_DATA_STRUCT_NAME}) == {trailer_data_size(telemetries)}, "sizeof {TRAILER_DATA_STRUCT_NAME} failure");\n'
    out += f'\tstatic_assert(sizeof({STORE_STRUCT_NAME}) == {store_size(telemetries)}, "size of {STORE_STRUCT_NAME} failure");\n'

    out += "}\n"
    return out


def offset_test_function(telemetries: list[Telemetry]) -> str:
    out: str = "void offset_test() {\n"
    out += "\t#define __STD_ARRAY_ELEMS__ _Elems\n"
    for telemetry in telemetries:
        if telemetry.is_event:
            continue
        if telemetry.is_trailer_channel:
            for i in range(SCS_TELEMETRY_trailers_count):
                offset, initialized_offset, size_offset = offsets_of(
                    telemetries, telemetry, i
                )
                storage_member: str = (
                    f"trailers.__STD_ARRAY_ELEMS__[{i}].{telemetry.simple_name}"
                )
                if telemetry.indexed:
                    out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}) == {offset}, "{telemetry.simple_name} offset failure");\n'
                    out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}.initialized) == {initialized_offset}, "{telemetry.simple_name}.initialized offset failure");\n'
                    out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}.size) == {size_offset}, "{telemetry.simple_name}.size offset failure");\n'
                else:
                    out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}) == {offset}, "{telemetry.simple_name} offset failure");\n'
                    out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}.initialized) == {initialized_offset}, "{telemetry.simple_name}.initialized offset failure");\n'
            continue
        else:
            offset, initialized_offset, size_offset = offsets_of(
                telemetries, telemetry, -1
            )
            storage_member: str = telemetry.simple_name
        if telemetry.indexed:
            out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}) == {offset}, "{telemetry.simple_name} offset failure");\n'
            out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}.initialized) == {initialized_offset}, "{telemetry.simple_name}.initialized offset failure");\n'
            out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}.size) == {size_offset}, "{telemetry.simple_name}.size offset failure");\n'
        else:
            out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}) == {offset}, "{telemetry.simple_name} offset failure");\n'
            out += f'\tstatic_assert(offsetof({STORE_STRUCT_NAME}, {storage_member}.initialized) == {initialized_offset}, "{telemetry.simple_name}.initialized offset failure");\n'
    out += "}\n"
    return out


def telemtry_info_types(telemetries: list[Telemetry], tabs: int = 1) -> str:
    out: str = ""
    tabstr: str = "\t" * tabs

    out += f"{tabstr}struct {CPP_INVALID_TYPE};\n\n"
    for telemetry in telemetries:
        out += (
            f"{tabstr}struct {telemetry.simple_name} {{\n"
            f"{tabstr}\tstatic constexpr const {TELEMETRY_IDS_ENUM_NAME} id = {TELEMETRY_IDS_ENUM_NAME}::{telemetry.simple_name};\n"
            f'{tabstr}\tstatic constexpr const char* const macro = "{telemetry.expansion}";\n'
            f"{tabstr}\tusing type = {TYPES_BY_ID[telemetry.scs_type_id]};\n"
            f"{tabstr}\tusing storage_type = {f'value_array_storage<{TYPES_BY_ID[telemetry.scs_type_id]}, {telemetry.max_count}>' if telemetry.indexed else f'value_storage<{TYPES_BY_ID[telemetry.scs_type_id]}>'};\n"
            f"{tabstr}\tstatic constexpr const scs_value_type_t value_type_id = {telemetry.scs_type_id};\n"
            f"{tabstr}\tstatic constexpr const bool is_event = {'true' if telemetry.is_event else 'false'};\n"
            f"{tabstr}\tstatic constexpr const bool indexed = {'true' if telemetry.indexed else 'false'};\n"
            f"{tabstr}\tstatic constexpr const bool is_trailer_channel = {'true' if telemetry.is_trailer_channel else 'false'};\n"
            f"{tabstr}\tstatic constexpr const size_t max_count = {telemetry.max_count};\n"
            f"{tabstr}}};\n\n"
        )

    return out


def register_all_function(telemetries: list[Telemetry]) -> str:
    out: str = (
        f"std::vector<{CONTEXT_STORE_NAME}> {CONTEXTS_VECTOR_NAME};\n"
        "\n"
        "//TODO: Store Functions\n"
        "\n"
        "void register_all(scs_telemetry_register_for_channel_t register_for_channel) {\n"
    )
    for registration in registrations_for(telemetries):
        out += f"{registration}\n"
    out += "}\n"
    return out


def event_info_simple_name(configuration: Configuration) -> str:
    return configuration.macro.replace("SCS_TELEMETRY_CONFIG_", "")


def attribute_simple_name(attribute: TelemetryEventAttribute) -> str:
    return attribute.macro.replace("SCS_TELEMETRY_CONFIG_ATTRIBUTE_", "")


def event_info_to_bytes_function(configuration: Configuration) -> str:
    out: str = f"void to_bytes(const {event_info_simple_name(configuration)}& info, std::vector<uint8_t>& out) {{\n"


    out += "\tout.resize(1);\n"
    out += "\t*out.data() = info.information;\n"
    out += "\tsize_t offset = 1;\n\n"

    for i, attribute in enumerate(configuration.attributes):
        type_name: str = SHORT_TYPENAME_TO_TYPE[attribute.type]
        identifier: str = attribute_simple_name(attribute)
        if attribute.type == "string":
            if attribute.indexed:
                out += (
                    f"\tout.resize(offset + 1);\n"
                    f"\tout[offset] = static_cast<uint8_t>(info.{identifier}.size());\n"
                    "\toffset += 1;\n"
                    f"\tfor (size_t i = 0; i < info.{identifier}.size(); i++) {{\n"
                    f"\t\tout.resize(offset + info.{identifier}[i].size() + 1);\n"
                    f"\t\tstd::copy(info.{identifier}[i].begin(), info.{identifier}[i].end(), out.begin() + offset);\n"
                    f"\t\tout[offset + info.{identifier}[i].size()] = 0;\n"
                    f"\t\toffset += info.{identifier}[i].size() + 1;\n"
                    "\t}\n"
                )
            else:
                out += (
                    "\toffset = out.size();\n"
                    f"\tout.resize(offset + info.{identifier}.size() + 1);\n"
                    f"\tstd::copy(info.{identifier}.begin(), info.{identifier}.end(), out.begin() + offset);\n"
                    f"\tout[offset + info.{identifier}.size()] = 0;\n"
                )
        elif attribute.indexed:
            out += (
                f"\tout.resize(offset + 1 + sizeof({type_name}) * info.{identifier}.size());\n"
                f"\tout[offset] = static_cast<uint8_t>(info.{identifier}.size());\n"
                f"\tmemcpy(out.data() + offset + 1, info.{identifier}.data(), sizeof({type_name}) * info.{identifier}.size());\n"
                f"\toffset += 1 + sizeof({type_name}) * info.{identifier}.size();\n"
            )
        else:
            out += (
                f"\tout.resize(offset + sizeof({type_name}));\n"
                f"\t*reinterpret_cast<{type_name}*>(out.data() + offset) = info.{identifier};\n"
                f"\toffset += sizeof({type_name});\n"
            )
        if i != len(configuration.attributes) - 1:
            out += "\n"

    out += "}\n"
    return out


def event_info_from_bytes_function(configuration: Configuration) -> str:
    out: str = f"void from_bytes(const std::vector<uint8_t>& bytes, {event_info_simple_name(configuration)}& out) {{\n"

    out += "\tout.information = bytes[0];\n"
    out += "\tsize_t offset = 1;\n\n"
    size_initialized: bool = False

    for i, attribute in enumerate(configuration.attributes):
        type_name: str = SHORT_TYPENAME_TO_TYPE[attribute.type]
        identifier: str = attribute_simple_name(attribute)
        if attribute.type == "string":
            if attribute.indexed:
                out += (
                    f"\t{'' if size_initialized else 'uint8_t '}size = bytes[offset];\n"
                    "\toffset++;\n"
                    f"\tout.{identifier}.clear();\n"
                    "\tfor (int i = 0; i < size; i++) {\n"
                    f"\t\tout.{identifier}.push_back(std::string(reinterpret_cast<const char*>(bytes.data() + offset)));\n"
                    f"\t\toffset += out.{identifier}.back().size() + 1;\n"
                    "\t}\n"
                )
                size_initialized = True
            else:
                out += (
                    f"\tout.{identifier}.clear();\n"
                    "\tfor (; bytes[offset] != 0; offset++) {\n"
                    f"\t\tout.{identifier} += static_cast<char>(bytes[offset]);\n"
                    "\t}\n"
                )
        elif attribute.indexed:
            out += (
                f"\t{'' if size_initialized else 'uint8_t '}size = bytes[offset];\n"
                "\toffset++;\n"
                f"\tout.{identifier}.clear();\n"
                "\tfor (int i = 0; i < size; i++) {\n"
                f"\t\tout.{identifier}.push_back(*reinterpret_cast<const {type_name}*>(bytes.data() + offset));\n"
                f"\t\toffset += sizeof({type_name});\n"
                "\t}\n"
            )
            size_initialized = True
        else:
            out += (
                f"\tout.{identifier} = *reinterpret_cast<const {type_name}*>(bytes.data() + offset);\n"
                f"\toffset += sizeof({type_name});\n"
            )
        if i != len(configuration.attributes) - 1:
            out += "\n"

    out += "}\n"
    return out


def configuration_structs(configurations: list[Configuration]) -> str:
    out: str = ""
    for configuration in configurations:
        if not configuration.attributes:
            continue

        out += f"struct {event_info_simple_name(configuration)} {{\n"
        out += "\tuint8_t information = 0;\n"
        for attribute in configuration.attributes:
            type_name: str = "std::string" if attribute.type == "string" else SHORT_TYPENAME_TO_TYPE[attribute.type]
            if attribute.indexed:
                out += f"\tstd::vector<{type_name}> {attribute_simple_name(attribute)} = {{}};\n"
            else:
                out += f"\t{type_name} {attribute_simple_name(attribute)} = {{}};\n"
        out += "};\n\n"

    return out


def to_bytes_functions(configurations: list[Configuration]) -> str:
    out: str = ""
    for configuration in configurations:
        if not configuration.attributes:
            continue
        out += f"{event_info_to_bytes_function(configuration)}\n"
    return out


def from_bytes_functions(configurations: list[Configuration]) -> str:
    out: str = ""
    for configuration in configurations:
        if not configuration.attributes:
            continue
        out += f"{event_info_from_bytes_function(configuration)}\n"
    return out


def event_info_struct_offsets_expr(configuration: Configuration) -> str:
    out: str = "{\n"

    for i, attribute in enumerate(configuration.attributes):
        out += f"\t{{ \"{attribute.expansion}\", offsetof({event_info_simple_name(configuration)}, {attribute_simple_name(attribute)}) }}"
        if i != len(configuration.attributes) - 1:
            out += ","
        out += "\n"

    out += "}"
    return out


def event_infos_struct_offsets(configurations: list[Configuration]) -> str:
    out: str = ""
    for configuration in configurations:
        if not configuration.attributes:
            continue
        out += f"const std::unordered_map<std::string, size_t> {event_info_simple_name(configuration)}_offsets ={event_info_struct_offsets_expr(configuration)};\n\n"
    return out


def configuraion_indexed_attributes(configuration: Configuration) -> str:
    out: str = f"const std::set<std::string> {event_info_simple_name(configuration)}_indexed ={{\n"
    indexed: list[TelemetryEventAttribute] = list(filter(lambda a: a.indexed, configuration.attributes))
    for i, attribute in enumerate(indexed):
        out += f"\t\"{attribute.expansion}\""
        if i != len(indexed) - 1:
            out += ","
        out += "\n"
    out += "};\n"
    return out


def configurations_indexed_attributes(configurations: list[Configuration]) -> str:
    out: str = ""
    for configuration in configurations:
        if not configuration.attributes:
            continue
        out += f"{configuraion_indexed_attributes(configuration)}\n"
    return out


def generate_cpp(telemetries: list[Telemetry], configurations: list[Configuration], output_folder: str = '.') -> None:
    with open(join(output_folder, "sizes.test.gitignore.cpp"), "w", encoding="utf-8") as f:
        f.write(sizes_test(telemetries))
    with open(join(output_folder, "offset.test.gitignore.cpp"), "w", encoding="utf-8") as f:
        f.write(offset_test_function(telemetries))
    with open(join(output_folder, "metadata.gitignore.h"), "w", encoding="utf-8") as f:
        f.write(f"{sizeof_scs_type()}\n")
        f.write(f"{telemetry_id_enum(telemetries)}\n")
        f.write(f"{type_id_of_function(telemetries)}\n")
        f.write(f"{is_trailer_channel_function(telemetries)}\n")
        f.write(f"{max_count_function(telemetries)}\n")
        f.write(f"{is_event_function(telemetries)}\n")
        f.write(f"{offset_of_function(telemetries)}\n")
    with open(join(output_folder, "offset_test.gitignore.cpp"), "w", encoding="utf-8") as f:
        f.write(offset_test_function(telemetries))
    with open(join(output_folder, "registrations.gitignore.cpp"), "w", encoding="utf-8") as f:
        f.write(f"{context_store()}\n")
        f.write(f"{context_store_definition()}\n")
        f.write(f"{register_all_function(telemetries)}\n")
    with open(join(output_folder, "store.gitignore.cpp"), "w", encoding="utf-8") as f:
        f.write(f"{cpp_containers()}\n")
        f.write(f"{cpp_store_struct(telemetries)}\n")
    with open(join(output_folder, "telemetry_info_types.gitignore.h"), "w", encoding="utf-8") as f:
        f.write(telemtry_info_types(telemetries, 2))
    with open(join(output_folder, "configurations.gitignore.h"), "w", encoding="utf-8") as f:
        f.write(configuration_structs(configurations))
        f.write("\n")
        f.write(configurations_indexed_attributes(configurations))
        f.write("\n")
        f.write(event_infos_struct_offsets(configurations))
        f.write("\n")
        f.write(to_bytes_functions(configurations))
        f.write("\n")
        f.write(from_bytes_functions(configurations))


def main() -> None:
    telemetries, attributes, configurations, gameplay_events = load()

    if configurations[5].attributes[3].expansion == "id":
        print("Applying temporary fix")
        configurations[5].attributes.pop(3)

    print(
        f"Loaded {len(telemetries)} telemetries, {len(attributes)} attributes, {len(configurations)} configurations and {len(gameplay_events)} gameplay events."
    )
    generate_cpp(telemetries, configurations)


if __name__ == "__main__":
    main()
