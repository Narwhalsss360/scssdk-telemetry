from __future__ import annotations
from enum import Enum
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
    id_of_type
)
import json

# region Constants
TRUCKCONNECT_TELEMETRY_FILE: str = "truckconnect_telemetry.json"
TELEMETRY_EVENTS: str = [
    "SCS_TELEMETRY_EVENT_configuration",
    "SCS_TELEMETRY_EVENT_gameplay",
]
EXCLUDE_CHANNELS: dict[str, str] = {  # macro and reason
    "SCS_TELEMETRY_TRUCK_CHANNEL_adblue_average_consumption": "prism::sdk does not find this channel."
}
INVALID_TELEMETRY_ID: int = -1
# endregion


# region Basic Utility
def is_attribute(telemetry_or_attr: Telemetry | EventAttribute) -> bool:
    return isinstance(telemetry_or_attr, EventAttribute)


def as_custom_channel(channel: Channel) -> Channel:
    setattr(channel, "_is_custom", None)
    return channel


def is_custom_channel(channel: Channel | Telemetry) -> bool:
    if isinstance(channel, Telemetry):
        return channel.custom_channel
    return hasattr(channel, "_is_custom")


def name(telemetry_or_attr_str: Telemetry | EventAttribute | str) -> str:
    if is_attribute(telemetry_or_attr_str):
        return telemetry_or_attr_str.simple_name
    if isinstance(telemetry_or_attr_str, str):
        return telemetry_or_attr_str
    return telemetry_or_attr_str.name


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
    def from_name(name: str) -> TelemetryType:
        for type_name in TelemetryType:
            if type_name.name == name:
                return type_name
        raise ValueError(f"{name} not found.")

    @staticmethod
    def cpp(tabcount: int = 0, tab_chars: str = "\t") -> str:
        tabstr: str = tab_chars * tabcount
        out: str = f"{tabstr}enum class telemetry_type : uint8_t {{\n"
        for i, enum in enumerate(TelemetryType):
            out += f"{tabstr}{tab_chars}{enum.value}"
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
    COMMON_FIELDS = ("id", "telemetry_type", "constant_size", "identifier")
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
    custom_channel: bool = field(default=False)

    def __post_init__(self) -> None:
        self._telemetry: Channel | EventInfo | Structure | None = INVALID_TELEMETRY_DATA
        self._parent_structure: Telemetry | None = None
        assert (
            self.telemetry_type != TelemetryType.Invalid
            or self.is_structure
            or self.is_event_info
            or self.is_channel
        ), "telemetry must be either structure, event info or channel"
        if isinstance(self.telemetry_type, str):
            self.telemetry_type = TelemetryType.from_name(self.telemetry_type)

        if self.attributes or []:
            for i in range(len(self.attributes)):
                self.attributes[i] = EventAttribute(**self.attributes[i])
        if self.children or []:
            for i in range(len(self.children)):
                self.children[i] = Telemetry(**self.children[i])
        if self.event:
            self.event = Event(**self.event, event_infos=[])

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
        return self.telemetry_type == TelemetryType.Channel or isinstance(
            self._telemetry, Channel
        )

    @property
    def as_channel(self) -> Channel:
        assert self.is_channel, "Requested Channel, but telemetry was not"
        if self._telemetry is not None:
            return self._telemetry
        return self

    @property
    def is_event_info(self) -> bool:
        return self.telemetry_type == TelemetryType.EventInfo or isinstance(
            self._telemetry, EventInfo
        )

    @property
    def as_event_info(self) -> EventInfo:
        assert self.is_event_info, "Requested EventInfo, but telemetry was not"
        if self._telemetry is not None:
            return self._telemetry
        return self

    @property
    def is_structure(self) -> bool:
        return self.telemetry_type == TelemetryType.Structure or (
            isinstance(self._telemetry, Structure)
            and self._telemetry is not INVALID_TELEMETRY_DATA
        )

    @property
    def as_structure(self) -> Structure:
        assert self.is_structure, "Requested Structure, but telemetry was not"
        if self._telemetry is not INVALID_TELEMETRY_DATA:
            return self._telemetry
        return self

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
    def scs_type_id(self) -> int:
        assert self.is_channel, "The 'scs_type_id' is only available for channels"
        return id_of_type(self.as_channel.type)

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
        assert self._telemetry is not None

        for field in fields(self._telemetry):
            setattr(self, field.name, getattr(self._telemetry, field.name))
        self.identifier = name(self)
        if self.telemetry_type == TelemetryType.Invalid:
            if self.is_structure:
                self.telemetry_type = TelemetryType.Structure
            elif self.is_event_info:
                self.telemetry_type = TelemetryType.EventInfo
            else:
                self.telemetry_type = TelemetryType.Channel
        if self.is_channel:
            self.custom_channel = is_custom_channel(self.as_channel)

    @staticmethod
    def unbuilt(telemetry: Channel | EventInfo | Structure) -> Telemetry:
        unbuilt: Telemetry = Telemetry(
            INVALID_TELEMETRY_DATA, TelemetryType.Channel, False, ""
        )
        unbuilt.telemetry_type = TelemetryType.Invalid
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
                event_telemetry.as_structure.children.append(
                    Telemetry.unbuilt(event_info)
                )
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
            tuple()
            if telemetry.is_structure
            else tuple(field.name for field in fields(telemetry._telemetry))
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
            telemetry_data["children"] = [
                recurse(child) for child in telemetry.as_structure.children
            ]
        elif telemetry.is_event_info:
            telemetry_data["attributes"] = [
                asdict(attribute) for attribute in telemetry.as_event_info.attributes
            ]
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


def build_telemetries() -> list[Telemetry]:
    channels, events = load()
    channels.insert(0, as_custom_channel(PAUSED_CUSTOM_CHANNEL))
    return cache_telemetries(Telemetry.build(channels, events))


def main() -> None:
    telemetries: list[Telemetry] = build_telemetries()
    print(f"Built {len(telemetries)} telemetries.")
    with open(TRUCKCONNECT_TELEMETRY_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(prepare_distributable(master_telemetry()), indent=4, cls=TelemetryJSONEncoder))


if __name__ == "__main__":
    if retval := main():
        print(retval)
