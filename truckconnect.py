from __future__ import annotations
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from scssdk_dataclasses import (
    Channel,
    Event,
    EventInfo,
    EventAttribute,
    load,
    TYPE_SIZE_BY_ID,
    TYPE_MACROS_BY_ID,
    SCS_TELEMETRY_trailers_count,
)

OUTPUT_FOLDER: Path = Path("generated.gitignore/")
TAB_CHARS: str = "\t"

TELEMETRY_EVENTS: str = [
    "SCS_TELEMETRY_EVENT_configuration",
    "SCS_TELEMETRY_EVENT_gameplay",
]
EXCLUDE_CHANNELS: dict[str, str] = {  # macro and reason
    "SCS_TELEMETRY_TRUCK_CHANNEL_adblue_average_consumption": "prism::sdk does not find this channel."
}
INVALID_TELEMETRY_ID: int = -1

VALUE_STORAGE_TYPE_NAME: str = "value_storage"
VALUE_STORAGE_EXTRA_SIZE: int = 1
VALUE_ARRAY_STORAGE_TYPE_NAME: str = "value_array_storage"
VALUE_ARRAY_STORAGE_EXTRA_SIZE: int = 1 + 4
VALUE_VECTOR_STORAGE_TYPE_NAME: str = "value_vector_storage"
TELEMETRY_ID_ENUM_TYPE_NAME: str = "telemetry_id"
TELEMETRY_ID_ENUM_BASE_TYPE: str = "uint8_t"
STD_ARRAYS_ELEMS: str = "_Elems"


def is_attribute(telemetry_or_attr: Telemetry | EventAttribute) -> bool:
    return isinstance(telemetry_or_attr, EventAttribute)


def use_std_string(cpp_type: str) -> str:
    if cpp_type == "scs_value_string_t":
        return "std::string"
    return cpp_type


def scs_type_id_storage_size(scs_type_id: int) -> int:
    return TYPE_SIZE_BY_ID[scs_type_id] + VALUE_STORAGE_EXTRA_SIZE


def channel_storage(channel: Channel) -> tuple[str, int]:
    cpp_type: str
    template_args: str
    if channel.indexed:
        cpp_type = VALUE_ARRAY_STORAGE_TYPE_NAME
        template_args = f"{use_std_string(channel.primitive_type)}, {channel.max_count}"
    else:
        cpp_type = VALUE_STORAGE_TYPE_NAME
        template_args = use_std_string(channel.primitive_type)

    return f"{cpp_type}<{template_args}>", scs_type_id_storage_size(
        channel.scs_type_id
    ) * channel.max_count


def attribute_storage(attribute: EventAttribute) -> str:
    return f"{VALUE_VECTOR_STORAGE_TYPE_NAME if attribute.indexed else VALUE_STORAGE_TYPE_NAME}<{attribute.primitive_type}>"


def storage(telemetry_or_attr: Telemetry | EventAttribute) -> tuple[str, int]:
    if is_attribute(telemetry_or_attr):
        return attribute_storage(telemetry_or_attr), None
    elif telemetry_or_attr.is_channel:
        return channel_storage(telemetry_or_attr.as_channel)

    assert False, "Can only get storage of a channel or event attribute"


def as_custom_channel(channel: Channel) -> Channel:
    channel._is_custom = None
    return channel


def is_custom_channel(channel: Channel) -> bool:
    return hasattr(channel, "_is_custom")


def type_name(telemetry_or_attr: Telemetry | EventAttribute) -> str:
    if is_attribute(telemetry_or_attr):
        return attribute_storage(telemetry_or_attr)
    if telemetry_or_attr.is_structure:
        return telemetry_or_attr.as_structure.type_name
    if telemetry_or_attr.is_event_info:
        return f"{name(telemetry_or_attr.parent_structure)}_{telemetry_or_attr.as_event_info.simple_name}_storage"
    if telemetry_or_attr.is_channel:
        return channel_storage(telemetry_or_attr.as_channel)[0]


def name(telemetry_or_attr_str: Telemetry | EventAttribute | str) -> str:
    if is_attribute(telemetry_or_attr_str):
        return telemetry_or_attr_str.simple_name
    if isinstance(telemetry_or_attr_str, str):
        return telemetry_or_attr_str
    return telemetry_or_attr_str.name


def qualify_name(*args: tuple[Telemetry]) -> str:
    qualified: str = ""
    for i, node in enumerate(args):
        qualified += name(node)
        if i != len(args) - 1:
            qualified += "::"
    return qualified


def qualify_type_name(telemetry: Telemetry) -> str:
    return qualify_name(
        *tuple(
            name(node) if node.is_channel else type_name(node)
            for node in telemetry.parents[::-1] + [telemetry]
        )
    )


def cpp_bool(boolean: bool) -> str:
    return "true" if boolean else "false"


def offsetof(type_name: str, member: str) -> str:
    return f"offsetof({type_name}, {member})"


class ChannelCategory(Enum):
    General = 0
    Truck = 1
    Trailer = 2

    @staticmethod
    def of(channel: Channel) -> ChannelCategory:
        if channel.macro.startswith("SCS_TELEMETRY_TRUCK_CHANNEL"):
            return ChannelCategory.Truck
        if channel.macro.startswith("SCS_TELEMETRY_TRAILER_CHANNEL"):
            return ChannelCategory.Trailer
        elif (
            channel.macro.startswith("SCS_TELEMETRY_CHANNEL")
            or channel.macro.startswith("SCS_TELEMETRY_JOB_CHANNEL")
            or is_custom_channel(channel)
        ):
            return ChannelCategory.General
        assert False, "A channel was not supplied"


class TelemetryType(Enum):
    Structure = "structure"
    EventInfo = "event_info"
    Channel = "channel"
    Invalid = "invalid = static_cast<telemetry_type>(-1)"

    def cpp_value(self) -> str:
        match self:
            case TelemetryType.Structure:
                return "telemetry_type::structure"
            case TelemetryType.EventInfo:
                return "telemetry_type::event_info"
            case TelemetryType.Channel:
                return "telemetry_type::channel"

    @staticmethod
    def cpp(tabcount: int = 0) -> str:
        tabstr: str = TAB_CHARS * tabcount
        out: str = f"{tabstr}enum class telemetry_type : uint8_t {{\n"
        for i, enum in enumerate(TelemetryType):
            out += f"{tabstr}{TAB_CHARS}{enum.value}"
            if i != len(TelemetryType):
                out += ","
            out += "\n"
        out += f"{tabstr}}};\n"
        return out


@dataclass
class Structure:
    data: Event | str
    children: list[Telemetry]

    @property
    def is_event(self) -> bool:
        return isinstance(self.data, Event)

    @property
    def is_str(self) -> bool:
        return isinstance(self.data, str)

    @property
    def name(self) -> str:
        if self.is_event:
            return self.data.simple_name
        return self.data

    @property
    def type_name(self) -> str:
        return f"{self.name}_storage"


@dataclass
class Telemetry:
    telemetry: Channel | EventInfo | Structure
    id: int = field(default=INVALID_TELEMETRY_ID)

    def __post_init__(self) -> None:
        self._parent_structure: Telemetry | None = None
        assert self.is_structure or self.is_event_info or self.is_channel, (
            "telemetry must be either structure, event info or channel"
        )

    def apply_parent_structure(self, parent: Telemetry) -> None:
        assert parent.is_structure, "Parent structure must be set."
        self._parent_structure = parent

    @property
    def parent_structure(self) -> Telemetry:
        assert self.name != "master", "Master has no parent"
        assert self._parent_structure is not None, "Parent structure must be set."
        return self._parent_structure

    @property
    def parents(self) -> list[Telemetry]:
        parents: list[Telemetry] = []
        current: Telemetry = self
        while current._parent_structure:
            parents.append(current._parent_structure)
            current = current._parent_structure
        return parents

    @property
    def is_channel(self) -> bool:
        return isinstance(self.telemetry, Channel)

    @property
    def as_channel(self) -> Channel:
        assert self.is_channel, "Requested Channel, but telemetry was not"
        return self.telemetry

    @property
    def is_event_info(self) -> bool:
        return isinstance(self.telemetry, EventInfo)

    @property
    def as_event_info(self) -> EventInfo:
        assert self.is_event_info, "Requested EventInfo, but telemetry was not"
        return self.telemetry

    @property
    def is_structure(self) -> bool:
        return isinstance(self.telemetry, Structure)

    @property
    def as_structure(self) -> Structure:
        assert self.is_structure, "Requested Structure, but telemetry was not"
        return self.telemetry

    @property
    def rank(self) -> int:
        if self.is_structure:
            return 0
        elif self.is_event_info:
            return 1
        elif self.is_channel:
            return 2

    @property
    def name(self) -> str:
        if self.is_structure:
            return self.as_structure.name
        elif self.is_event_info:
            return f"{self.as_event_info.event.simple_name}_{self.as_event_info.simple_name}_info"
        elif self.is_channel:
            return self.as_channel.simple_name

    @property
    def qualified_id(self) -> str:
        return qualify_name(TELEMETRY_ID_ENUM_TYPE_NAME, self.name)

    @property
    def telemetry_type(self) -> TelemetryType:
        if self.is_structure:
            return TelemetryType.Structure
        elif self.is_event_info:
            return TelemetryType.EventInfo
        elif self.is_channel:
            return TelemetryType.Channel

    @staticmethod
    def build(channels: list[Channel], events: list[Event]) -> list[Telemetry]:
        telemetries: list[Telemetry] = Telemetry._load_event_telemetries(events)
        general_structure: Telemetry = Telemetry(Structure("general", []))
        truck_structure: Telemetry = Telemetry(Structure("truck", []))
        trailer_structure: Telemetry = Telemetry(Structure("trailer", []))

        for channel_telemetry in Telemetry._load_channel_telemetries(channels):
            match ChannelCategory.of(channel_telemetry.telemetry):
                case ChannelCategory.General:
                    general_structure.telemetry.children.append(channel_telemetry)
                    channel_telemetry.apply_parent_structure(general_structure)
                case ChannelCategory.Truck:
                    truck_structure.telemetry.children.append(channel_telemetry)
                    channel_telemetry.apply_parent_structure(truck_structure)
                case ChannelCategory.Trailer:
                    trailer_structure.telemetry.children.append(channel_telemetry)
                    channel_telemetry.apply_parent_structure(trailer_structure)
                case _:
                    assert False, "'of' must always return a ChannelCategory"
            telemetries.append(channel_telemetry)

        telemetries.extend(
            (
                Telemetry(
                    Structure(
                        "channels",
                        [general_structure, truck_structure, trailer_structure],
                    )
                ),
                general_structure,
                truck_structure,
                trailer_structure,
            )
        )

        telemetries.sort(key=lambda t: t.rank)
        master: Telemetry = Telemetry(Structure("master", []))

        for telemetry in telemetries:
            if not telemetry.is_structure or telemetry._parent_structure:
                continue
            master.as_structure.children.append(telemetry)
            telemetry.apply_parent_structure(master)
        telemetries.insert(0, master)

        for i, telemetry in enumerate(telemetries):
            telemetry.id = i

        return telemetries

    @staticmethod
    def _load_event_telemetries(events: list[Event]) -> list[Telemetry]:
        event_telemetries: list[Telemetry] = []
        for event in events:
            if event.macro not in TELEMETRY_EVENTS:
                continue
            event_telemetry: Telemetry = Telemetry(Structure(event, []))
            for event_info in event.event_infos:
                event_info.attributes.insert(
                    0, EventAttribute("", "latest", "latest", "u32", False)
                )
                event_telemetry.as_structure.children.append(Telemetry(event_info))
                event_telemetry.as_structure.children[-1].apply_parent_structure(
                    event_telemetry
                )
            event_telemetries.append(event_telemetry)
            event_telemetries.extend(event_telemetry.as_structure.children)
        return event_telemetries

    @staticmethod
    def _load_channel_telemetries(channels: list[Channel]) -> list[Telemetry]:
        channel_telemetries: list[Telemetry] = []
        for channel in channels:
            if channel.macro in EXCLUDE_CHANNELS:
                print(
                    f"Excluding {channel.macro}. Reason: {EXCLUDE_CHANNELS[channel.macro]}"
                )
                continue
            channel_telemetries.append(Telemetry(channel))
        return channel_telemetries


__master_telemetry__: Telemetry | None = None
__trailer_structure_telemetry__: Telemetry | None = None
__configuration_trailer_structure_telemetry__: Telemetry | None = None


def cache_telemetries(telemetries: list[Telemetry]) -> list[Telemetry]:
    global __master_telemetry__
    global __trailer_structure_telemetry__
    global __configuration_trailer_structure_telemetry__
    __master_telemetry__ = telemetries[0]
    __trailer_structure_telemetry__ = next(
        filter(lambda t: name(t) == "trailer", telemetries)
    )
    __configuration_trailer_structure_telemetry__ = next(
        filter(lambda t: name(t) == "configuration_trailer_info", telemetries)
    )
    return telemetries


def master_telemetry() -> Telemetry:
    assert __master_telemetry__, "telemetries not cached"
    return __master_telemetry__


def trailer_structure_telemetry() -> Telemetry:
    assert __trailer_structure_telemetry__, "telemetries not cached"
    return __trailer_structure_telemetry__


def configuration_trailer_structure_telemetry() -> Telemetry:
    assert __configuration_trailer_structure_telemetry__, "telemetries not cached"
    return __configuration_trailer_structure_telemetry__


def master_structure(master: Telemetry, tabcount: int = 0) -> str:
    def recurse(tabcount: str, telemetry: Telemetry | EventAttribute):
        tabstr: str = TAB_CHARS * tabcount
        if isinstance(telemetry, EventAttribute):
            out = f"{tabstr}{storage(telemetry)[0]} {name(telemetry)} {{}};\n"
        elif telemetry.is_structure:
            out = f"{tabstr}struct {type_name(telemetry)} {{"
            if telemetry.as_structure.children:
                out += "\n"

            for child in telemetry.as_structure.children:
                out += recurse(tabcount + 1, child)

            out += f"{tabstr}}}"
            if telemetry == trailer_structure_telemetry():
                out += f"; std::array<{type_name(telemetry)}, {SCS_TELEMETRY_trailers_count}> {name(telemetry)};\n"
            else:
                if telemetry != master_telemetry():
                    out += f" {name(telemetry)}"
                out += ";\n"
        elif telemetry.is_event_info:
            out = f"{tabstr}struct {type_name(telemetry)} {{"
            if telemetry.as_event_info.attributes:
                out += "\n"

            for child in telemetry.as_event_info.attributes:
                out += recurse(tabcount + 1, child)

            out += f"{tabstr}}}"
            if telemetry == configuration_trailer_structure_telemetry():
                out += f"; std::array<{type_name(telemetry)}, {SCS_TELEMETRY_trailers_count}> {name(telemetry)};\n"
            else:
                if telemetry != master_telemetry():
                    out += f" {name(telemetry)}"
                out += ";\n"
        else:
            out = f"{tabstr}{storage(telemetry)[0]} {name(telemetry)} {{}};\n"

        return out

    return recurse(tabcount, master)


def telemetries_ids_enum(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}namespace {TELEMETRY_ID_ENUM_TYPE_NAME}s {{\n"
        f"{tabstr}{TAB_CHARS}enum {TELEMETRY_ID_ENUM_TYPE_NAME} : {TELEMETRY_ID_ENUM_BASE_TYPE} {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f"{tabstr}{TAB_CHARS * 2}{telemetry.name} = {i},\n"

    out += f"{tabstr}{TAB_CHARS * 2}invalid = static_cast<{TELEMETRY_ID_ENUM_TYPE_NAME}>(-1)\n"

    out += f"{tabstr}{TAB_CHARS}}};\n{tabstr}}};\n"
    return out


def metadata_value_struct(namespace: str, tab_count: int) -> str:
    tabstr: str = TAB_CHARS * tab_count

    out: str = (
        f"{TelemetryType.cpp(tab_count)}\n"
        f"{tabstr}constexpr const size_t INVALID_OFFSET = static_cast<size_t>(-1);\n\n"
        f"{tabstr}constexpr const size_t INVALID_TRAILER_INDEX = static_cast<size_t>(-1);\n\n"
        f"{tabstr}constexpr const size_t INVALID_SIZE = 0;\n\n"
        f"{tabstr}constexpr const {TELEMETRY_ID_ENUM_TYPE_NAME} LIFETIME_INVALID_ID = {TELEMETRY_ID_ENUM_TYPE_NAME}::invalid;\n\n"
    )

    out += (
        f"{tabstr}struct metadata_value {{\n"
        f"{tabstr}{TAB_CHARS}telemetry_id id;\n"
        f"{tabstr}{TAB_CHARS}telemetry_type telemetry_type;\n"
        f"{tabstr}{TAB_CHARS}size_t master_offset;\n"
        f"{tabstr}{TAB_CHARS}size_t structure_offset;\n"
        f"{tabstr}{TAB_CHARS}size_t storage_size;\n"
        f"{tabstr}{TAB_CHARS}const char* macro_identifier;\n"
        f"{tabstr}{TAB_CHARS}const char* macro;\n"
        f"{tabstr}{TAB_CHARS}bool indexed;\n"
        f"{tabstr}{TAB_CHARS}size_t max_count;\n"
        f"{tabstr}{TAB_CHARS}bool trailer_channel;\n"
        f"{tabstr}{TAB_CHARS}scs_value_type_t scs_type_id;\n"
        f"{tabstr}{TAB_CHARS}bool custom_channel;\n\n"
        f"{tabstr}{TAB_CHARS}constexpr metadata_value(\n"
        f"{tabstr}{TAB_CHARS}telemetry_id id = telemetry_id::invalid,\n"
        f"{tabstr}{TAB_CHARS}{namespace}::telemetry_type telemetry_type = ::metadata::telemetry_type::invalid,\n"
        f"{tabstr}{TAB_CHARS}size_t master_offset = INVALID_OFFSET,\n"
        f"{tabstr}{TAB_CHARS}size_t structure_offset = INVALID_OFFSET,\n"
        f"{tabstr}{TAB_CHARS}size_t storage_size = INVALID_SIZE,\n"
        f"{tabstr}{TAB_CHARS}const char* macro_identifier = nullptr,\n"
        f"{tabstr}{TAB_CHARS}const char* macro = nullptr,\n"
        f"{tabstr}{TAB_CHARS}bool indexed = false,\n"
        f"{tabstr}{TAB_CHARS}size_t max_count = 1,\n"
        f"{tabstr}{TAB_CHARS}bool trailer_channel = false,\n"
        f"{tabstr}{TAB_CHARS}scs_value_type_t scs_type_id = SCS_VALUE_TYPE_INVALID,\n"
        f"{tabstr}{TAB_CHARS}bool custom_channel = SCS_VALUE_TYPE_INVALID\n"
        f"{tabstr}) :\n"
        f"{tabstr}{TAB_CHARS}id(id),\n"
        f"{tabstr}{TAB_CHARS}telemetry_type(telemetry_type),\n"
        f"{tabstr}{TAB_CHARS}master_offset(master_offset),\n"
        f"{tabstr}{TAB_CHARS}structure_offset(structure_offset),\n"
        f"{tabstr}{TAB_CHARS}storage_size(storage_size),\n"
        f"{tabstr}{TAB_CHARS}macro_identifier(macro_identifier),\n"
        f"{tabstr}{TAB_CHARS}macro(macro),\n"
        f"{tabstr}{TAB_CHARS}indexed(indexed),\n"
        f"{tabstr}{TAB_CHARS}max_count(max_count),\n"
        f"{tabstr}{TAB_CHARS}trailer_channel(trailer_channel),\n"
        f"{tabstr}{TAB_CHARS}scs_type_id(scs_type_id),\n"
        f"{tabstr}{TAB_CHARS}custom_channel(custom_channel) {{}}\n"
        f"{tabstr}}};\n\n"
        f"{tabstr}constexpr const metadata_value INVALID_METADATA = metadata_value();\n\n"
    )

    return out


def telemetry_metadata_structs(
    telemetries: list[Telemetry], namespace: str = "metadata", tabcount: int = 0
) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = f"{tabstr}namespace {namespace} {{\n"
    tabstr = TAB_CHARS * (tabcount + 1)

    out += f"{metadata_value_struct(namespace, tabcount + 1)}\n"

    for i, telemetry in enumerate(telemetries):
        out += (
            f"{tabstr}struct {telemetry.name} {{\n"
            f"{tabstr}{TAB_CHARS}static constexpr const {TELEMETRY_ID_ENUM_TYPE_NAME} id = {telemetry.qualified_id};\n"
            f"{tabstr}{TAB_CHARS}static constexpr const telemetry_type telemetry_type = {telemetry.telemetry_type.cpp_value()};\n"
        )

        if telemetry == master_telemetry():
            out += (
                f"{tabstr}{TAB_CHARS}static constexpr const size_t master_offset = 0;\n"
            )
            out += f"{tabstr}{TAB_CHARS}static constexpr const size_t structure_offset = 0;\n"
        else:
            parents: list[Telemetry | str] = telemetry.parents[:-1][::-1]
            dot_notation: str = ""
            if telemetry.is_channel and telemetry.as_channel.is_trailer_channel:
                parents.append(f"{STD_ARRAYS_ELEMS}[0]")

            for parent in parents:
                dot_notation += f"{name(parent)}."
            dot_notation += name(telemetry)

            out += f"{tabstr}{TAB_CHARS}static constexpr const size_t master_offset = {offsetof(type_name(master_telemetry()), dot_notation)};\n"

        if telemetry.is_structure:
            out += f"{tabstr}{TAB_CHARS}using storage_type = {qualify_type_name(telemetry)};\n"
            if telemetry != master_telemetry():
                out += (
                    f"{tabstr}{TAB_CHARS}static constexpr const size_t structure_offset = {offsetof(qualify_name(*[type_name(parent) for parent in telemetry.parents][::-1]), name(telemetry))};\n"
                    f"{tabstr}{TAB_CHARS}static constexpr const metadata_value metadata_value = metadata_value(id, telemetry_type, master_offset, structure_offset, sizeof(storage_type));\n"
                )
            else:
                out += f"{tabstr}{TAB_CHARS}static constexpr const metadata_value metadata_value = metadata_value(id, telemetry_type, master_offset, structure_offset, sizeof(storage_type));\n"
        elif telemetry.is_event_info:
            out += (
                f"{tabstr}{TAB_CHARS}using storage_type = {qualify_name(*[type_name(parent) for parent in ([] if telemetry == master_telemetry() else telemetry.parents[::-1])], type_name(telemetry))};\n"
                f'{tabstr}{TAB_CHARS}static constexpr const char* const macro_identifier = "{telemetry.as_event_info.macro}";\n'
                f'{tabstr}{TAB_CHARS}static constexpr const char* const macro = "{telemetry.as_event_info.expansion}";\n'
                f"{tabstr}{TAB_CHARS}static constexpr const size_t structure_offset = {offsetof(qualify_type_name(telemetry.parent_structure), name(telemetry))};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const metadata_value metadata_value = metadata_value(id, telemetry_type, master_offset, structure_offset, sizeof(storage_type), macro_identifier, macro);\n"
            )
        elif telemetry.is_channel:
            out += (
                f"{tabstr}{TAB_CHARS}using storage_type = {type_name(telemetry)};\n"
                f'{tabstr}{TAB_CHARS}static constexpr const char* const macro_identifier = "{telemetry.as_channel.macro}";\n'
                f'{tabstr}{TAB_CHARS}static constexpr const char* const macro = "{telemetry.as_channel.expansion}";\n'
                f"{tabstr}{TAB_CHARS}static constexpr const bool indexed = {cpp_bool(telemetry.as_channel.indexed)};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const size_t max_count = {telemetry.as_channel.max_count};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const bool trailer_channel = {cpp_bool(telemetry.as_channel.is_trailer_channel)};\n"
                f"{tabstr}{TAB_CHARS}using scs_type = {telemetry.as_channel.scs_type};\n"
                f"{tabstr}{TAB_CHARS}static constexpr scs_value_type_t scs_type_id = {TYPE_MACROS_BY_ID[telemetry.as_channel.scs_type_id]};\n"
                f"{tabstr}{TAB_CHARS}using primitive_type = {telemetry.as_channel.primitive_type};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const size_t structure_offset = {offsetof(qualify_type_name(telemetry.parent_structure), name(telemetry))};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const bool custom_channel = {cpp_bool(is_custom_channel(telemetry.as_channel))};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const metadata_value metadata_value = metadata_value(id, telemetry_type, master_offset, structure_offset, sizeof(storage_type), macro_identifier, macro, indexed, max_count, trailer_channel, scs_type_id, custom_channel);\n"
            )
        out += f"{tabstr}}};\n"
        if i != len(telemetries) - 1:
            out += "\n"

    tabstr = TAB_CHARS * tabcount
    out += f"{tabstr}}}"
    return out


def telemetry_type_of_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const telemetry_type& telemtry_type_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::telemetry_type;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return telemetry_type::invalid;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def master_offset_of_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const size_t master_offset_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const size_t& trailer_index = INVALID_TRAILER_INDEX) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        if (
            telemetry.is_channel and telemetry.as_channel.is_trailer_channel
        ) or telemetry == trailer_structure_telemetry():
            out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return 0 <= trailer_index && trailer_index <= SCS_TELEMETRY_trailers_count ? {name(telemetry)}::master_offset + sizeof({qualify_type_name(telemetry.parent_structure)}) * trailer_index : INVALID_OFFSET;\n"
        elif telemetry == configuration_trailer_structure_telemetry():
            out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return 0 <= trailer_index && trailer_index <= SCS_TELEMETRY_trailers_count ? {name(telemetry)}::master_offset + sizeof({qualify_type_name(telemetry.parent_structure)}) * trailer_index : INVALID_OFFSET;\n"
        else:
            out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::master_offset;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_OFFSET;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def structure_offset_of_function(
    telemetries: list[Telemetry], tabcount: int = 0
) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const size_t& structure_offset_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::structure_offset;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_OFFSET;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def indexed_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const bool& indexed(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_channel, telemetries)):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::indexed;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return false;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def max_count_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const size_t& max_count(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_channel, telemetries)):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::max_count;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return 1;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def is_trailer_channel_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const bool& is_trailer_channel(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_channel, telemetries)):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::trailer_channel;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return false;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def scs_type_id_of_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const scs_value_type_t& scs_type_id_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_channel, telemetries)):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::scs_type_id;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return SCS_VALUE_TYPE_INVALID;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def id_of_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr bool streq(char const* a, char const* b) {{\n"
        f"{tabstr}{TAB_CHARS}return *a == *b && (*a == '\\0' || streq(a + 1, b + 1));\n"
        f"{tabstr}}}\n\n"
        f"{tabstr}constexpr const telemetry_id& id_of(const char* const macro) {{\n"
        f"{tabstr}{TAB_CHARS}return\n"
    )

    for i, telemetry in enumerate(telemetries):
        if telemetry.is_channel and telemetry.as_channel.is_trailer_channel:
            cmp_expr: str = f'{TAB_CHARS}streq(macro, "{name(telemetry)}") ||\n'
            for j in range(SCS_TELEMETRY_trailers_count):
                cmp_expr += (
                    f'{tabstr}{TAB_CHARS * 3}streq(macro, "{name(telemetry)}.{j}")'
                )
                if j != SCS_TELEMETRY_trailers_count - 1:
                    cmp_expr += " ||\n"
        else:
            cmp_expr: str = f'streq(macro, "{name(telemetry)}")'
            if not telemetry.is_structure:
                cmp_expr += f" || streq(macro, {name(telemetry)}::macro)"
        out += f"{tabstr}{TAB_CHARS * 2}{cmp_expr} ? {name(telemetry)}::id :\n"

    out += f"{tabstr}{TAB_CHARS * 2}LIFETIME_INVALID_ID;\n{tabstr}}}\n"
    return out


def name_of_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const char* const name_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f'{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return "{name(telemetry)}";\n'

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return nullptr;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def size_of_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const size_t size_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return sizeof({name(telemetry)}::storage_type);\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_SIZE;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def offset_of_latest_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const size_t offset_of_latest(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_event_info, telemetries)):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return offsetof({name(telemetry)}::storage_type, latest);\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_OFFSET;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def event_info_member_offset_of_function(
    telemetries: list[Telemetry], tabcount: int = 0
) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const size_t event_info_member_offset_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const char* const member) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_event_info, telemetries)):
        out += (
            f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}:\n"
            f"{tabstr}{TAB_CHARS * 3}return\n"
        )
        for attribute in telemetry.as_event_info.attributes:
            out += f'{tabstr}{TAB_CHARS * 4}streq(member, "{attribute.simple_name}") ? offsetof({name(telemetry)}::storage_type, {attribute.simple_name}) :\n'
        out += f"{tabstr}{TAB_CHARS * 4}INVALID_OFFSET;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_OFFSET;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def event_info_member_scs_type_id_function(
    telemetries: list[Telemetry], tabcount: int = 0
) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const scs_value_type_t event_info_member_scs_type_id(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const char* const member) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_event_info, telemetries)):
        out += (
            f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}:\n"
            f"{tabstr}{TAB_CHARS * 3}return\n"
        )
        for attribute in telemetry.as_event_info.attributes:
            out += f'{tabstr}{TAB_CHARS * 4}streq(member, "{attribute.simple_name}") ? {TYPE_MACROS_BY_ID[attribute.scs_type_id]} :\n'
        out += f"{tabstr}{TAB_CHARS * 4}SCS_VALUE_TYPE_INVALID;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return SCS_VALUE_TYPE_INVALID;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def is_custom_channel_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const bool is_custom_channel(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_channel, telemetries)):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::custom_channel;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return false;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def metadata_value_of_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const metadata_value& metadata_value_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::metadata_value;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_METADATA;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


PAUSED_CUSTOM_CHANNEL: Channel = Channel(
    "channel_paused", "", "bool", False, "channel_paused", False, 1
)


def main() -> None:
    channels, events = load()
    channels.insert(0, as_custom_channel(PAUSED_CUSTOM_CHANNEL))

    telemetries: list[Telemetry] = cache_telemetries(Telemetry.build(channels, events))
    print(f"Loaded {len(telemetries)} telemetries.")

    if not OUTPUT_FOLDER.exists():
        OUTPUT_FOLDER.mkdir()
    with open(OUTPUT_FOLDER.joinpath("master_structure.h"), "w", encoding="utf-8") as f:
        f.write(master_structure(master_telemetry()))
    with open(
        OUTPUT_FOLDER.joinpath("telemetry_type_enum.h"), "w", encoding="utf-8"
    ) as f:
        f.write(TelemetryType.cpp())
    with open(
        OUTPUT_FOLDER.joinpath("telemetry_id_enum.h"), "w", encoding="utf-8"
    ) as f:
        f.write(telemetries_ids_enum(telemetries))
    with open(
        OUTPUT_FOLDER.joinpath("telemetry_metadata_structs.h"), "w", encoding="utf-8"
    ) as f:
        f.write(telemetry_metadata_structs(telemetries))
    with open(
        OUTPUT_FOLDER.joinpath("telemetry_metadata_functions.h"), "w", encoding="utf-8"
    ) as f:
        f.write(f"{telemetry_type_of_function(telemetries)}\n")
        f.write(f"{master_offset_of_function(telemetries)}\n")
        f.write(f"{structure_offset_of_function(telemetries)}\n")
        f.write(f"{indexed_function(telemetries)}\n")
        f.write(f"{max_count_function(telemetries)}\n")
        f.write(f"{is_trailer_channel_function(telemetries)}\n")
        f.write(f"{scs_type_id_of_function(telemetries)}\n")
        f.write(f"{id_of_function(telemetries)}\n")
        f.write(f"{name_of_function(telemetries)}\n")
        f.write(f"{size_of_function(telemetries)}\n")
        f.write(f"{offset_of_latest_function(telemetries)}\n")
        f.write(f"{event_info_member_offset_of_function(telemetries)}\n")
        f.write(f"{event_info_member_scs_type_id_function(telemetries)}\n")
        f.write(f"{is_custom_channel_function(telemetries)}\n")
        f.write(f"{metadata_value_of_function(telemetries)}\n")


if __name__ == "__main__":
    if retval := main():
        print(retval)
