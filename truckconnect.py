from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from scssdk_dataclasses import Channel, Event, EventInfo, EventAttribute, load, TYPE_SIZE_BY_ID


TELEMETRY_EVENTS: str = [
    "SCS_TELEMETRY_EVENT_configuration",
    "SCS_TELEMETRY_EVENT_gameplay",
]
INVALID_TELEMETRY_ID: int = -1

VALUE_STORAGE_TYPE_NAME: str = "value_storage"
VALUE_STORAGE_EXTRA_SIZE: int = 1
VALUE_ARRAY_STORAGE_TYPE_NAME: str = "value_array_storage"
VALUE_ARRAY_STORAGE_EXTRA_SIZE: int = 1 + 4
VALUE_VECTOR_STORAGE_TYPE_NAME: str = "value_vector_storage"
VALUE_VECTOR_STORAGE_EXTRA_SIZE: int = 1

def scs_type_id_storage_size(scs_type_id: int) -> int:
    return TYPE_SIZE_BY_ID[scs_type_id] + VALUE_STORAGE_EXTRA_SIZE


def channel_storage(channel: Channel) -> tuple[str, int]:
    return f"{VALUE_ARRAY_STORAGE_TYPE_NAME if channel.indexed else VALUE_STORAGE_TYPE_NAME}<{channel.primitive_type}>", scs_type_id_storage_size(channel.scs_type_id) * channel.max_count


def attribute_storage(attribute: EventAttribute) -> str:
    return f"{VALUE_VECTOR_STORAGE_TYPE_NAME if attribute.indexed else VALUE_STORAGE_TYPE_NAME}<{attribute.primitive_type}>"


def storage(telemetry_or_attr: Telemetry | EventAttribute) -> tuple[str, int]:
    if telemetry_or_attr.is_channel:
        return channel_storage(telemetry_or_attr.as_channel)
    elif isinstance(telemetry_or_attr, EventAttribute):
        return attribute_storage(telemetry_or_attr), None

    assert False, "Can only get storage of a channel or event attribute"


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
        ) or channel.macro.startswith("SCS_TELEMETRY_JOB_CHANNEL"):
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
            channel_telemetries.append(Telemetry(channel))
        return channel_telemetries


def main() -> None:
    telemetries: list[Telemetry] = Telemetry.build(*load())
    print(f"Loaded {len(telemetries)} telemetries.")


if __name__ == "__main__":
    if retval := main():
        print(retval)
