from scssdk_dataclasses import Telemetry, TYPE_MACROS_BY_ID, SCS_TELEMETRY_trailers_count, load


STORE_FUNCTION_NAME: str = 'store'


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
        context: str = 'nullptr'

        if telemetry.is_trailer_channel:
            if telemetry.indexed:
                out = (
                    f'{tab_str}char {telemetry.macro}_expansion[] = "{expansion.replace("trailer", "trailer.0")}";\n'
                    f'{tab_str}char& {telemetry.macro}_trailer_index_char = {telemetry.macro}_expansion[8];\n'
                    f"{tab_str}for (scs_u32_t t = 0; t < {trailer_count}; t++) {{\n"
                    f"{tab_str}\t{telemetry.macro}_trailer_index_char = '0' + t;\n"
                    f'{tab_str}\tfor(scs_u32_t i = 0; i < {telemetry.max_count}; i++) {{\n'
                    f'{tab_str}\t\t{function}({telemetry.macro}_expansion, i, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, {context});\n'
                    f"{tab_str}\t}}\n"
                    f"{tab_str}}}\n"
                )
            else:
                out = (
                    f'{tab_str}char {telemetry.macro}_expansion[] = "{expansion.replace("trailer", "trailer.0")}";\n'
                    f'{tab_str}char& {telemetry.macro}_trailer_index_char = {telemetry.macro}_expansion[8];\n'
                    f"{tab_str}for (scs_u32_t t = 0; t < {trailer_count}; t++) {{\n"
                    f"{tab_str}\t{telemetry.macro}_trailer_index_char = '0' + t;\n"
                    f'{tab_str}\t{function}({telemetry.macro}_expansion, SCS_U32_NIL, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, {context});\n'
                    f"{tab_str}}}\n"
                )
        else:
            if telemetry.indexed:
                out = (
                    f"{tab_str}for (scs_u32_t i = 0; i < {telemetry.max_count}; i++) {{\n"
                    f"{tab_str}\t{function}({telemetry.macro}, i, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, {context});\n"
                    f"{tab_str}}}\n"
                )
            else:
                out = f"{tab_str}{function}({telemetry.macro}, SCS_U32_NIL, {type_macro}, SCS_TELEMETRY_CHANNEL_FLAG_none, {callback}, {context});\n"

        yield out


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



if __name__ == '__main__':
    main()
