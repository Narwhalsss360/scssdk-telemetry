from scssdk_dataclasses import Telemetry, TYPE_MACROS_BY_ID, SCS_TELEMETRY_trailers_count, load, TYPE_SIZE_BY_ID


VALUE_STORAGE_STRUCT_NAME: str = 'value_storage'
VALUE_ARRAY_STORAGE_STRUCT_NAME: str = 'value_array_storage'
TRAILER_DATA_STRUCT_NAME: str = 'trailer_data'
TRAILER_DATA_INSTANCE_NAME: str = 'trailers'
STORE_STRUCT_NAME: str = 'game_data_store'
STORE_INSTANCE_NAME: str = 'game_data'
STORE_FUNCTION_NAME: str = 'store'


def cpp_containers() -> str:
    return (
        'template <typename T>\n'
        f'struct {VALUE_STORAGE_STRUCT_NAME} {{\n'
        '\tT value;\n'
        '\tbool initialized = false;\n'
        '};\n'
        '\n'
        'template <typename T, size_t max_count>\n'
        f'struct {VALUE_ARRAY_STORAGE_STRUCT_NAME} {{\n'
        '\tstd::array<T, max_count> values;\n'
        '\tbool initialized = false;\n'
        '\tuint32_t size = 0;\n'
        '};\n'
        '\n'
    )


def cpp_store_struct(telemetries: list[Telemetry]) -> str:
    out: str = f'struct {TRAILER_DATA_STRUCT_NAME} {{\n'
    for trailer_telemetry in filter(lambda t: t.is_trailer_channel, telemetries):
        if trailer_telemetry.indexed:
            container_type: str = VALUE_ARRAY_STORAGE_STRUCT_NAME
            template_args: str = f'{trailer_telemetry.scs_type}, {trailer_telemetry.max_count}'
        else:
            container_type: str = VALUE_STORAGE_STRUCT_NAME
            template_args: str = trailer_telemetry.scs_type
        out += f'\t{container_type}<{template_args}> {trailer_telemetry.simple_name};\n'

    out += (
        '};\n'
        '\n'
        f'struct {STORE_STRUCT_NAME} {{\n'
    )

    for telemetry in filter(lambda t: not t.is_trailer_channel and not t.is_event, telemetries):
        if telemetry.indexed:
            container_type: str = VALUE_ARRAY_STORAGE_STRUCT_NAME
            template_args: str = f'{telemetry.scs_type}, {telemetry.max_count}'
        else:
            container_type: str = VALUE_STORAGE_STRUCT_NAME
            template_args: str = telemetry.scs_type
        out += f'\t{container_type}<{template_args}> {telemetry.simple_name};\n'
    out += f'\tstd::array<{TRAILER_DATA_STRUCT_NAME}, {SCS_TELEMETRY_trailers_count}> {TRAILER_DATA_INSTANCE_NAME};\n'
    out += '};\n\n'
    return out


def registrations_for(telemetries: list[Telemetry], trailer_count: int = SCS_TELEMETRY_trailers_count, tabs: int = 1) -> str:
    tab_str: str = '\t' * tabs
    out: str
    for telemetry in telemetries:
        if telemetry.is_event:
            continue
        function: str = 'register_for_channel'
        expansion: str = telemetry.expansion
        type_macro: str = TYPE_MACROS_BY_ID[telemetry.scs_type_id]
        callback: str = f'{STORE_FUNCTION_NAME}<{telemetry.scs_type}, {telemetry.max_count}>' if telemetry.indexed else f'store<{telemetry.scs_type}>'

        if telemetry.is_trailer_channel:
            if telemetry.indexed:
                out = (
                    f'{tab_str}char {telemetry.macro}_expansion[] = "{expansion.replace("trailer", "trailer.0")}";\n'
                    f'{tab_str}char& {telemetry.macro}_trailer_index_char = {telemetry.macro}_expansion[8];\n'
                    f"{tab_str}for (scs_u32_t t = 0; t < {trailer_count}; t++) {{\n"
                    f"{tab_str}\t{telemetry.macro}_trailer_index_char = '0' + t;\n"
                    f'{tab_str}\tfor(scs_u32_t i = 0; i < {telemetry.max_count}; i++) {{\n'
                    f'{tab_str}\t\t{function}({telemetry.macro}_expansion, i, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, &{STORE_INSTANCE_NAME}.{TRAILER_DATA_INSTANCE_NAME}[t].{telemetry.simple_name});\n'
                    f"{tab_str}\t}}\n"
                    f"{tab_str}}}\n"
                )
            else:
                out = (
                    f'{tab_str}char {telemetry.macro}_expansion[] = "{expansion.replace("trailer", "trailer.0")}";\n'
                    f'{tab_str}char& {telemetry.macro}_trailer_index_char = {telemetry.macro}_expansion[8];\n'
                    f"{tab_str}for (scs_u32_t t = 0; t < {trailer_count}; t++) {{\n"
                    f"{tab_str}\t{telemetry.macro}_trailer_index_char = '0' + t;\n"
                    f'{tab_str}\t{function}({telemetry.macro}_expansion, SCS_U32_NIL, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, &{STORE_INSTANCE_NAME}.{TRAILER_DATA_INSTANCE_NAME}[t].{telemetry.simple_name});\n'
                    f"{tab_str}}}\n"
                )
        else:
            if telemetry.indexed:
                out = (
                    f"{tab_str}for (scs_u32_t i = 0; i < {telemetry.max_count}; i++) {{\n"
                    f"{tab_str}\t{function}({telemetry.macro}, i, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, &{STORE_INSTANCE_NAME}.{telemetry.simple_name});\n"
                    f"{tab_str}}}\n"
                )
            else:
                out = f"{tab_str}{function}({telemetry.macro}, SCS_U32_NIL, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, &{STORE_INSTANCE_NAME}.{telemetry.simple_name});\n"

        yield out


def trailer_data_size(telemetries: list[Telemetry]) -> int:
    size: int = 0
    for telemetry in telemetries:
        if not telemetry.is_trailer_channel:
            continue
        count: int = telemetry.max_count if telemetry.indexed else 1 
        if count != 1:
            size += 4
        size += (count * TYPE_SIZE_BY_ID[telemetry.scs_type_id]) + 1

    return size


def trailer_data_offset(telemetries: list[Telemetry]) -> int:
    offset: int = 0
    for telemetry in telemetries:
        if telemetry.is_trailer_channel or telemetry.is_event:
            continue
        count: int = telemetry.max_count if telemetry.indexed else 1 
        if count != 1:
            offset += 4
        offset += (count * TYPE_SIZE_BY_ID[telemetry.scs_type_id]) + 1
    return offset


def trailer_data_offset_of(telemetries: list[Telemetry], telemetry: Telemetry) -> tuple[int, int, int]:
    if not telemetry.is_trailer_channel:
        raise ValueError('Telemetry is not a trailer channel')


    offset: int = 0
    for other in telemetries:
        if not other.is_trailer_channel or other.is_event:
            continue
        if other.id == telemetry.id:
            break
        count: int = other.max_count if other.indexed else 1 
        if count != 1:
            offset += 4
        offset += (count * TYPE_SIZE_BY_ID[other.scs_type_id]) + 1

    count: int = telemetry.max_count if telemetry.indexed else 1 
    initialized_offset: int = offset + (count * TYPE_SIZE_BY_ID[telemetry.scs_type_id])
    size_offset: int = initialized_offset + 1
    return offset, initialized_offset, size_offset


def offsets_of(telemetries: list[Telemetry], telemetry: Telemetry, trailer_index: int = -1) -> tuple[int, int, int]:
    offset: int = 0
    if telemetry.is_trailer_channel or trailer_index != -1:
        if not (0 <= trailer_index <= SCS_TELEMETRY_trailers_count):
            raise IndexError(f'trailer_index must be within [0, {SCS_TELEMETRY_trailers_count})')

        origin: int = trailer_data_size() * (trailer_index + 1)
        return tuple(origin + offset for offset in trailer_data_offset_of(telemetries, telemetry, trailer_index))

    for other in telemetries:
        if other.is_trailer_channel or other.is_event:
            continue
        if other.id == telemetry.id:
            break
        count: int = other.max_count if other.indexed else 1 
        if count != 1:
            offset += 4
        offset += (count * TYPE_SIZE_BY_ID[other.scs_type_id]) + 1

    count: int = telemetry.max_count if telemetry.indexed else 1 
    initialized_offset: int = offset + (count * TYPE_SIZE_BY_ID[telemetry.scs_type_id])
    size_offset: int = initialized_offset + 1
    return offset, initialized_offset, size_offset


def main() -> None:
    telemetries, attributes, configurations, gameplay_events = load()
    print(
        f"Loaded {len(telemetries)} telemetries, {len(attributes)} attributes, {len(configurations)} configurations and {len(gameplay_events)} gameplay events."
    )

    with open('registrations.gitignore.cpp', 'w', encoding='utf-8') as f:
        f.write('void register_all(scs_telemetry_register_for_channel_t register_for_channel) {\n')
        for registration in registrations_for(telemetries):
            f.write(registration)
        f.write('}\n')
    with open('store.gitignore.cpp', 'w', encoding='utf-8') as f:
        f.write(cpp_containers())
        f.write(cpp_store_struct(telemetries))


if __name__ == '__main__':
    main()
