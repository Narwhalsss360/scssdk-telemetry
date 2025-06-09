from __future__ import annotations
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from scssdk_dataclasses import Channel, Event, EventInfo, EventAttribute, load, TYPE_SIZE_BY_ID

OUTPUT_FOLDER: Path = Path("generated.gitignore/")
TAB_CHARS: str = '\t'

TELEMETRY_EVENTS: str = [
    "SCS_TELEMETRY_EVENT_configuration",
    "SCS_TELEMETRY_EVENT_gameplay",
]
EXCLUDE_CHANNELS: dict[str, str] = { # macro and reason
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

    return f"{cpp_type}<{template_args}>", scs_type_id_storage_size(channel.scs_type_id) * channel.max_count


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


def qualify_name(*args) -> str:
    qualified: str = ""
    for i, name in enumerate(args):
        qualified += name
        if i != len(args) - 1:
            qualified += "::"
    return qualified


def type_name(telemetry_or_attr: Telemetry | EventAttribute) -> str:
    if is_attribute(telemetry_or_attr):
        return attribute_storage(telemetry_or_attr)
    if telemetry_or_attr.is_structure:
        return telemetry_or_attr.as_structure.type_name
    if telemetry_or_attr.is_event_info:
        return f"{telemetry_or_attr.as_event_info.simple_name}_storage"
    if telemetry_or_attr.is_channel:
        return channel_storage(telemetry_or_attr.as_channel)


def name(telemetry_or_attr: Telemetry | EventAttribute) -> str:
    if is_attribute(telemetry_or_attr):
        return telemetry_or_attr.simple_name
    return telemetry_or_attr.name


class ChannelCategory(Enum):
    General = (0,)
    Truck = (1,)
    Trailer = 2

    @staticmethod
    def of(channel: Channel) -> ChannelCategory:
        if channel.macro.startswith("SCS_TELEMETRY_TRUCK_CHANNEL"):
            return ChannelCategory.Truck
        if channel.macro.startswith("SCS_TELEMETRY_TRAILER_CHANNEL"):
            return ChannelCategory.Trailer
        elif channel.macro.startswith(
            "SCS_TELEMETRY_CHANNEL"
        ) or channel.macro.startswith("SCS_TELEMETRY_JOB_CHANNEL")or is_custom_channel(channel):
            return ChannelCategory.General
        assert False, "A channel was not supplied"


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
                case ChannelCategory.Truck:
                    truck_structure.telemetry.children.append(channel_telemetry)
                case ChannelCategory.Trailer:
                    trailer_structure.telemetry.children.append(channel_telemetry)
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

        telemetries.insert(
            0,
            Telemetry(
                Structure("master", list(filter(lambda t: t.is_structure, telemetries)))
            ),
        )

        for i, telemetry in enumerate(telemetries):
            telemetry.id = i
        return telemetries

    @staticmethod
    def _load_event_telemetries(events: list[Event]) -> list[Telemetry]:
        event_telemetries: list[Telemetry] = []
        for event in events:
            if event.macro not in TELEMETRY_EVENTS:
                continue
            event_telemetries.append(
                Telemetry(
                    Structure(
                        event,
                        [Telemetry(event_info) for event_info in event.event_infos],
                    )
                )
            )
            event_telemetries.extend(event_telemetries[-1].telemetry.children)
        return event_telemetries

    @staticmethod
    def _load_channel_telemetries(channels: list[Channel]) -> list[Telemetry]:
        channel_telemetries: list[Telemetry] = []
        for channel in channels:
            if channel.macro in EXCLUDE_CHANNELS:
                print(f"Excluding {channel.macro}. Reason: {EXCLUDE_CHANNELS[channel.macro]}")
                continue
            channel_telemetries.append(Telemetry(channel))
        return channel_telemetries


def master_structure(master: Telemetry) -> str:
    def recurse(tabcount: str, telemetry: Telemetry | EventAttribute):
        tabstr: str = TAB_CHARS * tabcount
        if isinstance(telemetry, EventAttribute):
            out = f"{tabstr}{storage(telemetry)[0]} {name(telemetry)};\n"
        elif telemetry.is_structure:
            out = f"{tabstr}struct {type_name(telemetry)} {{"
            if telemetry.as_structure.children:
                out += "\n"

            for child in telemetry.as_structure.children:
                out += recurse(tabcount + 1, child)

            out += f"{tabstr}}}"
            if name(telemetry) != "master":
                out += f" {name(telemetry)}"
            out += ";\n"
        elif telemetry.is_event_info:
            out = f"{tabstr}struct {type_name(telemetry)} {{"
            if telemetry.as_event_info.attributes:
                out += "\n"

            for child in telemetry.as_event_info.attributes:
                out += recurse(tabcount + 1, child)

            out += f"{tabstr}}} {name(telemetry)};\n"
        else:
            out = f"{tabstr}{storage(telemetry)[0]} {name(telemetry)};\n"

        return out

    return recurse(0, master)


PAUSED_CUSTOM_CHANNEL: Channel = Channel(
    "channel_paused",
    "",
    "bool",
    False,
    "channel_paused",
    False,
    1
)


def main() -> None:
    channels, events = load()
    channels.insert(0, as_custom_channel(PAUSED_CUSTOM_CHANNEL))

    telemetries: list[Telemetry] = Telemetry.build(channels, events)
    print(f"Loaded {len(telemetries)} telemetries.")

    if not OUTPUT_FOLDER.exists():
        OUTPUT_FOLDER.mkdir()
    with open(OUTPUT_FOLDER.joinpath("master_structure.h"), "w", encoding="utf-8") as f:
        f.write(master_structure(telemetries[0]))


if __name__ == "__main__":
    if retval := main():
        print(retval)
