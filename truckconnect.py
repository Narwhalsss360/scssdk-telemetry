from __future__ import annotations
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field, asdict, fields
from copy import deepcopy
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
import json

# region Constants
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
# endregion


# region Basic Utility
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
    return f"{VALUE_VECTOR_STORAGE_TYPE_NAME if attribute.indexed else VALUE_STORAGE_TYPE_NAME}<{use_std_string(attribute.primitive_type)}>"


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


# endregion


# region Types
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
    Invalid = "invalid = static_cast<uint8_t>(-1)"

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


INVALID_TELEMETRY_DATA: Channel = Structure(None, None)


@dataclass
class Telemetry:
    COMMON_FIELDS = (
        "id",
        "telemetry_type",
        "constant_size",
        "identifier"
    )
    id: int
    telemetry_type: TelemetryType
    constant_size: bool
    identifier: str
    event: Event | None = field(default=None)
    attributes: list[EventAttribute] | None = field(default=None)
    children: list[Telemetry] | None = field(default=None)
    macro: str | None = field(default=None)
    expansion: str | None = field(default=None)
    type: str | None = field(default=None)
    indexed: bool | None = field(default=None)
    simple_name: str | None = field(default=None)
    is_trailer_channel: bool | None = field(default=None)
    max_count: int | None = field(default=None)
    custom_channel: bool | None = field(default=None)

    def __post_init__(self) -> None:
        self._telemetry: Channel | EventInfo | Structure | None = INVALID_TELEMETRY_DATA
        self._parent_structure: Telemetry | None = None
        assert self.is_structure or self.is_event_info or self.is_channel, (
            "telemetry must be either structure, event info or channel"
        )
        if self.telemetry_type is None:
            if self.is_structure:
                self.telemetry_type = TelemetryType.Structure
            elif self.is_event_info:
                self.telemetry_type = TelemetryType.EventInfo
            else:
                self.telemetry_type = TelemetryType.Channel

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
        return isinstance(self._telemetry, Channel)

    @property
    def as_channel(self) -> Channel:
        assert self.is_channel, "Requested Channel, but telemetry was not"
        return self._telemetry

    @property
    def is_event_info(self) -> bool:
        return isinstance(self._telemetry, EventInfo)

    @property
    def as_event_info(self) -> EventInfo:
        assert self.is_event_info, "Requested EventInfo, but telemetry was not"
        return self._telemetry

    @property
    def is_structure(self) -> bool:
        return isinstance(self._telemetry, Structure)

    @property
    def as_structure(self) -> Structure:
        assert self.is_structure and self._telemetry is not INVALID_TELEMETRY_DATA, "Requested Structure, but telemetry was not"
        return self._telemetry

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

    def _constant_size(self) -> bool:
        if self.is_channel:
            return self.as_channel.type != "string"
        if self.is_event_info:
            return False

        for child in self.as_structure.children:
            if not child._constant_size():
                return False

        return True

    def _apply_properties(self) -> None:
        for field in fields(self._telemetry):
            setattr(self, field.name, getattr(self._telemetry, field.name))
        self.identifier = name(self)

    @staticmethod
    def unbuilt(telemetry: Channel | EventInfo | Structure) -> Telemetry:
        unbuilt: Telemetry = Telemetry(INVALID_TELEMETRY_ID, TelemetryType.Invalid, False, "")
        unbuilt._telemetry = telemetry
        return unbuilt

    @staticmethod
    def build(channels: list[Channel], events: list[Event]) -> list[Telemetry]:
        telemetries: list[Telemetry] = Telemetry._load_event_telemetries(events)
        general_structure: Telemetry = Telemetry.unbuilt(Structure("general", []))
        truck_structure: Telemetry = Telemetry.unbuilt(Structure("truck", []))
        trailer_structure: Telemetry = Telemetry.unbuilt(Structure("trailer", []))

        for channel_telemetry in Telemetry._load_channel_telemetries(channels):
            match ChannelCategory.of(channel_telemetry._telemetry):
                case ChannelCategory.General:
                    general_structure._telemetry.children.append(channel_telemetry)
                    channel_telemetry.apply_parent_structure(general_structure)
                case ChannelCategory.Truck:
                    truck_structure._telemetry.children.append(channel_telemetry)
                    channel_telemetry.apply_parent_structure(truck_structure)
                case ChannelCategory.Trailer:
                    trailer_structure._telemetry.children.append(channel_telemetry)
                    channel_telemetry.apply_parent_structure(trailer_structure)
                case _:
                    assert False, "'of' must always return a ChannelCategory"
            telemetries.append(channel_telemetry)

        channels_structure: Telemetry = Telemetry.unbuilt(
            Structure(
                "channels",
                [general_structure, truck_structure, trailer_structure],
            )
        )
        general_structure.apply_parent_structure(channels_structure)
        truck_structure.apply_parent_structure(channels_structure)
        trailer_structure.apply_parent_structure(channels_structure)
        telemetries.extend(
            (
                channels_structure,
                general_structure,
                truck_structure,
                trailer_structure,
            )
        )

        telemetries.sort(key=lambda t: t.rank)
        master: Telemetry = Telemetry.unbuilt(Structure("master", []))

        for telemetry in telemetries:
            if not telemetry.is_structure or telemetry._parent_structure:
                continue
            master.as_structure.children.append(telemetry)
            telemetry.apply_parent_structure(master)
        telemetries.insert(0, master)

        for i, telemetry in enumerate(telemetries):
            telemetry.id = i
            telemetry.constant_size = telemetry._constant_size()
            telemetry._apply_properties()
        return telemetries

    @staticmethod
    def _load_event_telemetries(events: list[Event]) -> list[Telemetry]:
        event_telemetries: list[Telemetry] = []
        for event in events:
            if event.macro not in TELEMETRY_EVENTS:
                continue
            event_telemetry: Telemetry = Telemetry.unbuilt(Structure(event, []))
            for event_info in event.event_infos:
                event_info.attributes.insert(
                    0, EventAttribute("", "latest", "latest", "u32", False)
                )
                event_telemetry.as_structure.children.append(Telemetry.unbuilt(event_info))
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
            channel_telemetries.append(Telemetry.unbuilt(channel))
        return channel_telemetries

    @staticmethod
    def dict_factory(telemetry: Telemetry) -> dict:
        as_dict: dict = {}
        names: list[str] = Telemetry.COMMON_FIELDS + (
            tuple() if telemetry.is_structure else tuple(field.name for field in fields(telemetry._telemetry))
        )

        for name in names:
            as_dict[name] = deepcopy(getattr(telemetry, name))

        if telemetry.is_structure:
            if telemetry.is_structure and telemetry.as_structure.is_event:
                as_dict["event"] = asdict(telemetry.as_structure.data)
                del as_dict["event"]["event_infos"]
            children = as_dict["children"] = []
            for child in telemetry.as_structure.children:
                children.append(Telemetry.dict_factory(child))
        elif telemetry.is_event_info:
            attributes: list[Telemetry] = as_dict["attributes"]
            for i in range(len(attributes)):
                attributes[i] = asdict(attributes[i])

        return as_dict

    def __iter__(self):
        return iter(Telemetry.dict_factory(self).items())


class TelemetryJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Telemetry):
            return Telemetry.dict_factory(obj)
        elif isinstance(obj, TelemetryType):
            return obj.name
        return super().default(obj)
# endregion


# region Important telemetry caching
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


# endregion


# region Types and Constants Generators
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
        f"{tabstr}constexpr const uint32_t& INVALID_OFFSET = static_cast<uint32_t>(-1);\n\n"
        f"{tabstr}constexpr const trailer_index_uint& INVALID_TRAILER_INDEX = static_cast<trailer_index_uint>(-1);\n\n"
        f"{tabstr}constexpr const uint32_t& INVALID_SIZE = 0;\n\n"
        f"{tabstr}constexpr const uint32_t& DEFAULT_MAX_COUNT = 0;\n\n"
        f"{tabstr}constexpr const {TELEMETRY_ID_ENUM_TYPE_NAME}& LIFETIME_INVALID_ID = {TELEMETRY_ID_ENUM_TYPE_NAME}::invalid;\n\n"
        f"{tabstr}constexpr const telemetry_type& LIFETIME_INVALID_TYPE = telemetry_type::invalid;\n\n"
        f"{tabstr}constexpr const char* const& LIFETIME_INVALID_CSTR = \"\";\n\n"
        f"{tabstr}constexpr const bool& LIFETIME_FALSE = false;\n\n"
    )

    out += (
        f"{tabstr}struct event_info_member {{\n"
        f"{tabstr}{TAB_CHARS}{TELEMETRY_ID_ENUM_TYPE_NAME} event_info_id;\n"
        f"{tabstr}{TAB_CHARS}const char* const macro_identifier;\n"
        f"{tabstr}{TAB_CHARS}const char* const macro;\n"
        f"{tabstr}{TAB_CHARS}uint32_t structure_offset;\n"
        f"{tabstr}{TAB_CHARS}scs_value_type_t scs_type_id;\n"
        f"{tabstr}{TAB_CHARS}bool indexed;\n\n"
        f"{tabstr}{TAB_CHARS}constexpr event_info_member(\n"
        f"{tabstr}{TAB_CHARS * 2}{TELEMETRY_ID_ENUM_TYPE_NAME} event_info_id = {TELEMETRY_ID_ENUM_TYPE_NAME}::invalid,\n"
        f"{tabstr}{TAB_CHARS * 2}const char* const macro_identifier = nullptr,\n"
        f"{tabstr}{TAB_CHARS * 2}const char* const macro = nullptr,\n"
        f"{tabstr}{TAB_CHARS * 2}uint32_t structure_offset = 0,\n"
        f"{tabstr}{TAB_CHARS * 2}scs_value_type_t scs_type_id = SCS_VALUE_TYPE_INVALID,\n"
        f"{tabstr}{TAB_CHARS * 2}bool indexed = false\n"
        f"{tabstr}{TAB_CHARS}) :\n"
        f"{tabstr}{TAB_CHARS * 2}event_info_id(event_info_id),\n"
        f"{tabstr}{TAB_CHARS * 2}macro_identifier(macro_identifier),\n"
        f"{tabstr}{TAB_CHARS * 2}macro(macro),\n"
        f"{tabstr}{TAB_CHARS * 2}structure_offset(structure_offset),\n"
        f"{tabstr}{TAB_CHARS * 2}scs_type_id(scs_type_id),\n"
        f"{tabstr}{TAB_CHARS * 2}indexed(indexed) {{}}\n"
        f"{tabstr}}};\n\n"
        f"{tabstr}constexpr const event_info_member INVALID_EVENT_INFO_MEMBER = event_info_member();\n\n"
        f"{tabstr}struct metadata_value {{\n"
        f"{tabstr}{TAB_CHARS}{TELEMETRY_ID_ENUM_TYPE_NAME} id;\n"
        f"{tabstr}{TAB_CHARS}const telemetry_type& telemetry_type;\n"
        f"{tabstr}{TAB_CHARS}const bool& constant_size;\n"
        f"{tabstr}{TAB_CHARS}const uint32_t& master_offset;\n"
        f"{tabstr}{TAB_CHARS}const uint32_t& structure_offset;\n"
        f"{tabstr}{TAB_CHARS}const uint32_t& storage_size;\n"
        f"{tabstr}{TAB_CHARS}const char* const& macro_identifier;\n"
        f"{tabstr}{TAB_CHARS}const char* const& macro;\n"
        f"{tabstr}{TAB_CHARS}const bool& indexed;\n"
        f"{tabstr}{TAB_CHARS}const uint32_t& max_count;\n"
        f"{tabstr}{TAB_CHARS}const bool& trailer_channel;\n"
        f"{tabstr}{TAB_CHARS}const scs_value_type_t& scs_type_id;\n"
        f"{tabstr}{TAB_CHARS}const bool& custom_channel;\n\n"
        f"{tabstr}{TAB_CHARS}constexpr metadata_value(\n"
        f"{tabstr}{TAB_CHARS * 2}const {TELEMETRY_ID_ENUM_TYPE_NAME}& id = LIFETIME_INVALID_ID,\n"
        f"{tabstr}{TAB_CHARS * 2}const {namespace}::telemetry_type& telemetry_type = LIFETIME_INVALID_TYPE,\n"
        f"{tabstr}{TAB_CHARS * 2}const bool& constant_size = LIFETIME_FALSE,\n"
        f"{tabstr}{TAB_CHARS * 2}const uint32_t& master_offset = INVALID_OFFSET,\n"
        f"{tabstr}{TAB_CHARS * 2}const uint32_t& structure_offset = INVALID_OFFSET,\n"
        f"{tabstr}{TAB_CHARS * 2}const uint32_t& storage_size = INVALID_SIZE,\n"
        f"{tabstr}{TAB_CHARS * 2}const char* const& macro_identifier = LIFETIME_INVALID_CSTR,\n"
        f"{tabstr}{TAB_CHARS * 2}const char* const& macro = LIFETIME_INVALID_CSTR,\n"
        f"{tabstr}{TAB_CHARS * 2}const bool& indexed = LIFETIME_FALSE,\n"
        f"{tabstr}{TAB_CHARS * 2}const uint32_t& max_count = DEFAULT_MAX_COUNT,\n"
        f"{tabstr}{TAB_CHARS * 2}const bool& trailer_channel = LIFETIME_FALSE,\n"
        f"{tabstr}{TAB_CHARS * 2}const scs_value_type_t& scs_type_id = SCS_VALUE_TYPE_INVALID,\n"
        f"{tabstr}{TAB_CHARS * 2}const bool& custom_channel = LIFETIME_FALSE\n"
        f"{tabstr}{TAB_CHARS}) :\n"
        f"{tabstr}{TAB_CHARS * 2}id(id),\n"
        f"{tabstr}{TAB_CHARS * 2}telemetry_type(telemetry_type),\n"
        f"{tabstr}{TAB_CHARS * 2}constant_size(constant_size),\n"
        f"{tabstr}{TAB_CHARS * 2}master_offset(master_offset),\n"
        f"{tabstr}{TAB_CHARS * 2}structure_offset(structure_offset),\n"
        f"{tabstr}{TAB_CHARS * 2}storage_size(storage_size),\n"
        f"{tabstr}{TAB_CHARS * 2}macro_identifier(macro_identifier),\n"
        f"{tabstr}{TAB_CHARS * 2}macro(macro),\n"
        f"{tabstr}{TAB_CHARS * 2}indexed(indexed),\n"
        f"{tabstr}{TAB_CHARS * 2}max_count(max_count),\n"
        f"{tabstr}{TAB_CHARS * 2}trailer_channel(trailer_channel),\n"
        f"{tabstr}{TAB_CHARS * 2}scs_type_id(scs_type_id),\n"
        f"{tabstr}{TAB_CHARS * 2}custom_channel(custom_channel) {{}}\n"
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
            f"{tabstr}{TAB_CHARS}static constexpr const {TELEMETRY_ID_ENUM_TYPE_NAME}& id = {telemetry.qualified_id};\n"
            f"{tabstr}{TAB_CHARS}static constexpr const telemetry_type& telemetry_type = {telemetry.telemetry_type.cpp_value()};\n"
            f"{tabstr}{TAB_CHARS}static constexpr const bool& constant_size = {cpp_bool(telemetry.constant_size)};\n"
        )

        if telemetry == master_telemetry():
            out += f"{tabstr}{TAB_CHARS}static constexpr const uint32_t& master_offset = 0;\n"
            out += f"{tabstr}{TAB_CHARS}static constexpr const uint32_t& structure_offset = 0;\n"
        else:
            parents: list[Telemetry | str] = telemetry.parents[:-1][::-1]
            dot_notation: str = ""
            if telemetry.is_channel and telemetry.as_channel.is_trailer_channel:
                parents.append(f"{STD_ARRAYS_ELEMS}[0]")

            for parent in parents:
                dot_notation += f"{name(parent)}."
            dot_notation += name(telemetry)

            out += f"{tabstr}{TAB_CHARS}static constexpr const uint32_t& master_offset = {offsetof(type_name(master_telemetry()), dot_notation)};\n"

        if telemetry.is_structure:
            out += (
                f"{tabstr}{TAB_CHARS}using storage_type = {qualify_type_name(telemetry)};\n"
                f'{tabstr}{TAB_CHARS}static constexpr const uint32_t& storage_type_size = sizeof(storage_type);\n'
            )
            if telemetry != master_telemetry():
                out += (
                    f"{tabstr}{TAB_CHARS}static constexpr const uint32_t& structure_offset = {offsetof(qualify_name(*[type_name(parent) for parent in telemetry.parents][::-1]), name(telemetry))};\n"
                        f"{tabstr}{TAB_CHARS}static constexpr const metadata_value& metadata_value = {namespace}::metadata_value(id, telemetry_type, constant_size, master_offset, structure_offset, storage_type_size);\n"
                )
            else:
                out += f"{tabstr}{TAB_CHARS}static constexpr const metadata_value& metadata_value = {namespace}::metadata_value(id, telemetry_type, constant_size, master_offset, structure_offset, storage_type_size);\n"
        elif telemetry.is_event_info:
            out += (
                f"{tabstr}{TAB_CHARS}using storage_type = {qualify_name(*[type_name(parent) for parent in ([] if telemetry == master_telemetry() else telemetry.parents[::-1])], type_name(telemetry))};\n"
                f'{tabstr}{TAB_CHARS}static constexpr const uint32_t& storage_type_size = sizeof(storage_type);\n'
                f'{tabstr}{TAB_CHARS}static constexpr const char* const& macro_identifier = "{telemetry.as_event_info.macro}";\n'
                f'{tabstr}{TAB_CHARS}static constexpr const char* const& macro = "{telemetry.as_event_info.expansion}";\n'
                f"{tabstr}{TAB_CHARS}static constexpr const uint32_t& structure_offset = {offsetof(qualify_type_name(telemetry.parent_structure), name(telemetry))};\n"
                    f"{tabstr}{TAB_CHARS}static constexpr const metadata_value& metadata_value = {namespace}::metadata_value(id, telemetry_type, constant_size, master_offset, structure_offset, storage_type_size, macro_identifier, macro);\n"
            )

            out += f"{tabstr}{TAB_CHARS}static constexpr const event_info_member members[] = {{\n"
            for i, attribute in enumerate(telemetry.as_event_info.attributes):
                out += f"{tabstr}{TAB_CHARS * 2}event_info_member({telemetry.qualified_id}, \"{attribute.macro}\", \"{attribute.expansion}\", offsetof(storage_type, {name(attribute)}), {TYPE_MACROS_BY_ID[attribute.scs_type_id]}, {cpp_bool(attribute.indexed)})"
                if i != len(telemetry.as_event_info.attributes) - 1:
                    out += ","
                out += "\n"
            out += f"{tabstr}{TAB_CHARS}}};\n"
            for i, attribute in enumerate(telemetry.as_event_info.attributes):
                out += f"{tabstr}{TAB_CHARS}static constexpr const event_info_member& {name(attribute)}_member_info = members[{i}];\n"
        elif telemetry.is_channel:
            out += (
                f"{tabstr}{TAB_CHARS}using storage_type = {type_name(telemetry)};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const uint32_t storage_type_size = sizeof(storage_type);\n"
                f'{tabstr}{TAB_CHARS}static constexpr const char* const& macro_identifier = "{telemetry.as_channel.macro}";\n'
                f'{tabstr}{TAB_CHARS}static constexpr const char* const& macro = "{telemetry.as_channel.expansion}";\n'
                f"{tabstr}{TAB_CHARS}static constexpr const bool& indexed = {cpp_bool(telemetry.as_channel.indexed)};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const uint32_t& max_count = {telemetry.as_channel.max_count};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const bool& trailer_channel = {cpp_bool(telemetry.as_channel.is_trailer_channel)};\n"
                f"{tabstr}{TAB_CHARS}using scs_type = {telemetry.as_channel.scs_type};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const scs_value_type_t& scs_type_id = {TYPE_MACROS_BY_ID[telemetry.as_channel.scs_type_id]};\n"
                f"{tabstr}{TAB_CHARS}using primitive_type = {telemetry.as_channel.primitive_type};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const uint32_t& structure_offset = {offsetof(qualify_type_name(telemetry.parent_structure), name(telemetry))};\n"
                f"{tabstr}{TAB_CHARS}static constexpr const bool& custom_channel = {cpp_bool(is_custom_channel(telemetry.as_channel))};\n"
                    f"{tabstr}{TAB_CHARS}static constexpr const metadata_value& metadata_value = {namespace}::metadata_value(id, telemetry_type, constant_size, master_offset, structure_offset, storage_type_size, macro_identifier, macro, indexed, max_count, trailer_channel, scs_type_id, custom_channel);\n"
            )

            if telemetry.as_channel.is_trailer_channel:
                out += f"{tabstr}{TAB_CHARS}static constexpr const uint32_t master_offset_of_trailer_index(const uint32_t& trailer_index) {{ return 0 <= trailer_index &&  trailer_index < SCS_TELEMETRY_trailers_count ? (master_offset + sizeof({qualify_type_name(telemetry.parent_structure)}) * trailer_index) : INVALID_OFFSET; }}\n"

        out += f"{tabstr}}};\n"
        if i != len(telemetries) - 1:
            out += "\n"

    tabstr = TAB_CHARS * tabcount
    out += f"{tabstr}}}"
    return out


# endregion


# region Function Generators
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
        f"{tabstr}constexpr const uint32_t master_offset_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const uint32_t& trailer_index = INVALID_TRAILER_INDEX) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        if telemetry.is_channel and telemetry.as_channel.is_trailer_channel:
            out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return 0 <= trailer_index && trailer_index < SCS_TELEMETRY_trailers_count ? {name(telemetry)}::master_offset + sizeof({qualify_type_name(telemetry.parent_structure)}) * trailer_index : INVALID_OFFSET;\n"
        elif telemetry in (configuration_trailer_structure_telemetry(), trailer_structure_telemetry()):
            out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return 0 <= trailer_index && trailer_index < SCS_TELEMETRY_trailers_count ? {name(telemetry)}::master_offset + sizeof({qualify_type_name(telemetry)}) * trailer_index : INVALID_OFFSET;\n"
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
        f"{tabstr}constexpr const uint32_t& structure_offset_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
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
        f"{tabstr}{TAB_CHARS * 2}default: return LIFETIME_FALSE;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def max_count_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const uint32_t& max_count(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
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
        f"{tabstr}{TAB_CHARS * 2}default: return LIFETIME_FALSE;\n"
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
        f"{tabstr}constexpr const {TELEMETRY_ID_ENUM_TYPE_NAME}& id_of(const char* const macro, const bool& is_event_info = false) {{\n"
        f"{tabstr}{TAB_CHARS}return\n"
    )

    for i, telemetry in enumerate(telemetries):
        if telemetry.is_channel and telemetry.as_channel.is_trailer_channel:
            cmp_expr: str = f'{TAB_CHARS}!is_event_info && streq(macro, "{name(telemetry)}") ||\n'
            for j in range(SCS_TELEMETRY_trailers_count):
                cmp_expr += (
                    f'{tabstr}{TAB_CHARS * 3}streq(macro, "{name(telemetry)}.{j}")'
                )
                if j != SCS_TELEMETRY_trailers_count - 1:
                    cmp_expr += " ||\n"
        else:
            cmp_expr: str = f'{'' if telemetry.is_event_info else '!' }is_event_info && streq(macro, "{name(telemetry)}")'
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
        f"{tabstr}constexpr const uint32_t size_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::storage_type_size;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_SIZE;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def offset_of_latest_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const uint32_t offset_of_latest(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
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
        f"{tabstr}constexpr const uint32_t event_info_member_offset_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const char* const member) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_event_info, telemetries)):
        out += (
            f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}:\n"
            f"{tabstr}{TAB_CHARS * 3}return\n"
        )
        for attribute in telemetry.as_event_info.attributes:
            out += f'{tabstr}{TAB_CHARS * 4}streq(member, "{attribute.expansion}") ? offsetof({name(telemetry)}::storage_type, {attribute.simple_name}) :\n'
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
            out += f'{tabstr}{TAB_CHARS * 4}streq(member, "{attribute.expansion}") ? {TYPE_MACROS_BY_ID[attribute.scs_type_id]} :\n'
        out += f"{tabstr}{TAB_CHARS * 4}SCS_VALUE_TYPE_INVALID;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return SCS_VALUE_TYPE_INVALID;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def event_info_member_indexed_function(
    telemetries: list[Telemetry], tabcount: int = 0
) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const bool event_info_member_indexed(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const char* const member) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_event_info, telemetries)):
        out += (
            f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}:\n"
            f"{tabstr}{TAB_CHARS * 3}return\n"
        )
        for attribute in telemetry.as_event_info.attributes:
            if attribute.indexed:
                out += f'{tabstr}{TAB_CHARS * 4}streq(member, "{attribute.expansion}") ? true :\n'
        out += f"{tabstr}{TAB_CHARS * 4}false;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return LIFETIME_FALSE;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )
    return out


def event_info_latest_offset(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const uint32_t event_info_latest_offset(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_event_info, telemetries)):
        out += (
           f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return offsetof({name(telemetry)}::storage_type, latest);\n"
        )

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_OFFSET;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )

    return out


def event_info_member_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const event_info_member& event_info_member_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const char* const member) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_event_info, telemetries)):
        out += (
            f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}:\n"
            f"{tabstr}{TAB_CHARS * 3}return\n"
        )
        for attribute in telemetry.as_event_info.attributes:
            out += f'{tabstr}{TAB_CHARS * 4}streq(member, "{attribute.expansion}") ? {name(telemetry)}::{name(attribute)}_member_info :\n'
        out += f"{tabstr}{TAB_CHARS * 4}INVALID_EVENT_INFO_MEMBER;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_EVENT_INFO_MEMBER;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )

    return out


def is_custom_channel_function(telemetries: list[Telemetry], tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}constexpr const bool& is_custom_channel(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(filter(lambda t: t.is_channel, telemetries)):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {name(telemetry)}::custom_channel;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return LIFETIME_FALSE;\n"
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


def indicize_trailer_telemetry_expansion(telemetry: Telemetry, index: int) -> str:
    assert 0 <= index < SCS_TELEMETRY_trailers_count, "index out of range"
    assert telemetry.is_channel or telemetry.is_event_info, (
        "trailer is only a channel or event info"
    )
    return telemetry._telemetry.expansion.replace("trailer", f"trailer.{index}")


def registration_for(
    telemetry: Telemetry,
    channel_callback: str,
    indexed_channel_callback: str,
    trailer_channel_callback: str,
    indexed_trailer_callback: str,
    event_callack: str,
    metadata_namespace: str = "metadata",
    tabcount: int = 1,
) -> str:
    assert (telemetry.is_channel and not is_custom_channel(telemetry.as_channel)) or (
        telemetry.is_structure and telemetry.as_structure.is_event
    ), "Can only register for channels and events"
    tabstr: str = TAB_CHARS * tabcount
    out: str = ""

    if telemetry.is_channel:
        if telemetry.as_channel.is_trailer_channel:
            if telemetry.as_channel.indexed:
                out += f"{tabstr}for (uint32_t i = 0; i < {metadata_namespace}::{name(telemetry)}::max_count; i++) {{\n"
                for i in range(SCS_TELEMETRY_trailers_count):
                    out += f'{tabstr}{TAB_CHARS}register_for_channel("{indicize_trailer_telemetry_expansion(telemetry, i)}", i, {TYPE_MACROS_BY_ID[telemetry.as_channel.scs_type_id]}, SCS_TELEMETRY_CHANNEL_FLAG_none, {indexed_trailer_callback}<{metadata_namespace}::{name(telemetry)}, {i}>, nullptr);\n'
                out += f"{tabstr}}}\n"
            else:
                for i in range(SCS_TELEMETRY_trailers_count):
                    out += f'{tabstr}register_for_channel("{indicize_trailer_telemetry_expansion(telemetry, i)}", SCS_U32_NIL, {TYPE_MACROS_BY_ID[telemetry.as_channel.scs_type_id]}, SCS_TELEMETRY_CHANNEL_FLAG_none, {trailer_channel_callback}<{metadata_namespace}::{name(telemetry)}, {i}>, nullptr);\n'
        elif telemetry.as_channel.indexed:
            out += (
                f"{tabstr}for (uint32_t i = 0; i < {metadata_namespace}::{name(telemetry)}::max_count; i++) {{\n"
                f"{tabstr}{TAB_CHARS}register_for_channel({telemetry.as_channel.macro}, i, {TYPE_MACROS_BY_ID[telemetry.as_channel.scs_type_id]}, SCS_TELEMETRY_CHANNEL_FLAG_none, {indexed_channel_callback}<{metadata_namespace}::{name(telemetry)}>, nullptr);\n"
                f"{tabstr}}}\n"
            )
        else:
            out = f"{tabstr}register_for_channel({telemetry.as_channel.macro}, SCS_U32_NIL, {TYPE_MACROS_BY_ID[telemetry.as_channel.scs_type_id]}, SCS_TELEMETRY_CHANNEL_FLAG_none, {channel_callback}<{metadata_namespace}::{name(telemetry)}>, nullptr);\n"
    else:
        out = f"{tabstr}register_for_event({telemetry.as_structure.data.macro}, {event_callack}<{metadata_namespace}::{name(telemetry)}>, nullptr);\n"

    return out


def register_all_function(
    telemetries: list[Telemetry],
    channel_callback: str,
    indexed_channel_callback: str,
    trailer_channel_callback: str,
    indexed_trailer_callback: str,
    event_callback: str,
    metadata_namespace: str = "metadata",
    tabcount: int = 0,
) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = f"{tabstr}void register_all(scs_telemetry_register_for_channel_t register_for_channel, scs_telemetry_register_for_event_t register_for_event) {{\n"
    registerables: list[Telemetry] = list(
        filter(
            lambda t: (t.is_channel and not is_custom_channel(t.as_channel))
            or (t.is_structure and t.as_structure.is_event),
            telemetries,
        )
    )
    for telemetry in registerables:
        out += registration_for(
            telemetry,
            channel_callback,
            indexed_channel_callback,
            trailer_channel_callback,
            indexed_trailer_callback,
            event_callback,
            metadata_namespace,
            tabcount + 1,
        )
    out += f"{tabstr}}}\n"
    return out


def append_bytes_function(
    structure_telemetry: Telemetry,
    metadata_namespace: str = "metadata",
    tabcount: int = 0,
) -> str:
    assert not isinstance(structure_telemetry, list), (
        "wrong function, did you mean the plural one?"
    )
    assert structure_telemetry.is_structure or structure_telemetry.is_event_info, (
        "Must be a structure or event info"
    )
    tabstr: str = TAB_CHARS * tabcount
    qualified_type_name: str = qualify_type_name(structure_telemetry)
    out: str = (
        f"{tabstr}void append_bytes(const {qualified_type_name}& {name(structure_telemetry)}, std::vector<uint8_t>& out) {{\n"
        f"{tabstr}{TAB_CHARS}constexpr const uint32_t& packed_size = {qualify_name(metadata_namespace, 'packed_size_of')}({structure_telemetry.qualified_id});\n"
        f"{tabstr}{TAB_CHARS}if (out.capacity() - out.size() < packed_size) {{\n"
        f"{tabstr}{TAB_CHARS * 2}out.reserve(packed_size);\n"
        f"{tabstr}{TAB_CHARS}}}\n"
    )

    tabstr = TAB_CHARS * (tabcount + 1)
    if structure_telemetry.constant_size:
        out += f"{tabstr}//reserve the packed size of the structure.\n"
    for child in (
        structure_telemetry.as_structure.children
        if structure_telemetry.is_structure
        else structure_telemetry.as_event_info.attributes
    ):
        path: str = f"{name(structure_telemetry)}.{name(child)}"
        out += f"{tabstr}append_bytes({path}, out);\n"

    out += f"{TAB_CHARS * tabcount}}}\n"
    return out


def from_bytes_function(
    structure_telemetry: Telemetry,
    metadata_namespace: str = "metadata",
    tabcount: int = 0,
) -> tuple[tuple[str], str]:
    assert not isinstance(structure_telemetry, list), (
        "wrong function, did you mean the plural one?"
    )
    assert structure_telemetry.is_structure or structure_telemetry.is_event_info, (
        "Must be a structure or event info"
    )
    tabstr: str = TAB_CHARS * tabcount
    qualified_type_name: str = qualify_type_name(structure_telemetry)
    declarations: list[str] = [
        f"{tabstr}bool from_bytes(const std::vector<uint8_t>& as_bytes, {qualified_type_name}& {name(structure_telemetry)}, const uint32_t offset, uint32_t& read)",
        f"{tabstr}static bool from_bytes(const std::vector<uint8_t>& as_bytes, {qualified_type_name}& {name(structure_telemetry)}) {{ uint32_t read; return from_bytes(as_bytes, {name(structure_telemetry)}, 0, read); }}",
    ]
    out: str = f"{declarations[0]} {{\n"
    declarations[0] += ";"

    tabstr = TAB_CHARS * (tabcount + 1)
    out += (
        f"{tabstr}constexpr const uint32_t& packed_size = {metadata_namespace}::packed_size_of({structure_telemetry.qualified_id});\n"
        f"{tabstr}if (as_bytes.size() - offset < {metadata_namespace}::packed_size_of({structure_telemetry.qualified_id})) return false;\n"
        f"{tabstr}read = 0;\n"
        f"{tabstr}uint32_t single_read = 0;\n"
    )

    for child in (
        structure_telemetry.as_structure.children
        if structure_telemetry.is_structure
        else structure_telemetry.as_event_info.attributes
    ):
        path: str = f"{name(structure_telemetry)}.{name(child)}"
        if (
            child == trailer_structure_telemetry()
            or child == configuration_trailer_structure_telemetry()
        ):
            out += (
                f"{tabstr}for (trailer_index_uint i = 0; i < SCS_TELEMETRY_trailers_count; i++){{\n"
                f"{tabstr}{TAB_CHARS}if (!from_bytes(as_bytes, {path}[i], offset + read, single_read)) return false;\n"
                f"{tabstr}{TAB_CHARS}read += single_read;\n"
                f"{tabstr}}}\n"
            )
        else:
            out += (
                f"{tabstr}if (!from_bytes(as_bytes, {path}, offset + read, single_read)) return false;\n"
                f"{tabstr}read += single_read;\n"
            )

    out += f"{tabstr}return true;\n{TAB_CHARS * tabcount}}}\n"
    return tuple(declarations), out


def append_bytes_functions(
    telemetries: list[Telemetry],
    metadata_namespace: str = "metadata",
    tabcount: int = 0,
) -> tuple[str, str]:
    implout: str = ""
    dependency_sorted: list[Telemetry] = list(
        filter(lambda t: t.is_structure or t.is_event_info, telemetries[::-1])
    )
    dependency_sorted.sort(key=lambda t: 3 if t == master_telemetry() else -t.rank)
    declarations: list[str] = []
    for structure in dependency_sorted:
        function: str = (
            f"{append_bytes_function(structure, metadata_namespace, tabcount)}\n"
        )
        declarations.append(f"{function[: function.index(')') + 1]};")
        implout += function

    tabstr: str = TAB_CHARS * tabcount
    declarations.append(f"bool append_bytes(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const void* const data, std::vector<uint8_t>& out);")
    implout += (
        f"{tabstr}bool append_bytes(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const void* const data, std::vector<uint8_t>& out) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        implout += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: append_bytes(*reinterpret_cast<const {metadata_namespace}::{name(telemetry)}::storage_type* const>(data), out); return true;\n"

    implout += (
        f"{tabstr}{TAB_CHARS * 2}default: return false;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )

    declout: str = ""
    for i, declaration in enumerate(declarations):
        declout += f"{declaration}\n"
        if i != len(declarations) - 1:
            declout += "\n"
    return declout, implout


def from_bytes_functions(
    telemetries: list[Telemetry],
    metadata_namespace: str = "metadata",
    tabcount: int = 0,
) -> tuple[str.str]:
    implout: str = ""
    dependency_sorted: list[Telemetry] = list(
        filter(lambda t: t.is_structure or t.is_event_info, telemetries[::-1])
    )
    dependency_sorted.sort(key=lambda t: 3 if t == master_telemetry() else -t.rank)
    declarations: list[str] = []
    for structure in dependency_sorted:
        telemetry_declarations, implementation = from_bytes_function(
            structure, metadata_namespace, tabcount
        )
        declarations.extend(telemetry_declarations)
        implout += f"{implementation}\n"

    tabstr: str = TAB_CHARS * tabcount
    declarations.append(f"bool from_bytes(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const std::vector<uint8_t>& as_bytes, void* const out, const uint32_t& offset, uint32_t& read);")
    implout += (
        f"{tabstr}bool from_bytes(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id, const std::vector<uint8_t>&as_bytes, void* const out,  const uint32_t& offset,uint32_t& read) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        implout += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return from_bytes(as_bytes, *reinterpret_cast<{metadata_namespace}::{name(telemetry)}::storage_type* const>(out), offset, read);\n"

    implout += (
        f"{tabstr}{TAB_CHARS * 2}default: read = 0; return false;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )

    declout: str = ""
    for i, declaration in enumerate(declarations):
        declout += f"{declaration}\n"
        if i != len(declarations) - 1:
            declout += "\n"

    return declout, implout


def packed_size_of_constant(
    telemetry: Telemetry, metadata_namespace: str = "metadata", tabcout: int = 0
) -> str:
    assert telemetry.is_structure or telemetry.is_event_info, (
        "Only structures and event info require this function"
    )
    tabstr: str = TAB_CHARS * tabcout
    out: str = f"{tabstr}constexpr const uint32_t packed_size_of_{name(telemetry)} = \n"
    tabstr: str = TAB_CHARS * (tabcout + 1)
    if telemetry.is_structure:
        for i, child in enumerate(telemetry.as_structure.children):
            if child.is_channel:
                out += f"{tabstr}{metadata_namespace}::{name(child)}::storage_type::serialization_info::packed_size"
            else:
                out += f"{tabstr}packed_size_of_{name(child)}"
            if i == len(telemetry.as_structure.children) - 1:
                out += ";\n"
            else:
                out += " +\n"
    else:
        for i, attribute in enumerate(telemetry.as_event_info.attributes):
            out += f"{tabstr}{storage(attribute)[0]}::serialization_info::packed_size"
            if i == len(telemetry.as_event_info.attributes) - 1:
                out += ";\n"
            else:
                out += " +\n"

    return out


def packed_size_of_function(
    telemetries: list[Telemetry],
    metadata_namespace: str = "metadata",
    tabcount: int = 0,
) -> str:
    out: str = ""
    dependency_sorted: list[Telemetry] = list(
        filter(lambda t: t.is_structure or t.is_event_info, telemetries[::-1])
    )
    dependency_sorted.sort(key=lambda t: 3 if t == master_telemetry() else -t.rank)
    for telemetry in dependency_sorted:
        out += f"{packed_size_of_constant(telemetry, metadata_namespace, tabcount)}\n"

    tabstr: str = TAB_CHARS * tabcount
    out += (
        f"{tabstr}constexpr const uint32_t& packed_size_of(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        if telemetry.is_channel:
            out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {metadata_namespace}::{name(telemetry)}::storage_type::serialization_info::packed_size;\n"
        else:
            out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return packed_size_of_{name(telemetry)};\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return INVALID_OFFSET;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )

    return out


def is_constant_size_function(
    telemetries: list[Telemetry],
    metadata_namespace: str = "metadata",
    tabcount: int = 0,
) -> str:
    out: str = ""
    dependency_sorted: list[Telemetry] = list(
        filter(lambda t: t.is_structure or t.is_event_info, telemetries[::-1])
    )
    dependency_sorted.sort(key=lambda t: 3 if t == master_telemetry() else -t.rank)
    for telemetry in dependency_sorted:
        out += f"{packed_size_of_constant(telemetry, metadata_namespace, tabcount)}\n"

    tabstr: str = TAB_CHARS * tabcount
    out += (
        f"{tabstr}constexpr const bool& is_constant_size(const {TELEMETRY_ID_ENUM_TYPE_NAME}& id) {{\n"
        f"{tabstr}{TAB_CHARS}switch (id) {{\n"
    )

    for i, telemetry in enumerate(telemetries):
        out += f"{tabstr}{TAB_CHARS * 2}case {telemetry.qualified_id}: return {metadata_namespace}::{name(telemetry)}::constant_size;\n"

    out += (
        f"{tabstr}{TAB_CHARS * 2}default: return LIFETIME_FALSE;\n"
        f"{tabstr}{TAB_CHARS}}}\n"
        f"{tabstr}}}\n"
    )

    return out


def storage_type_of_template(
    telemetries: list[Telemetry],
    metadata_namespace: str = "metadata",
    tabcount: int = 0
) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}template <telemetry_id id>\nstruct storage_type_of;\n\n"
    )

    for telemetry in telemetries:
        out += (
            f"template<>\n"
            f"struct storage_type_of<{telemetry.qualified_id}> : {qualify_name(metadata_namespace, name(telemetry), "storage_type")} {{}};\n\n"
        )

    return out


def memory_usage_function(tabcount: int = 0) -> str:
    tabstr: str = TAB_CHARS * tabcount
    out: str = (
        f"{tabstr}const uint32_t memory_usage(const {type_name(master_telemetry())}& master) {{\n"
        f"{tabstr}{TAB_CHARS}uint32_t usage = 0;\n"
    )

    def recurse(telemetry: Telemetry, parent_names: list[str]) -> None:
        nonlocal out
        if telemetry.constant_size:
            out += f"{tabstr}{TAB_CHARS}usage += sizeof({type_name(telemetry)});\n"
            return
        dotted_parents: str = "".join(f"{name}." for name in parent_names)
        if telemetry.is_event_info:
            for attribute in telemetry.as_event_info.attributes:
                if telemetry == configuration_trailer_structure_telemetry():
                    continue
                dotted = f"{dotted_parents}{name(attribute)}"
                out += f"{tabstr}{TAB_CHARS}usage += sizeof({type_name(attribute)});\n"
                if attribute.indexed:
                    if attribute.type == "string":
                        out += (
                            f"{tabstr}{TAB_CHARS}for (uint32_t i = 0; i < {dotted}.values.size(); i++) {{\n"
                            f"{tabstr}{TAB_CHARS * 2}usage += static_cast<uint32_t>({dotted}.values[i].size() + 1);\n"
                            f"{tabstr}{TAB_CHARS}}}\n"
                        )
                    else:
                        out += f"{tabstr}{TAB_CHARS}usage += static_cast<uint32_t>({dotted}.values.size() * sizeof({attribute.primitive_type}));\n"
                elif attribute.type == "string":
                    out += f"{tabstr}{TAB_CHARS}usage += static_cast<uint32_t>({dotted}.value.size() + 1);\n"
        else:
            for child in telemetry.as_structure.children:
                dotted = f"{dotted_parents}{name(child)}"
                if child.constant_size:
                    out += f"{tabstr}{TAB_CHARS}usage += sizeof({qualify_type_name(child)});\n"
                else:
                    recurse(child, parent_names + [name(child)])
                    out += "\n"

    recurse(master_telemetry(), ["master"])
    out += (
        f"{tabstr}{TAB_CHARS}return usage;\n"
        f"{tabstr}}}\n"
    )
    return out


# endregion


def flatten_master(master_telemetry: Telemetry) -> list[Telemetry]:
    flattened: list[Telemetry] = []
    def recurse(telemetry: Telemetry) -> list[Telemetry]:
        flattened.append(telemetry)
        if telemetry.is_structure:
            for child in telemetry.as_structure.children:
                recurse(child)

    recurse(master_telemetry)
    flattened.sort(key=lambda t: t.id)
    return flattened


def prepare_distributable(master_telemetry: Telemetry) -> dict:
    def recurse(telemetry: Telemetry) -> dict:
        telemetry_data: dict = {
            "id": telemetry.id,
            "telemetry_type": telemetry.telemetry_type.name,
            "identifier": name(telemetry),
            "constant_size": telemetry.constant_size,
        }

        if telemetry.is_structure:
            if telemetry.as_structure.is_event:
                telemetry_data["event"] = asdict(telemetry.as_structure.data)
                del telemetry_data["event"]["event_infos"]
            telemetry_data["children"] = [recurse(child) for child in telemetry.as_structure.children]
        elif telemetry.is_event_info:
            telemetry_data["attributes"] = [asdict(attribute) for attribute in telemetry.as_event_info.attributes]
        elif telemetry.is_channel:
            telemetry_data.update(asdict(telemetry.as_channel))
            telemetry_data["custom_channel"] = is_custom_channel(telemetry)
        return telemetry_data

    return {
        "version": "0.1.0",
        "telemetries": recurse(master_telemetry),
    }


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
        f.write(f"{event_info_member_indexed_function(telemetries)}\n")
        f.write(f"{event_info_latest_offset(telemetries)}\n")
        f.write(f"{event_info_member_function(telemetries)}\n")
        f.write(f"{is_custom_channel_function(telemetries)}\n")
        f.write(f"{metadata_value_of_function(telemetries)}\n")
        f.write(f"{is_constant_size_function(telemetries)}\n")
    with open(
        OUTPUT_FOLDER.joinpath("storage_type_of.h"), "w", encoding="utf-8"
    ) as f:
        f.write(storage_type_of_template(telemetries))
    with open(OUTPUT_FOLDER.joinpath("register_all.cpp"), "w", encoding="utf-8") as f:
        f.write(
            register_all_function(
                telemetries, "store", "store", "store", "store", "handle_event"
            )
        )
    with open(OUTPUT_FOLDER.joinpath("memory_usage.cpp"), "w", encoding="utf-8") as f:
        f.write(memory_usage_function())
    with open(
        OUTPUT_FOLDER.joinpath("packed_size_of_constants.h"), "w", encoding="utf-8"
    ) as f:
        f.write(packed_size_of_function(telemetries))
    append_bytes_functions_decl, append_bytes_functions_impl = append_bytes_functions(
        telemetries
    )
    from_bytes_functions_decl, from_bytes_functions_impl = from_bytes_functions(
        telemetries
    )
    with open(OUTPUT_FOLDER.joinpath("byte_converters.h"), "w", encoding="utf-8") as f:
        f.write(f"{append_bytes_functions_decl}\n")
        f.write(f"{from_bytes_functions_decl}\n")
    with open(
        OUTPUT_FOLDER.joinpath("byte_converters.cpp"), "w", encoding="utf-8"
    ) as f:
        f.write(f"{append_bytes_functions_impl}\n")
        f.write(f"{from_bytes_functions_impl}\n")
    with open(OUTPUT_FOLDER.joinpath("truckconnect_telemetry.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(prepare_distributable(master_telemetry()), indent = 4))
    with open(OUTPUT_FOLDER.joinpath("asdict_telemetry.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(master_telemetry(), indent=4, cls=TelemetryJSONEncoder))

if __name__ == "__main__":
    if retval := main():
        print(retval)

